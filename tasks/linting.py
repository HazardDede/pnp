from invoke import task

from tasks.config import (
    CONFIGS_PATH,
    DOCS_PATH,
    SCRIPTS_PATH,
    SOURCE_PATH,
)


@task
def flake8(ctx):
    """Runs flake8 linter against codebase."""
    ctx.run("flake8 "
            "--max-line-length 120 "
            "--ignore=E704,E722,E731,W503 "
            f"{SOURCE_PATH}")


@task
def pylint(ctx):
    """Runs pylint linter against codebase."""
    ctx.run(f"pylint {SOURCE_PATH}")


@task
def mypy(ctx):
    """Runs the mypy typing linter against the codebase."""
    _includes = [
        f"{SOURCE_PATH}/logging.py",
        f"{SOURCE_PATH}/models.py",
        f"{SOURCE_PATH}/selector.py",
        f"{SOURCE_PATH}/utils.py",
        f"{SOURCE_PATH}/validator.py",
        f"{SOURCE_PATH}/engines/*.py",
        f"{SOURCE_PATH}/plugins/__init__.py",
        f"{SOURCE_PATH}/plugins/pull/__init__.py",
        f"{SOURCE_PATH}/plugins/push/__init__.py",
        f"{SOURCE_PATH}/plugins/udf/__init__.py"
    ]
    ctx.run(f"mypy {' '.join(_includes)}")


@task
def configs(ctx):
    """Validates configuration files in configs and docs."""
    ctx.run(f"yamllint -c .yamllint {CONFIGS_PATH} {DOCS_PATH}")
    ctx.run(f"python {SCRIPTS_PATH}/test_configs.py", pty=True)


@task(flake8, pylint, mypy, configs, default=True)
def lint(ctx):
    """Run all configured linters against the codebase."""
