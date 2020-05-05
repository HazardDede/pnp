from invoke import task

from tasks.config import VERSION


@task
def version(ctx):
    """Show the current version."""
    print(VERSION)


@task
def clean(ctx):
    """Removes python build artifacts (*.pyc, *.pyo, caches, ...)"""
    ctx.run(
        "find . -type f -name '*.pyc' -delete && "
        "find . -type f -name '*.pyo' -delete && "
        "rm -rf .pytest_cache && "
        "rm -rf .mypy_cache"
    )
