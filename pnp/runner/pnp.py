"""Pull 'n' Push

Usage:
  pnp [(--engine=<engine>)] [(-v | --verbose)] [--log=<log_conf>] <configuration>
  pnp (-c | --check) <configuration>
  pnp (-h | --help)
  pnp --version

Options:
  -c --check        Only check configuration and do not run it.
  --engine=<engine> Override engine from configuration file (thread, process, sequential, async).
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

from ..app import Application
from ..engines import DEFAULT_ENGINES
from ..utils import get_first_existing_file


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
    possible_engines = list(DEFAULT_ENGINES.keys())
    engine_schema = Or(
        None,
        And(Use(str), lambda n: n in possible_engines,
            error='Not a valid engine. Use one of {}'.format(list(possible_engines)))
    )

    validator = Schema({
        "--help": Use(bool),
        "--verbose": Use(bool),
        "--version": Use(str),
        "--check": Use(bool),
        "--engine": engine_schema,
        "--log": Or(None, And(os.path.isfile, Use(os.path.abspath))),
        "<configuration>": And(os.path.isfile, Use(os.path.abspath))
    })
    return validator.validate(args)


def run(args):
    """Run pull 'n' push."""
    validated = _validate_args(args)
    pnp_cfg_path = validated['<configuration>']
    default_log_level = os.environ.get('LOG_LEVEL', 'DEBUG')
    _setup_logging(
        args['--log'], 'logging.yaml', os.path.join(os.path.dirname(pnp_cfg_path), 'logging.yaml'),
        default_level=default_log_level, verbose=validated['--verbose']
    )
    app = Application.from_file(pnp_cfg_path, engine_override=validated['--engine'])
    if not validated['--check']:
        app.start()


def main():
    """Main entry point into pnp application."""
    arguments = docopt(__doc__, version='0.20.2')
    run(arguments)


if __name__ == '__main__':
    main()
