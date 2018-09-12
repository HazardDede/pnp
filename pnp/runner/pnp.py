"""Pull 'n' Push

Usage:
  pnp [(-c | --check)] <configuration>
  pnp (-h | --help)
  pnp (-v | --version)

Options:
  -c --check        Only check configuration and do not run it.
  -h --help         Show this screen.
  -v --version      Show version.

"""

import logging
import os

from docopt import docopt
from schema import Schema, Use, And

from ..app import Application

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=LOG_LEVEL)


def validate_args(args):
    validator = Schema({
        "--help": Use(bool),
        "--version": Use(str),
        "--check": Use(bool),
        "<configuration>": And(os.path.isfile, Use(os.path.abspath))
    })
    return validator.validate(args)


def run(args):
    validated = validate_args(args)
    app = Application.from_file(validated['<configuration>'])
    if not validated['--check']:
        app.start()


def main():
    arguments = docopt(__doc__, version='0.10.0')
    run(arguments)


if __name__ == '__main__':
    main()
