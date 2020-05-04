from invoke import Collection, task

from tasks import (
    docker,
    docs,
    linting,
    testing
)
from tasks.config import VERSION


@task
def version(ctx):
    print(VERSION)


ns = Collection()

docker = Collection.from_module(docker, name="docker")
docs = Collection.from_module(docs, name="docs")
linting = Collection.from_module(linting, name="lint")
testing = Collection.from_module(testing, name="test")

# Subtasks
ns.add_collection(docker)
ns.add_collection(docs)
ns.add_collection(linting)
ns.add_collection(testing)

# Tasks
ns.add_task(version)
