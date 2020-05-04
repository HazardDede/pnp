from invoke import Collection, task

from tasks import docker
from tasks import linting
from tasks import testing
from tasks.config import VERSION

ns = Collection()

docker = Collection.from_module(docker, name="docker")
linting = Collection.from_module(linting, name="lint")
testing = Collection.from_module(testing, name="test")


@task
def version(ctx):
    print(VERSION)


ns.add_collection(docker)
ns.add_collection(linting)
ns.add_collection(testing)
ns.add_task(version)
