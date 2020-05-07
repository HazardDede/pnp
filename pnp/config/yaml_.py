"""Config Loader for yaml files."""

import os
from functools import partial
from typing import Any, Dict, Iterator, cast, Union, List, Iterable, Optional

import schema as sc
from box import Box
from dictmentor import DictMentor, ext
from ruamel import yaml

from pnp.config._base import Configuration
from pnp.engines import Engine as RealEngine, RetryHandler
from pnp.models import UDFModel, PullModel, PushModel, TaskModel, TaskSet
from pnp.plugins import load_plugin
from pnp.plugins.pull import PullBase
from pnp.plugins.push import PushBase
from pnp.plugins.udf import UserDefinedFunction
from pnp.utils import make_list

# Type alias that represents a yaml config snippet
PartialConfig = Any

# Type alias that represents yaml push config snippet
PushConfig = Dict[str, Any]


class Schemas:
    """Collection of validation schemas for different components."""

    # Single pull
    Pull = sc.Schema({
        "plugin": sc.Use(str),
        sc.Optional("args", default={}): {
            sc.Optional(str): object
        },
    })

    # Single push block
    Push = sc.Schema({
        "plugin": sc.Use(str),
        sc.Optional("selector", default=None): sc.Or(object, None),
        sc.Optional("unwrap", default=False): bool,
        sc.Optional("args", default={}): {
            sc.Optional(str): object
        },
        # deps is a list of push_schemas as well, but cannot declare recursive schemas
        sc.Optional("deps", default=list()): sc.And(object, sc.Use(make_list))
    })

    # Multiple pushes
    PushList = sc.Schema([Push])

    # Single task (one pull and multiple related pushes)
    Task = sc.Schema({
        "name": sc.Use(str),
        "pull": Pull,
        "push": sc.And(sc.Or(PushList, Push), sc.Use(make_list))
    })

    # Allow configuration of a single task or a list of tasks
    TaskList = sc.Schema(
        sc.Or(
            sc.And(Task, sc.Use(make_list)),
            [Task]
        )
    )

    # Engine
    Engine = RealEngine

    # User Defined Functions
    UDFS = sc.Schema([{
        "name": sc.Use(str),
        "plugin": sc.Use(str),
        sc.Optional("args"): sc.Or({
            str: object
        }, None)
    }])

    GlobalSettings = sc.Schema({
        sc.Optional(sc.Or("anchors", "anchor", "ref", "refs", "alias", "aliases")): object,
        sc.Optional("engine", default=None): Engine,
        sc.Optional("udfs", default=None): UDFS,
        'tasks': TaskList
    })

    Root = sc.Schema(sc.And(
        sc.Or(
            # Tasks with additional settings and aliases (yaml only)
            GlobalSettings,
            # Tasks without settings or aliases - just a list of tasks (backwards compatibility)
            TaskList,
        ),
        # In case of list only we create a tasks node - so we know it's always there
        sc.Use(lambda x: x if 'tasks' in x else dict(tasks=x))
    ))


def _custom_yaml_constructor(loader: Any, node: Any, clstype: Any) -> Any:
    """YAML custom constructor. Necessary to create an engine and retry handler."""
    args = loader.construct_mapping(node, deep=True)
    if 'type' not in args:
        raise ValueError("You have to specify a 'type' when instantiating a engine with !engine")
    clazz_name = args.pop('type')
    return load_plugin(clazz_name, clstype, **args)


def _mk_pull(task_config: Box, **extra: Any) -> PullModel:
    """Make a pull out of a task configuration."""
    args = {'name': '{task.name}_pull'.format(task=task_config), **extra, **task_config.pull.args}
    return PullModel(instance=cast(PullBase, load_plugin(
        plugin_path=task_config.pull.plugin,
        plugin_type=PullBase,
        instantiate=True,
        **args
    )))


