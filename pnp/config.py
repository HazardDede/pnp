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
        >>> data = dict(inbound='value')
        >>> schema.validate(data)
        {'override': 'value'}

    """
    def __init__(self, *args, **kwargs):
        if len(args) < 2:
            raise ValueError("OrMap expects the mapping value at first and then multiple validation directives")
        self.override = args[0]
        super().__init__(*args[1:], **kwargs)

    def validate(self, data):
        super().validate(data)
        return self.override


plugin_schema = {
    "plugin": Use(str),
    Optional("selector", default=None): Or(str, None),
    Optional("args", default={}): {
        Optional(str): object
    }
}


plugin_list = [plugin_schema]

tasks = [{
    "name": Use(str),
    OrOverride("pull", "inbound", "pull"): plugin_schema,
    OrOverride("pushes", "outbound", "push"): And(Or(plugin_schema, plugin_list), Use(make_list))
}]

tasks_settings = {
    Optional(Or("anchors", "anchor", "ref", "refs", "alias", "aliases")): object,
    'tasks': tasks
}

root = And(Or(
    tasks_settings,  # Tasks with additional settings and aliases (yaml only)
    tasks,  # Tasks without settings or aliases - just a list of tasks (backward compatibility)
),
    # In case of list only we create a tasks node - so we know it's always there
    Use(lambda x: x if 'tasks' in x else dict(tasks=x))
)

schema = Schema(root)


def load_config(config_path):
    """Load the specified config"""
    with open(config_path, 'r') as fp:
        cfg = yaml.safe_load(fp)
    return Box(schema.validate(cfg)).tasks
