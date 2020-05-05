from invoke import Collection

from tasks import (
    build,
    config,
    docker,
    docs,
    linting,
    release,
    testing
)

ns = Collection()

config = Collection.from_module(config, name="config")
docker = Collection.from_module(docker, name="docker")
docs = Collection.from_module(docs, name="docs")
linting = Collection.from_module(linting, name="lint")
release = Collection.from_module(release, name="release")
testing = Collection.from_module(testing, name="test")

# Subtasks
ns.add_collection(config)
ns.add_collection(docker)
ns.add_collection(docs)
ns.add_collection(linting)
ns.add_collection(release)
ns.add_collection(testing)

# Tasks
ns.add_task(build.version)
ns.add_task(build.clean)