def _mk_push(task_config: Box, **extra: Any) -> List[PushModel]:
    """Make one or more pushes out of task configuration."""
    def _many(pushlist: List[Box], prefix: str) -> Iterable[PushModel]:
        for i, push in enumerate(pushlist):
            push_name = '{prefix}_{i}'.format(
                i=i,
                prefix=prefix
            )
            args = {'name': push_name, **extra, **push.args}
            unwrap = getattr(push, 'unwrap', False)
            yield PushModel(
                instance=cast(PushBase, load_plugin(
                    plugin_path=push.plugin,
                    plugin_type=PushBase,
                    instantiate=True,
                    **args
                )),
                selector=push.selector,
                unwrap=unwrap,
                deps=list(_many(push.deps, push_name))
            )
    return list(_many(task_config.push, "{task_config.name}_push".format(**locals())))


def _mk_udf(udf_config: Box) -> UDFModel:
    if not isinstance(udf_config, Box):
        udf_config = Box(udf_config)
    udf_type = cast(
        Union[str, type],
        'callable' if not hasattr(udf_config, 'args') else UserDefinedFunction
    )
    instantiate = hasattr(udf_config, 'args')
    kwargs = udf_config.get('args') or {}
    fun = load_plugin(
        plugin_path=udf_config.plugin,
        plugin_type=udf_type,
        instantiate=instantiate,
        **{'name': udf_config.name, **kwargs}
    )
    return UDFModel(name=udf_config.name, callable=cast(UserDefinedFunction, fun))


class YamlConfigLoader:
    """Configuration loader from a yaml file."""

    def __init__(self, config_file: str):
        self.config_file = str(config_file)

    def _validate_push_deps(self, push: PushConfig) -> Iterator[PushConfig]:
        """Validates a push against the schema. This is done recursively."""
        _ = self  # Fake usage
        for dependency in push['deps']:
            validated_push = Schemas.Push.validate(dependency)
            validated_push['deps'] = list(self._validate_push_deps(validated_push))
            yield validated_push

    def _add_constructors(self) -> None:
        _ = self  # Fake usage
        yaml.SafeLoader.add_constructor(
            u"!engine", partial(_custom_yaml_constructor, clstype=RealEngine)
        )
        yaml.SafeLoader.add_constructor(
            u"!retry", partial(_custom_yaml_constructor, clstype=RetryHandler)
        )

    def _augment(self, configuration: PartialConfig) -> Any:
        """Augments the configuration by using dictmentor with `Environment`,
        `ExternalResource` and `ExternalYamlResource` plguins."""

        # pnp configuration is probably of list of tasks. dictmentor needs a dict ...
        # ... let's fake it ;-)
        cfg = dict(fake_root=configuration)

        mentor = DictMentor(
            ext.Environment(fail_on_unset=True),
            ext.ExternalResource(base_path=os.path.dirname(self.config_file)),
            ext.ExternalYamlResource(base_path=os.path.dirname(self.config_file))
        )

        # Remove the faked dictionary as root level
        return mentor.augment(cfg)['fake_root']

    def _tasks_from_config(self, config: Box, base_path: Optional[str] = None) -> TaskSet:
        """Create a task from a task configuration."""
        _ = self  # Fake usage

        extra_kwargs = {'base_path': base_path}
        res = {}
        for task in config.tasks:
            instance = TaskModel(
                name=task.name,
                pull=_mk_pull(task, **extra_kwargs),
                pushes=list(_mk_push(task, **extra_kwargs))
            )
            res[instance.name] = instance

        return res

    def _udfs_from_config(self, config: Box) -> List[UDFModel]:
        """Creates a UDFModel from a udf configuration snippet."""
        _ = self  # Fake usage

        if not hasattr(config, 'udfs'):
            return []
        return [_mk_udf(udf_config) for udf_config in config.udfs or []]

    def load_config(self) -> Configuration:
        """Load the yaml configuration."""

        # Custom yaml constructors: !engine and !retry
        self._add_constructors()

        with open(self.config_file, 'r') as fp:
            cfg = yaml.safe_load(fp)

        validated = Schemas.Root.validate(self._augment(cfg))
        # We need to validate each push again against the Push-schema.
        # Cause the dependencies of push are pushes as well and we cannot define
        # a recursive schema in one go.
        for pull in validated['tasks']:
            for push in pull['push']:
                push['deps'] = list(self._validate_push_deps(push))
        config = Box(validated)

        return Configuration(
            engine=config.get('engine') or None,
            udfs=self._udfs_from_config(config),
            tasks=self._tasks_from_config(config, os.path.dirname(self.config_file))
        )
