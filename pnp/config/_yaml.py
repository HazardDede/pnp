"""Config Loader for yaml files."""

import os
from functools import partial
from typing import Any, Dict, Iterator, cast, Union, List, Iterable, Optional

import schema as sc
from box import Box
from dictmentor import DictMentor, ext
from ruamel import yaml

from pnp.config._base import Configuration, ConfigLoader
from pnp.engines import Engine as RealEngine, RetryHandler
from pnp.models import UDFModel, PullModel, PushModel, TaskModel, TaskSet, APIModel
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

    plugin_args_name = "args"
    plugin_name = "plugin"

    # Single pull
    Pull = sc.Schema({
        plugin_name: sc.Use(str),
        sc.Optional(plugin_args_name, default={}): {
            sc.Optional(str): object
        },
    })

    # Single push block

    push_selector_name = "selector"
    push_unwrap_name = "unwrap"
    push_deps_name = "deps"

    Push = sc.Schema({
        plugin_name: sc.Use(str),
        sc.Optional(push_selector_name, default=None): sc.Or(object, None),
        sc.Optional(push_unwrap_name, default=False): bool,
        sc.Optional(plugin_args_name, default={}): {
            sc.Optional(str): object
        },
        # deps is a list of push_schemas as well, but cannot declare recursive schemas
        sc.Optional(push_deps_name, default=list()): sc.And(object, sc.Use(make_list))
    })

    # Multiple pushes
    PushList = sc.Schema([Push])

    # Single task (one pull and multiple related pushes)
    task_name = "name"
    task_pull_name = "pull"
    task_push_name = "push"

    Task = sc.Schema({
        task_name: sc.Use(str),
        task_pull_name: Pull,
        task_push_name: sc.And(sc.Or(PushList, Push), sc.Use(make_list))
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

    # API
    api_port_name = "port"
    api_endpoint_name = "endpoints"
    api_endpoint_swagger = "swagger"
    api_endpoint_metrics = "metrics"

    api_endpoint_defaults = {
        api_endpoint_swagger: False,
        api_endpoint_metrics: False
    }

    API = sc.Schema({
        api_port_name: sc.Use(int),
        sc.Optional(api_endpoint_name, default=api_endpoint_defaults): {
            sc.Optional(api_endpoint_swagger, False): sc.Use(bool),
            sc.Optional(api_endpoint_metrics, False): sc.Use(bool)
        }
    })

    # User Defined Functions
    udf_name = "name"

    UDFS = sc.Schema([{
        udf_name: sc.Use(str),
        plugin_name: sc.Use(str),
        sc.Optional(plugin_args_name): sc.Or({
            str: object
        }, None)
    }])

    # Global settings

    global_engine_name = "engine"
    global_api_name = "api"
    global_udfs_name = "udfs"
    global_tasks_name = "tasks"

    GlobalSettings = sc.Schema({
        sc.Optional(sc.Or("anchors", "anchor", "ref", "refs", "alias", "aliases")): object,
        sc.Optional(global_engine_name, default=None): Engine,
        sc.Optional(global_api_name, default=None): API,
        sc.Optional(global_udfs_name, default=None): UDFS,
        global_tasks_name: TaskList
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
    name = '{}_pull'.format(task_config[Schemas.task_name])
    pull_args = task_config[Schemas.task_pull_name][Schemas.plugin_args_name]
    plugin = task_config[Schemas.task_pull_name][Schemas.plugin_name]
    args = {'name': name, **extra, **pull_args}
    return PullModel(instance=cast(PullBase, load_plugin(
        plugin_path=plugin,
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
            args = {'name': push_name, **extra, **push[Schemas.plugin_args_name]}
            unwrap = getattr(push, Schemas.push_unwrap_name, False)
            yield PushModel(
                instance=cast(PushBase, load_plugin(
                    plugin_path=push[Schemas.plugin_name],
                    plugin_type=PushBase,
                    instantiate=True,
                    **args
                )),
                selector=push[Schemas.push_selector_name],
                unwrap=unwrap,
                deps=list(_many(push[Schemas.push_deps_name], push_name))
            )
    pushes = task_config[Schemas.task_push_name]
    prefix = task_config[Schemas.task_name] + "_push"
    return list(_many(pushes, prefix))


def _mk_udf(udf_config: Box) -> UDFModel:
    if not isinstance(udf_config, Box):
        udf_config = Box(udf_config)
    udf_type = cast(
        Union[str, type],
        'callable' if not hasattr(udf_config, Schemas.plugin_args_name) else UserDefinedFunction
    )
    instantiate = hasattr(udf_config, Schemas.plugin_args_name)
    kwargs = udf_config.get(Schemas.plugin_args_name) or {}
    fun = load_plugin(
        plugin_path=udf_config[Schemas.plugin_name],
        plugin_type=udf_type,
        instantiate=instantiate,
        **{'name': udf_config[Schemas.udf_name], **kwargs}
    )
    return UDFModel(name=udf_config[Schemas.udf_name], callable=cast(UserDefinedFunction, fun))


class YamlConfigLoader(ConfigLoader):
    """Configuration loader from a yaml file."""

    def _validate_push_deps(self, push: PushConfig) -> Iterator[PushConfig]:
        """Validates a push against the schema. This is done recursively."""
        _ = self  # Fake usage
        for dependency in push[Schemas.push_deps_name]:
            validated_push = Schemas.Push.validate(dependency)
            validated_push[Schemas.push_deps_name] = list(self._validate_push_deps(validated_push))
            yield validated_push

    def _add_constructors(self) -> None:
        _ = self  # Fake usage
        yaml.SafeLoader.add_constructor(
            u"!engine", partial(_custom_yaml_constructor, clstype=RealEngine)
        )
        yaml.SafeLoader.add_constructor(
            u"!retry", partial(_custom_yaml_constructor, clstype=RetryHandler)
        )

    def _augment(self, configuration: PartialConfig, base_path: str) -> Any:
        """Augments the configuration by using dictmentor with `Environment`,
        `ExternalResource` and `ExternalYamlResource` plguins."""
        _ = self  # Fake usage
        assert isinstance(base_path, str)

        # pnp configuration is probably of list of tasks. dictmentor needs a dict ...
        # ... let's fake it ;-)
        cfg = dict(fake_root=configuration)

        mentor = DictMentor(
            ext.Environment(fail_on_unset=True),
            ext.ExternalResource(base_path=base_path),
            ext.ExternalYamlResource(base_path=base_path)
        )

        # Remove the faked dictionary as root level
        return mentor.augment(cfg)['fake_root']

    def _api_from_config(self, config: Box) -> Optional[APIModel]:
        _ = self  # Fake usage

        api = config.get(Schemas.global_api_name)
        if not api:
            return None

        return APIModel(
            port=api[Schemas.api_port_name],
            enable_metrics=api[Schemas.api_endpoint_name].get(Schemas.api_endpoint_metrics, False),
            enable_swagger=api[Schemas.api_endpoint_name].get(Schemas.api_endpoint_swagger, False)
        )

    def _tasks_from_config(self, config: Box, base_path: Optional[str] = None) -> TaskSet:
        """Create a task from a task configuration."""
        _ = self  # Fake usage

        extra_kwargs = {'base_path': base_path}
        res = {}
        for task in config[Schemas.global_tasks_name]:
            instance = TaskModel(
                name=task[Schemas.task_name],
                pull=_mk_pull(task, **extra_kwargs),
                pushes=list(_mk_push(task, **extra_kwargs))
            )
            res[instance.name] = instance

        return res

    def _udfs_from_config(self, config: Box) -> List[UDFModel]:
        """Creates a UDFModel from a udf configuration snippet."""
        _ = self  # Fake usage

        udfs = config.get(Schemas.global_udfs_name)
        if not udfs:
            return []

        return [_mk_udf(udf_config) for udf_config in udfs or []]

    @classmethod
    def supported_extensions(cls) -> Iterable[str]:
        return ['json', 'yaml']

    def load_pull_from_snippet(self, snippet: Any, name: str, **extra: Any) -> PullModel:
        pull_config = Schemas.Pull.validate(snippet)
        return _mk_pull(Box({'name': name, 'pull': pull_config}), **extra)

    def load_config(self, config_file: str) -> Configuration:
        config_file = str(config_file)
        base_path = os.path.dirname(config_file)

        with open(config_file, 'r') as fp:
            # Custom yaml constructors: !engine and !retry
            self._add_constructors()
            cfg = yaml.safe_load(fp)

        validated = Schemas.Root.validate(self._augment(cfg, base_path))
        # We need to validate each push again against the push-schema.
        # Cause the dependencies of push are pushes as well and we cannot define
        # a recursive schema in one go.
        for pull in validated[Schemas.global_tasks_name]:
            for push in pull[Schemas.task_push_name]:
                push[Schemas.push_deps_name] = list(self._validate_push_deps(push))
        config = Box(validated)

        return Configuration(
            api=self._api_from_config(config),
            engine=config.get(Schemas.global_engine_name) or None,
            udfs=self._udfs_from_config(config),
            tasks=self._tasks_from_config(config, base_path)
        )
