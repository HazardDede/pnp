"""Global pnp api toolkit."""

import asyncio
import logging
from typing import Any, no_type_check, Optional

from sanic import Sanic  # type: ignore
from sanic.request import Request, RequestParameters  # type: ignore
from sanic.response import json, HTTPResponse  # type: ignore
from sanic_openapi import swagger_blueprint, doc  # type: ignore
from sanic_prometheus import monitor  # type: ignore

from pnp.models import TaskSet
from pnp.plugins.pull import Polling
from pnp.utils import Singleton

_LOGGER = logging.getLogger(__name__)


class Response:
    """Common controller responses."""
    ERROR = {
        'message': doc.String
    }

    HEALTH = {
        'success': doc.Boolean()
    }

    EMPTY = {}


def bad_request(message: str) -> HTTPResponse:
    """Create a bad request 400 http response."""
    return json({'message': message}, 400)


def internal_error(message: str) -> HTTPResponse:
    """Create a internal error 500 http response."""
    return json({'message': message}, 500)


class RestAPI(Singleton):
    """API singleton."""
    def __init__(self):  # pylint: disable=super-init-not-called
        self.api = None  # type: Optional[Sanic]
        self.port = None  # type: Optional[int]
        self._add_swagger = False
        self._server = None  # type: Any

    def _assert_api(self) -> Sanic:
        if not self.api:
            raise RuntimeError("You have to call create_api first")
        return self.api

    @no_type_check
    def _add_health_endpoint(self) -> None:
        """Route: /health"""
        api = self._assert_api()

        @api.route('/health')
        @doc.summary("Health")
        @doc.description("Returns a json about the current health of the api")
        @doc.response(200, Response.HEALTH, description="Health information")
        async def health(request: Request) -> HTTPResponse:  # pylint: disable=unused-variable
            _ = request  # Fake usage
            return json({'success': True})

    def _add_swagger_endpoint(self) -> None:
        """Route: /swagger"""
        self._assert_api()
        # Memorize that we want to add the swagger endpoint
        # We do it in the last possible moment, so that it can
        # pick up any additional endpoints registered later
        self._add_swagger = True

    def _add_monitoring_endpoint(self) -> None:
        """Route: /metrics"""
        api = self._assert_api()

        monitor(api).expose_endpoint()

    def add_trigger_endpoint(self, task_set: TaskSet) -> None:
        """Route: /trigger.
        Triggers a poll right now without waiting for the schedule to be arrived.
        This will only work for `Polling` pulls, cause a regular pull waits for external
        signals to do it's job."""
        api = self._assert_api()

        @api.route('/trigger', methods=["POST"])
        @doc.summary("Triggers a poll right now")
        @doc.description(
            "Triggers a poll right now without being it's schedule be fulfilled. "
            "This only works for polling components and not for regular pull"
        )
        @doc.consumes(doc.String("The name of the task", name='task'), required=True)
        @doc.response(200, Response.EMPTY, description="Poll was triggered")
        @doc.response(400, Response.ERROR, description="Bad request")  # pylint: disable=unused-variable
        @doc.response(500, Response.ERROR, description="Internal error")
        async def trigger(request: Request) -> HTTPResponse:
            args = RequestParameters(request.args)
            task_name = args.get('task')
            if not task_name:
                return bad_request("Argument 'task' in query string not set.")

            task_name = str(task_name)
            task = task_set.get(task_name)
            if not task:
                return bad_request(
                    "Value '{}' of argument 'task' is not a known task.".format(task_name)
                )

            pull = task.pull.instance
            if not isinstance(pull, Polling):
                return bad_request(
                    "Can only trigger polling pulls, but pull instance of task '{}' is not "
                    "a poll.".format(task_name)
                )

            try:
                await pull.run_now()
                return json({}, 200)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("While triggering the poll an error occurred.")
                return internal_error("While triggering the poll an error occurred.")

    def create_api(
            self, app_name: str = 'pnp', enable_metrics: bool = True, enable_swagger: bool = True
    ) -> None:
        """
        Creates a sanic application to serve api requests.
        """
        self.api = Sanic(str(app_name))
        logging.getLogger('sanic.root').setLevel(logging.WARNING)

        self._add_health_endpoint()
        if bool(enable_swagger):
            self._add_swagger_endpoint()
        if bool(enable_metrics):
            self._add_monitoring_endpoint()

    def run_api_background(self, port: int = 9999) -> None:
        """Run the api application in the background. The control will be returned to the caller."""
        api = self._assert_api()
        port = int(port)
        self.port = port

        if self._add_swagger:
            api.blueprint(swagger_blueprint)

        self._server = api.create_server(
            host="0.0.0.0",
            port=port,
            debug=False,
            access_log=False
        )
        asyncio.ensure_future(self._server)

        _LOGGER.info("API server started @ port %s", port)

    def shutdown(self) -> None:
        """Shutdown the api."""
        if self._server:
            self._server.close()
        self.api = None
        self.port = None
        self._add_swagger = False
        self._server = None