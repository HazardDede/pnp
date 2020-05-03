from invoke import Collection

from tasks import linting
from tasks import testing

ns = Collection()

linting = Collection.from_module(linting, name="lint")
testing = Collection.from_module(testing, name="test")

ns.add_collection(linting)
ns.add_collection(testing)
