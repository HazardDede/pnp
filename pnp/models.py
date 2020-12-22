"""Data model."""
from typing import Dict, List, Union

from pydantic import BaseModel, Field

from pnp.plugins.pull import Pull
from pnp.plugins.push import Push
from pnp.plugins.udf import UserDefinedFunction
from pnp.typing import AnyCallable, SelectorExpression


class PullModel(BaseModel):
    """Model representing a pull configuration."""

    # The actual pull instance of type `Pull`
    instance: Pull

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class PushModel(BaseModel):
    """Model representing a push."""

    # The actual push instance of type `Push`
    instance: Push

    # The given selector expression or None if not passed.
    selector: SelectorExpression = None

    # If true the selector will be computed for each payload item (if applicable)
    unwrap: bool = False

    # A list of push depdencies
    deps: List['PushModel'] = Field(default_factory=list)

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


PushModel.update_forward_refs()


class TaskModel(BaseModel):
    """Model representing a task (pull and dependant pushes)."""

    # The name of the task
    name: str

    # The pull model to produce incoming data
    pull: PullModel

    # List of pushes that are triggered when the pull produced some data
    pushes: List[PushModel]

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class APIModel(BaseModel):
    """Model representing the api server configuration."""

    # The port the api should listen for incoming requests
    port: int

    # Enables the /metrics endpoint
    enable_metrics: bool


class UDFModel(BaseModel):
    """Model representing a user-defined function."""

    # The alias name of the udf
    name: str

    # The callable or the UDF to use
    callable: Union[AnyCallable, UserDefinedFunction]

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


# Alias type for a set of tasks
TaskSet = Dict[str, TaskModel]
