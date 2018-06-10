from ruamel import yaml

from box import Box
from schema import Schema, Use, Optional, Or, And

from .utils import make_list


class OrOverride(Or):
    """
    Validates the given data as the original Or validation directive would do, but overrides the resulting
    data.

    Example:
        >>> # Whether inbound or outbound are valid keys, but will be overridden by override
        >>> schema = Schema({OrOverride('override', 'inbound', 'outbound'): Use(str)})
        >>> schema.validate({'inbound': 'value'})  # inbound will be mapped to override
        {'override': 'value'}
        >>> schema.validate({'outbound': 'value'})  # outbound will be mapped to override
        {'override': 'value'}
        >>> OrOverride('override')  # Only override without valid directives is bad...
        Traceback (most recent call last):
        ...
        ValueError: OrMap expects the mapping value at first and then multiple validation directives

    """
    def __init__(self, *args, **kwargs):
        if len(args) < 2:
            raise ValueError("OrMap expects the mapping value at first and then multiple validation directives")
        self.override = args[0]
        super().__init__(*args[1:], **kwargs)

    def validate(self, data):
        super().validate(data)
        return self.override


push_schema = Schema({
    "plugin": Use(str),
    Optional("selector", default=None): Or(str, None),
    Optional("args", default={}): {
        Optional(str): object
    },
    # deps is a list of push_schemas as well, but cannot declare recursive schemas
    Optional("deps", default=list()): And(object, Use(make_list))
})

pull_schema = Schema({
    "plugin": Use(str),
    Optional("args", default={}): {
        Optional(str): object
    },
})

push_list_schema = Schema([push_schema])

tasks_schema = Schema([{
    "name": Use(str),
    OrOverride("pull", "inbound", "pull"): pull_schema,
    OrOverride("pushes", "outbound", "push"): And(Or(push_list_schema, push_schema), Use(make_list))
}])

tasks_settings_schema = Schema({
    Optional(Or("anchors", "anchor", "ref", "refs", "alias", "aliases")): object,
    'tasks': tasks_schema
})

root_schema = Schema(And(Or(
    tasks_settings_schema,  # Tasks with additional settings and aliases (yaml only)
    tasks_schema,  # Tasks without settings or aliases - just a list of tasks (backward compatibility)
),
    # In case of list only we create a tasks node - so we know it's always there
    Use(lambda x: x if 'tasks' in x else dict(tasks=x))
))

schema = Schema(root_schema)


def validate_push_deps(push):
    # Recursively validate pushes
    for dependency in push['deps']:
        validated_push = push_schema.validate(dependency)
        validated_push['deps'] = list(validate_push_deps(validated_push))
        yield validated_push


def load_config(config_path):
    """Load the specified config"""
    with open(config_path, 'r') as fp:
        cfg = yaml.safe_load(fp)
    validated = schema.validate(cfg)
    for pull in validated['tasks']:
        for push in pull['pushes']:
            push['deps'] = list(validate_push_deps(push))
    return Box(validated).tasks
