"""Global pnp api toolkit."""

import asyncio
import logging
from typing import Any, no_type_check

from sanic import Sanic  # type: ignore
from sanic.request import Request, RequestParameters  # type: ignore
from sanic.response import json, HTTPResponse  # type: ignore
from sanic_openapi import swagger_blueprint, doc  # type: ignore
from sanic_prometheus import monitor  # type: ignore

from pnp.models import TaskSet
from pnp.plugins.pull import Polling

_LOGGER = logging.getLogger(__name__)

# type alias for API type
API = Sanic


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


@no_type_check
def _add_health_endpoint(api: API) -> None:
    """Route: /health"""
    @api.route('/health')
    @doc.summary("Health")
    @doc.description("Returns a json about the current health of the api")
    @doc.response(200, Response.HEALTH, description="Health information")
    async def health(request: Request) -> HTTPResponse:  # pylint: disable=unused-variable
        _ = request  # Fake usage
        return json({'success': True})


def _add_swagger_endpoint(api: API) -> None:
    """Route: /swagger"""
    api.blueprint(swagger_blueprint)


def _add_monitoring_endpoint(api: API) -> None:
    """Route: /metrics"""
    monitor(api).expose_endpoint()


def add_trigger_endpoint(api: API, task_set: TaskSet) -> None:
    """Route: /trigger.
    Triggers a poll right now without waiting for the schedule to be arrived.
    This will only work for `Polling` pulls, cause a regular pull waits for external
    signals to do it's job."""
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
        app_name: str = 'pnp', enable_metrics: bool = True, enable_swagger: bool = True
) -> API:
    """
    Creates a sanic application to serve api requests.
    """
    api = Sanic(str(app_name))
    logging.getLogger('sanic.root').setLevel(logging.WARNING)

    _add_health_endpoint(api)
    if bool(enable_swagger):
        _add_swagger_endpoint(api)
    if bool(enable_metrics):
        _add_monitoring_endpoint(api)

    return api


def api_coro(api: API, port: int = 9090) -> Any:
    """Return a co-routine to run the api on an event loop of your choice."""
    port = int(port)
    return api.create_server(
        host="0.0.0.0",
        port=port,
        debug=False,
        access_log=False
    )


def run_api_background(api: API, port: int = 9999) -> Any:
    """Run the api application in the background. The control will be returned to the caller."""
    server = api_coro(api, port)
    asyncio.ensure_future(server)

    _LOGGER.info("API server started @ port %s", port)

    return server
