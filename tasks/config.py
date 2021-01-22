import os

from invoke import task

# VERSION
VERSION = "0.27.0"


# PATH STUFF
PROJECT_ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DOCS_PATH = os.path.join(PROJECT_ROOT_PATH, 'docs')
SCRIPTS_PATH = os.path.join(PROJECT_ROOT_PATH, 'scripts')
SOURCE_PATH = os.path.join(PROJECT_ROOT_PATH, 'pnp')
TASKS_PATH = os.path.join(PROJECT_ROOT_PATH, 'tasks')
TEST_PATH = os.path.join(PROJECT_ROOT_PATH, 'tests')


@task(default=True)
def config(ctx):
    """Shows the general configuration."""
    for k, v in globals().items():
        if k.endswith("_PATH"):
            print(k.ljust(20), v)
