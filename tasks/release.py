from invoke import task


@task
def next_version(ctx, version_part):
    """Prepares the next release.

    version_part: Part of the version to bump (patch, minor, major).
    """
    res = ctx.run(
        'bumpversion --dry-run --allow-dirty --list {} | grep new_version | sed s,"^.*=",,'.format(version_part),
        hide=True
    )
    print("Next version is ", res.stdout)
    ctx.run(
        "bumpversion {} && git diff".format(version_part)
    )
    print("Review your version changes first")
    print("Accept your version: invoke release.accept-version")
    print("Accept your version: invoke release.revoke-version")


@task
def accept_version(ctx):
    """Accepts the staged version."""
    ctx.run("git push && git push --tags")


@task
def revoke_version(ctx):
    """Rollback the staged version."""
    # Remove the tag and rollback the commit
    ctx.run(
        "git tag -d `git describe --tags --abbrev=0` && git reset --hard HEAD~1 "
    )


@task
def dist(ctx):
    """Create a python distribution (source and wheel)."""
    ctx.run("poetry build")


@task(dist)
def testpypi(ctx):
    """Publishes the package to testpypi."""
    ctx.run("poetry publish --repository testpypi")


@task(dist)
def pypi(ctx):
    """Publishes the package to pypi."""
    ctx.run("poetry publish")
