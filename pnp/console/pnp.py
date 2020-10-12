"""Pull 'n' Push main entrypoint."""

import logging
import logging.config
import os

import click
import coloredlogs
from ruamel import yaml
from sty import fg, bg, ef, rs

from pnp import __version__
from pnp.app import Application
from pnp.logo import PNP
from pnp.utils import get_first_existing_file


# Default log file name
DEFAULT_LOGGING_FILE_NAME = 'logging.yaml'

# Double space
DSPACE = " " * 2


def _setup_logging(*candidates, log_level_override=None, env_key='PNP_LOG_CONF'):
    """Setup logging configuration"""
    log_file_path = get_first_existing_file(*candidates)
    env_path = os.getenv(env_key, None)
    if env_path:
        log_file_path = env_path
    if log_file_path and os.path.exists(log_file_path):
        log_file_path = os.path.abspath(log_file_path)
        with open(log_file_path, 'rt') as fhandle:
            config = yaml.safe_load(fhandle.read())
        logging.config.dictConfig(config)
        logging_conf = log_file_path
    else:
        if not log_level_override:
            log_level_override = "INFO"
        logging_conf = "Basic logging"

    coloredlogs.install(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
        level=log_level_override or logging.getLogger().level
    )
    return logging_conf


def _print_api_config(config):
    def helper():
        if not config.api:
            return f'{fg.yellow}No API configured{fg.rs}'
        return f'{fg.green}{config.api}{fg.rs}'

    print(f"{ef.bold}API{rs.all}\n{DSPACE}{helper()}")


def _print_udf_config(config):
    print_str = f"{ef.bold}UDFs{rs.all}\n"
    if not config.udfs:
        print_str += f"{DSPACE}{fg.yellow}No UDFs configured{fg.rs}"
    else:
        all_udfs = [f"{DSPACE}- {fg.green}{str(udf)}{fg.rs}" for udf in config.udfs]
        print_str += "\n".join(all_udfs)
    print(print_str)


def _print_engine_config(config):
    engine_str = f"{fg.green}{str(config.engine)}{fg.rs}"
    print(f"{ef.bold}Engine{rs.all}\n{DSPACE}{engine_str}")


def _stringify_single_push(push, level):
    res = f"{DSPACE * level}- {fg.green}{push.instance}{fg.rs}"
    level += 1
    if push.selector:
        res += f"\n{DSPACE * level}{ef.bold}Selector{rs.all}: {push.selector}"
    if push.deps:
        res += "\n" + _stringify_push_config(push.deps, level, "Dependencies")
    return res


def _stringify_push_config(pushes, level=2, label="Push"):
    res = f"{DSPACE * level}{ef.bold}{label}{rs.all}\n"
    all_pushes = [_stringify_single_push(push, level + 1) for push in pushes]
    res += "\n".join(all_pushes)
    return res


def _print_tasks_config(config):
    print_str = f"{ef.bold}Tasks{rs.all}\n"
    all_tasks = []
    for task in config.tasks.values():
        task_str = ""
        task_str += f"{DSPACE}- {ef.bold}{task.name}{rs.all}\n"
        task_str += f"{DSPACE * 2}{ef.bold}Pull{rs.all}\n"
        task_str += f"{DSPACE * 3}{fg.green}{task.pull.instance}{fg.rs}\n"
        task_str += _stringify_push_config(task.pushes)
        all_tasks.append(task_str)
    print_str += "\n".join(all_tasks)
    print(print_str)


@click.command('pnp')
@click.argument(
    'configfile',
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    required=True,
)
@click.option(
    '-c', '--check',
    is_flag=True,
    help="Only check the given config file but does not run it."
)
@click.option(
    '--no-log-probe',
    is_flag=True,
    help="Disables the automatic logging configuration probing."
)
@click.option(
    '--log',
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help="Specify logging configuration to load."
)
@click.option(
    '--log-level',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'], case_sensitive=False),
    default=None,
    help="Overrides the log level."
)
@click.version_option(version=__version__)
def main(configfile, check, log, log_level, no_log_probe):
    """Pull 'n' Push. Runs or checks the given CONFIGFILE"""
    print(f"{ef.bold}Welcome to {fg.green}pnp{fg.rs} @ {fg.green}{__version__}{rs.all}")
    print(f"{fg.green}{bg.black}{PNP}{bg.rs}{fg.rs}")

    app = Application.from_file(configfile)
    config = app.config

    _print_api_config(config)
    _print_engine_config(config)
    _print_udf_config(config)
    _print_tasks_config(config)

    if not check:
        log_level_override = log_level or os.environ.get('LOG_LEVEL')
        probing_log_conf = [log]
        if not no_log_probe:
            probing_log_conf += [
                # logging.yaml in cwd
                DEFAULT_LOGGING_FILE_NAME,
                # logging.yaml in pnp config loc
                os.path.join(os.path.dirname(configfile), DEFAULT_LOGGING_FILE_NAME)
            ]
        logging_config_path = _setup_logging(
            *probing_log_conf,
            log_level_override=log_level_override
        )
        print(f"{ef.bold}Logging{rs.all}\n{DSPACE}{fg.green}{logging_config_path}{fg.rs}")

        app.start()


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
