import json

from attrdict import AttrDict
from schema import Schema, Use, Optional, Or


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
    Optional("args", default={}): {
        Optional(str): object
    }
}


schema = Schema([{
    "name": Use(str),
    OrOverride("inbound", "inbound", "pull"): plugin_schema,
    OrOverride("outbound", "outbound", "push"): plugin_schema
}])


def load_config(config_path):
    """Load the specified config"""
    with open(config_path, 'r') as fp:
        cfg = json.load(fp)
    return AttrDict({'base': schema.validate(cfg)}).base
