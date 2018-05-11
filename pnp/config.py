import json

from attrdict import AttrDict
from schema import Schema, Use, Optional

plugin_schema = {
    "plugin": Use(str),
    Optional("args", default={}): {
        Optional(str): object
    }
}


schema = Schema([{
    "name": Use(str),
    "inbound": plugin_schema,
    "outbound": plugin_schema
}])


def load_config(config_path):
    with open(config_path, 'r') as fp:
        cfg = json.load(fp)
    return AttrDict({'base': schema.validate(cfg)}).base
