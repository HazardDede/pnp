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

from ..app import Application
from ..config import load_config
from ..models import Task, tasks_to_str

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
    cfg = load_config(validated['<configuration>'])

    tasks = {
        task.name: Task.from_dict(task) for task in cfg
    }

    logging.info("Configured tasks\n{}".format(tasks_to_str(tasks)))

    app = Application()
    app.run(tasks)


def main():
    arguments = docopt(__doc__, version='0.7.2')
    run(arguments)


if __name__ == '__main__':
    main()
