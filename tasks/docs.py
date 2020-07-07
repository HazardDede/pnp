from invoke import task


@task(default=True)
def docs(ctx):
    """Creates the sphinx documentation."""
    ctx.run("cd docs; make clean html", pty=True)
