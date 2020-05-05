from invoke import task

from tasks.config import (
    SOURCE_PATH,
    TEST_PATH
)


@task
def doctest(ctx):
    """Only runs doctests using pytest. Target `pytest` includes doctests."""
    ctx.run(
        "pytest --verbose --color=yes --doctest-modules {}".format(SOURCE_PATH)
    )


@task
def pytest(ctx):
    """Runs unit tests using pytest."""
    ctx.run(
        "pytest --verbose --color=yes "
        "--durations=10 "
        "--doctest-modules "
        "--cov={source} --cov-report html --cov-report term {test} "
        "{source}".format(source=SOURCE_PATH, test=TEST_PATH),
        pty=True
    )


@task(pytest, default=True)
def test(ctx):
    """Runs all tests against the codebase."""
