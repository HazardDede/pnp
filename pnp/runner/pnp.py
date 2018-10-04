"""Pull 'n' Push

Usage:
  pnp [(-c | --check)] [--log=<log_conf>] <configuration>
  pnp (-h | --help)
  pnp (-v | --version)

Options:
  -c --check        Only check configuration and do not run it.
  --log=<log_conf>  Specify logging configuration to load.
  -h --help         Show this screen.
  -v --version      Show version.

"""

import logging
import logging.config
import os

from docopt import docopt
from schema import Schema, Use, And, Or
from ruamel import yaml

from ..app import Application


def setup_logging(default_path, default_level=logging.INFO, env_key='PNP_LOG_CONF'):
    """Setup logging configuration"""
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
        logging.info("Logging loaded from: {}".format(path))
    else:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=default_level)
        logging.info("Logging loaded with basic configuration")


def validate_args(args):
    validator = Schema({
        "--help": Use(bool),
        "--version": Use(str),
        "--check": Use(bool),
        "--log": Or(None, And(os.path.isfile, Use(os.path.abspath))),
        "<configuration>": And(os.path.isfile, Use(os.path.abspath))
    })
    return validator.validate(args)


def run(args):
    default_log_level = os.environ.get('LOG_LEVEL', 'DEBUG')
    setup_logging(default_path=(args['--log'] or 'logging.yaml'), default_level=default_log_level)
    validated = validate_args(args)
    app = Application.from_file(validated['<configuration>'])
    if not validated['--check']:
        app.start()


def main():
    arguments = docopt(__doc__, version='0.10.0')
    run(arguments)


if __name__ == '__main__':
    main()
