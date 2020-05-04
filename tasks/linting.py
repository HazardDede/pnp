from invoke import task

from tasks.config import (
    CONFIGS_PATH,
    DOCS_PATH,
    SCRIPTS_PATH,
    SOURCE_PATH
)


@task
def flake8(ctx):
    """Runs flake8 linter against codebase."""
    ctx.run("flake8 "
            "--max-line-length 120 "
            "--ignore=E704,E722,E731,W503 "
            "{}".format(SOURCE_PATH))


@task
def pylint(ctx):
    """Runs pylint linter against codebase."""
    ctx.run("pylint {}".format(SOURCE_PATH))


@task
def mypy(ctx):
    """Runs the mypy typing linter against the codebase."""
    _includes = [
        "{}/logging.py".format(SOURCE_PATH),
        "{}/models.py".format(SOURCE_PATH),
        "{}/selector.py".format(SOURCE_PATH),
        "{}/utils.py".format(SOURCE_PATH),
        "{}/validator.py".format(SOURCE_PATH),
        "{}/engines/*.py".format(SOURCE_PATH),
        "{}/plugins/__init__.py".format(SOURCE_PATH),
        "{}/plugins/pull/__init__.py".format(SOURCE_PATH),
        "{}/plugins/push/__init__.py".format(SOURCE_PATH),
        "{}/plugins/udf/__init__.py".format(SOURCE_PATH)
    ]
    ctx.run("mypy {}".format(' '.join(_includes)))


@task
def configs(ctx):
    """Validates configuration files in configs and docs."""
    ctx.run("yamllint -c .yamllint {configs} {docs}".format(configs=CONFIGS_PATH, docs=DOCS_PATH))
    ctx.run("python {}/test_configs.py".format(SCRIPTS_PATH), pty=True)


@task(flake8, pylint, mypy, configs, default=True)
def lint(ctx):
    """Run all configured linters against the codebase."""