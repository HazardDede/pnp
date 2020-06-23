"""Global pnp api toolkit."""

import asyncio
import logging
from typing import Any, no_type_check, Optional

from sanic import Sanic  # type: ignore
from sanic.request import Request, RequestParameters  # type: ignore
from sanic.response import json, HTTPResponse  # type: ignore
from sanic_openapi import swagger_blueprint, doc  # type: ignore
from sanic_prometheus import monitor  # type: ignore
from typeguard import typechecked

from pnp.models import TaskSet
from pnp.plugins.pull import PullNowMixin, AsyncPullNowMixin
from pnp.utils import Singleton

_LOGGER = logging.getLogger(__name__)


class Response:
    """Common controller responses."""

    ERROR = {"message": doc.String}

    HEALTH = {"success": doc.Boolean()}

    VERSION = {"version": doc.String(), "python": doc.String()}

    EMPTY = {}


class APIError(RuntimeError):
    """Raised when some api error is experienced."""

    DEFAULT_MESSAGE = "Internal API error."

    def __init__(self, message: Optional[str] = None):
        super().__init__(message or self.DEFAULT_MESSAGE)


class APINotConfiguredError(APIError):
    """Raised when the api is not configured / enabled, but is necessary to perform a
    task."""

    DEFAULT_MESSAGE = "API is not configured, but is required to perform this task."


class APINotInitialized(APIError):
    """Raised when the api not initialized properly."""

    DEFAULT_MESSAGE = "API is not initialized properly. Try to `RestAPI.create_api(...)` first."


def bad_request(message: str) -> HTTPResponse:
    """Create a bad request 400 http response."""
    return json({"message": str(message)}, 400)


def internal_error(message: str) -> HTTPResponse:
    """Create a internal error 500 http response."""
    return json({"message": str(message)}, 500)


def success() -> HTTPResponse:
    """Create a simple success response."""
    return json({"success": True}, 200)


def empty() -> HTTPResponse:
    """Create a simple empty response."""
    return json({}, 200)


class RestAPI(Singleton):
    """API singleton."""

    def __init__(self):  # pylint: disable=super-init-not-called
        self.api = None  # type: Optional[Sanic]
        self.port = None  # type: Optional[int]
        self._add_swagger = False
        self._server = None  # type: Any

    def _assert_api(self) -> Sanic:
        if not self.api:
            raise APINotInitialized()
        return self.api

    @no_type_check
    def _add_health_endpoint(self) -> None:
        """Route: /health"""
        api = self._assert_api()

        @api.route("/health")
        @doc.summary("Health")
        @doc.description("Returns a json about the current health of the api")
        @doc.response(200, Response.HEALTH, description="Health information")
        async def health(request: Request,) -> HTTPResponse:  # pylint: disable=unused-variable
            _ = request  # Fake usage
            return success()

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

    def _add_version_endpoint(self) -> None:
        api = self._assert_api()

        @api.route("/version")
        @doc.summary("Return version information")
        @doc.description("Returns the current version of pnp and python")
        @doc.response(200, Response.VERSION, description="Version information")
        @doc.response(500, Response.ERROR, description="Internal error")
        async def version(request: Request,) -> HTTPResponse:  # pylint: disable=unused-variable
            _ = request  # Fake usage
            import sys
            from pnp import __version__

            return json({"version": __version__, "python": sys.version})

    def _add_log_level_endpoint(self) -> None:
        api = self._assert_api()

        @api.route("/loglevel", methods=["POST"])
        @doc.summary("Change the log level")
        @doc.description("Change the logging level of the application during runtime")
        @doc.consumes(
            doc.String(
                "Logging Level. One of DEBUG, INFO, WARNING, ERROR, CRITICAL", name="level",
            ),
            required=True,
        )
        @doc.response(200, Response.EMPTY, description="Empty response")
        @doc.response(400, Response.ERROR, description="Bad request")
        @doc.response(
            500, Response.ERROR, description="Internal error"
        )  # pylint: disable=unused-variable
        async def loglevel(request: Request) -> HTTPResponse:
            args = RequestParameters(request.args)
            level = args.get("level")
            if not level:
                return bad_request("Argument 'level' in query string not set.")
            level = level.upper()
            level_code = logging.getLevelName(level)
            if not isinstance(level_code, int):
                return bad_request("Argument 'level' is not a valid logging level.")
            logging.getLogger().setLevel(level_code)

            return empty()

    @typechecked
    def add_trigger_endpoint(self, task_set: TaskSet) -> None:
        """Route: /trigger.
        Triggers a poll right now without waiting for the schedule to be arrived.
        This will only work for `Polling` pulls, cause a regular pull waits for external
        signals to do it's job."""
        api = self._assert_api()

        @api.route("/trigger", methods=["POST"])
        @doc.summary("Triggers a poll right now")
        @doc.description(
            "Triggers a poll right now without being it's schedule be fulfilled. "
            "This only works for polling components and not for regular pull"
        )
        @doc.consumes(doc.String("The name of the task", name="task"), required=True)
        @doc.response(200, Response.EMPTY, description="Poll was triggered")
        @doc.response(400, Response.ERROR, description="Bad request")  # pylint: disable=unused-variable
        @doc.response(500, Response.ERROR, description="Internal error")
        async def trigger(request: Request) -> HTTPResponse:
            args = RequestParameters(request.args)
            task_name = args.get("task")
            if not task_name:
                return bad_request("Argument 'task' in query string not set.")

            task_name = str(task_name)
            task = task_set.get(task_name)
            if not task:
                return bad_request(
                    "Value '{}' of argument 'task' is not a known task.".format(task_name)
                )

            pull = task.pull.instance
            if not isinstance(pull, (PullNowMixin, AsyncPullNowMixin)):
                return bad_request(
                    "Task '{}' does not support pull_now() / async_pull_now()."
                    " Implement PullNowMixin / AsyncPullMixin for support".format(task_name)
                )

            try:
                if isinstance(pull, AsyncPullNowMixin):
                    await pull.async_pull_now()
                else:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, pull.pull_now)

                return empty()
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("While triggering the poll an error occurred.")
                return internal_error("While triggering the poll an error occurred.")

    @property
    def enabled(self) -> bool:
        """Return True if the api is enabled; otherwise False."""
        return self.api is not None

    @property
    def running(self) -> bool:
        """Return True if the api is running; otherwise False."""
        return self._server is not None

    def create_api(
        self, app_name: str = "pnp", enable_metrics: bool = True, enable_swagger: bool = True,
    ) -> None:
        """
        Creates a sanic application to serve api requests.
        """
        self.api = Sanic(str(app_name))
        logging.getLogger("sanic.root").setLevel(logging.WARNING)

        self._add_health_endpoint()
        self._add_version_endpoint()
        self._add_log_level_endpoint()
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

        self._server = api.create_server(host="0.0.0.0", port=port, debug=False, access_log=False)
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
