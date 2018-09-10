"""Pull 'n' Push

Usage:
  pnp <configuration>
  pnp (-h | --help)
  pnp (-v | --version)

Options:
  -h --help         Show this screen.
  -v --version      Show version.

"""

import logging
import os

from docopt import docopt
from schema import Schema, Use, And

from ..engines.thread_engine import ThreadEngine
from ..app import Application

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=LOG_LEVEL)


def validate_args(args):
    validator = Schema({
        "--help": Use(bool),
        "--version": Use(str),
        "<configuration>": And(os.path.isfile, Use(os.path.abspath))
    })
    return validator.validate(args)


def run(args):
    validated = validate_args(args)

    # TODO: Make engine configurable via configuration
    # TODO: Make number of queue_worker configurable by configuration
    app = Application.from_file(validated['<configuration>'])
    app.bind(engine=ThreadEngine())
    app.start()


def main():
    arguments = docopt(__doc__, version='0.9.0')
    run(arguments)


if __name__ == '__main__':
    main()
