"""Configuration handling in json/yaml files."""

import os
from functools import partial

from ruamel import yaml  # type: ignore
from schema import Schema, Use, Optional, Or, And  # type: ignore
from box import Box  # type: ignore

from .engines import Engine, RetryHandler
from .plugins import load_plugin
from .utils import make_list


class OrOverride(Or):
    """
    Validates the given data as the original Or validation directive would do,
    but overrides the resulting data.

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
            raise ValueError("OrMap expects the mapping value at first and then "
                             "multiple validation directives")
        self.override = args[0]
        super().__init__(*args[1:], **kwargs)

    def validate(self, data):
        super().validate(data)
        return self.override


PUSH = Schema({
    "plugin": Use(str),
    Optional("selector", default=None): Or(object, None),
    Optional("unwrap", default=False): bool,
    Optional("args", default={}): {
        Optional(str): object
    },
    # deps is a list of push_schemas as well, but cannot declare recursive schemas
    Optional("deps", default=list()): And(object, Use(make_list))
})

PULL = Schema({
    "plugin": Use(str),
    Optional("args", default={}): {
        Optional(str): object
    },
})

PUSH_LIST = Schema([PUSH])

TASK = Schema({
    "name": Use(str),
    OrOverride("pull", "inbound", "pull"): PULL,
    OrOverride("pushes", "outbound", "push"): And(Or(PUSH_LIST, PUSH), Use(make_list))
})

# Allow configuration of a single task or a list of tasks
TASK_LIST = Schema(
    Or(
        And(TASK, Use(make_list)),
        [TASK]
    )
)

ENGINE = Engine

UDFS = Schema([{
    "name": Use(str),
    "plugin": Use(str),
    Optional("args"): Or({
        str: object
    }, None)
}])

TASK_SETTINGS = Schema({
    Optional(Or("anchors", "anchor", "ref", "refs", "alias", "aliases")): object,
    Optional("engine", default=None): ENGINE,
    Optional("udfs", default=None): UDFS,
    'tasks': TASK_LIST
})

ROOT = Schema(And(
    Or(
        # Tasks with additional settings and aliases (yaml only)
        TASK_SETTINGS,
        # Tasks without settings or aliases - just a list of tasks (backwards compatibility)
        TASK_LIST,
    ),
    # In case of list only we create a tasks node - so we know it's always there
    Use(lambda x: x if 'tasks' in x else dict(tasks=x))
))


def validate_push_deps(push):
    """Validates a push against the schema. This is done recursively."""
    for dependency in push['deps']:
        validated_push = PUSH.validate(dependency)
        validated_push['deps'] = list(validate_push_deps(validated_push))
        yield validated_push


def custom_constructor(loader, node, clstype):
    """YAML custom constructor. Necessary to create an engine and retry handler."""
    args = loader.construct_mapping(node, deep=True)
    if 'type' not in args:
        raise ValueError("You have to specify a 'type' when instantiating a engine with !engine")
    clazz_name = args.pop('type')
    return load_plugin(clazz_name, clstype, **args)


def make_mentor(config_path):
    """Creates an instance of the dictmentor with configured plugins."""
    from dictmentor import DictMentor, ext  # type: ignore
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

    validated = ROOT.validate(mentor.augment(cfg)['cfg'])
    for pull in validated['tasks']:
        for push in pull['pushes']:
            push['deps'] = list(validate_push_deps(push))
    b = Box(validated)

    return (
        b.udfs if 'udfs' in b else None,
        b.engine if 'engine' in b else None,
        b.tasks
    )
