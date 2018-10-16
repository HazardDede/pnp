import os
from functools import partial
from ruamel import yaml

from box import Box
from schema import Schema, Use, Optional, Or, And

from .engines import Engine, RetryHandler
from .plugins import load_plugin
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

task_entity_schema = Schema({
    "name": Use(str),
    OrOverride("pull", "inbound", "pull"): pull_schema,
    OrOverride("pushes", "outbound", "push"): And(Or(push_list_schema, push_schema), Use(make_list))
})

task_list_schema = Schema([task_entity_schema])

# Allow confguration of a single task
tasks = Schema(Or(And(task_entity_schema, Use(make_list)), task_list_schema))  # Single or multiple tasks are allowed

engine_schema = Engine

tasks_settings_schema = Schema({
    Optional(Or("anchors", "anchor", "ref", "refs", "alias", "aliases")): object,
    Optional("engine", default=None): engine_schema,
    'tasks': tasks
})

root_schema = Schema(And(
    Or(
        tasks_settings_schema,  # Tasks with additional settings and aliases (yaml only)
        tasks,  # Tasks without settings or aliases - just a list of tasks (backward compatibility)
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


def custom_constructor(loader, node, clstype):
    args = loader.construct_mapping(node, deep=True)
    if 'type' not in args:
        raise ValueError("You have to specify a 'type' when instantiating a engine with !engine")
    clazz_name = args.pop('type')
    return load_plugin(clazz_name, clstype, **args)


def make_mentor(config_path):
    from dictmentor import DictMentor, ext
    return DictMentor(
        ext.Environment(fail_on_unset=True),
        ext.ExternalResource(base_path=os.path.dirname(config_path)),
        ext.ExternalYamlResource(base_path=os.path.dirname(config_path))
    )


def load_config(config_path):
    """Load the specified config"""
    yaml.SafeLoader.add_constructor(u"!engine", partial(custom_constructor, clstype=Engine))
    yaml.SafeLoader.add_constructor(u"!retry", partial(custom_constructor, clstype=RetryHandler))

    with open(config_path, 'r') as fp:
        cfg = yaml.safe_load(fp)
        # pnp configuration is probably of list of tasks. dictmentor needs a dict ...
        # ... let's fake it ;-)
        cfg = dict(cfg=cfg)

    mentor = make_mentor(config_path)
    # Remove the faked dictionary as root level

    validated = schema.validate(mentor.augment(cfg)['cfg'])
    for pull in validated['tasks']:
        for push in pull['pushes']:
            push['deps'] = list(validate_push_deps(push))
    b = Box(validated)
    return b.engine if 'engine' in b else None, b.tasks
