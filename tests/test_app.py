import pytest

from pnp.app import Application
from pnp.runner import Runner
from tests.conftest import path_to_config

configs = [
    "config.api.max.yaml",
    "config.api.min.yaml",
    "config.api.none.yaml",
    "config.engine.yaml",
    "config.multi-deps.yaml",
    "config.multiple-pushes.json",
    "config.simple.json",
    "config.single-dep.yaml"
]


@pytest.mark.parametrize("config", configs)
def test_app(config):
    full_path = path_to_config(config)
    app = Application.from_file(full_path)
    Runner.choose_runner(app)
    # runner.run()
