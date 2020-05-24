"""Pull 'n' Push

Usage:
  pnp [(-v | --verbose)] [--log=<log_conf>] <configuration>
  pnp (-c | --check) <configuration>
  pnp (-h | --help)
  pnp --version

Options:
  -c --check        Only check configuration and do not run it.
  -v --verbose      Switches log level to debug.
  --log=<log_conf>  Specify logging configuration to load.
  -h --help         Show this screen.
  --version         Show version.
"""

import logging
import logging.config
import os

from docopt import docopt
from ruamel import yaml
from schema import Schema, Use, And, Or

from pnp import __version__
from pnp.app import Application
from pnp.utils import get_first_existing_file


def _setup_logging(*candidates, default_level=logging.INFO, env_key='PNP_LOG_CONF', verbose=False):
    """Setup logging configuration"""
    log_file_path = get_first_existing_file(*candidates)
    env_path = os.getenv(env_key, None)
    if env_path:
        log_file_path = env_path
    if log_file_path and os.path.exists(log_file_path):
        with open(log_file_path, 'rt') as fhandle:
            config = yaml.safe_load(fhandle.read())
        logging.config.dictConfig(config)
        logging.info("Logging loaded from: %s", log_file_path)
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.DEBUG if verbose else default_level)
        logging.info("Logging loaded with basic configuration")


def _validate_args(args):
    validator = Schema({
        "--help": Use(bool),
        "--verbose": Use(bool),
        "--version": Use(str),
        "--check": Use(bool),
        "--log": Or(None, And(os.path.isfile, Use(os.path.abspath))),
        "<configuration>": And(os.path.isfile, Use(os.path.abspath))
    })
    return validator.validate(args)


def run(args):
    """Run pull 'n' push."""
    validated = _validate_args(args)
    pnp_cfg_path = validated['<configuration>']
    default_log_level = os.environ.get('LOG_LEVEL', 'INFO')
    _setup_logging(
        args['--log'], 'logging.yaml', os.path.join(os.path.dirname(pnp_cfg_path), 'logging.yaml'),
        default_level=default_log_level, verbose=validated['--verbose']
    )
    app = Application.from_file(pnp_cfg_path)
    if not validated['--check']:
        app.start()


def main():
    """Main entry point into pnp application."""
    arguments = docopt(__doc__, version=__version__)
    run(arguments)


if __name__ == '__main__':
    import sys
    sys.exit(main())
