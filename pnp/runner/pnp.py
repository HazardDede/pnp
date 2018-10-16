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

from ..utils import get_first_existing_file
from ..app import Application


def setup_logging(*candidates, default_level=logging.INFO, env_key='PNP_LOG_CONF'):
    """Setup logging configuration"""
    log_file_path = get_first_existing_file(*candidates)
    env_path = os.getenv(env_key, None)
    if env_path:
        log_file_path = env_path
    if os.path.exists(log_file_path):
        with open(log_file_path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
        logging.info("Logging loaded from: {}".format(log_file_path))
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
    validated = validate_args(args)
    pnp_cfg_path = validated['<configuration>']
    default_log_level = os.environ.get('LOG_LEVEL', 'DEBUG')
    setup_logging(args['--log'], 'logging.yaml', os.path.join(os.path.dirname(pnp_cfg_path), 'logging.yaml'),
                  default_level=default_log_level)
    app = Application.from_file(pnp_cfg_path)
    if not validated['--check']:
        app.start()


def main():
    arguments = docopt(__doc__, version='0.11.1')
    run(arguments)


if __name__ == '__main__':
    main()
