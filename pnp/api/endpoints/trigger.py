"""Contains a trigger endpoint."""

import logging

from fastapi import FastAPI, Query, HTTPException
from starlette.responses import JSONResponse

from pnp.api.models import EmptyResponse
from pnp.models import TaskSet
from .base import Endpoint

_LOGGER = logging.getLogger(__name__)


class Trigger(Endpoint):
    """Triggers a poll right now without being it's schedule be fulfilled.
    This only works for polling components and not for regular pull"""

    def __init__(self, tasks: TaskSet):
        self.tasks = tasks

    async def endpoint(
            self,
            task_name: str = Query(
                ...,
                title="Task",
                description="The name of the task to trigger right now",
                alias="task"
            )
    ) -> JSONResponse:
        """Triggers a poll right now without being it's schedule be fulfilled.
        This only works for polling components and not for regular pull"""

        task = self.tasks.get(task_name)
        if not task:
            raise HTTPException(
                status_code=422,
                detail=f"Given task name '{task_name}' is not a known task."
            )

        pull = task.pull.instance
        if not pull.supports_pull_now:
            raise HTTPException(
                status_code=422,
                detail=f"Task '{task_name}' does not support pull_now(). "
                       f"Implement PullNowMixin / AsyncPullNowMixin for support"
            )

        try:
            await pull.pull_now()
            return EmptyResponse()
        except Exception as exc:  # pylint: disable=broad-except
            _LOGGER.exception("While triggering the poll an error occurred.")
            raise HTTPException(
                status_code=500,
                detail="While triggering the poll an error occurred."
            ) from exc

    def attach(self, fastapi: FastAPI) -> None:
        fastapi.post(
            path="/trigger",
            response_class=JSONResponse,
            responses={
                500: {"description": "Internal Server Error"}
            }
        )(self.endpoint)
