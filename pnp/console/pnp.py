"""Pull 'n' Push main entrypoint."""

import logging
import logging.config
import os

import click
from ruamel import yaml

from pnp import __version__
from pnp.app import Application
from pnp.utils import get_first_existing_file

CONFIG_FILE_TYPE = click.Path(exists=True, dir_okay=False, resolve_path=True)
LOG_FILE_TYPE = click.Path(exists=True, dir_okay=False, resolve_path=True)
LOG_LEVEL_CHOICES = ['DEBUG', 'INFO', 'WARNING', 'ERROR']


def _setup_logging(*candidates, log_level_override=None, env_key='PNP_LOG_CONF'):
    """Setup logging configuration"""
    log_file_path = get_first_existing_file(*candidates)
    env_path = os.getenv(env_key, None)
    if env_path:
        log_file_path = env_path
    if log_file_path and os.path.exists(log_file_path):
        with open(log_file_path, 'rt') as fhandle:
            config = yaml.safe_load(fhandle.read())
        logging.config.dictConfig(config)
        if log_level_override:
            logging.getLogger().setLevel(log_level_override)
        logging.info("Logging loaded from: %s", log_file_path)
    else:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=log_level_override or logging.INFO)
        logging.info("Logging loaded with basic configuration")


@click.command('pnp')
@click.argument(
    'configfile',
    type=CONFIG_FILE_TYPE,
    required=True,
)
@click.option(
    '-c', '--check',
    is_flag=True,
    help="Only check the given config file and do not run it."
)
@click.option(
    '--log',
    type=LOG_FILE_TYPE,
    help="Specify logging configuration to load."
)
@click.option(
    '--log-level',
    type=click.Choice(LOG_LEVEL_CHOICES, case_sensitive=False),
    default=None,
    help="Overrides the log level."
)
@click.version_option(version=__version__)
def main(configfile, check, log, log_level):
    """Pull 'n' Push. Runs or checks the given CONFIGFILE"""
    log_level_override = log_level or os.environ.get('LOG_LEVEL')
    _setup_logging(
        log, 'logging.yaml', os.path.join(os.path.dirname(configfile), 'logging.yaml'),
        log_level_override=log_level_override
    )
    app = Application.from_file(configfile)
    if not check:
        app.start()


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
