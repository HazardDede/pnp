"""Global pnp api toolkit."""

import asyncio
import logging
from typing import Any, no_type_check

from sanic import Sanic  # type: ignore
from sanic.request import Request  # type: ignore
from sanic.response import json, HTTPResponse  # type: ignore
from sanic_openapi import swagger_blueprint, doc  # type: ignore
from sanic_prometheus import monitor  # type: ignore

_LOGGER = logging.getLogger(__name__)

# type alias for API type
API = Sanic


class Response:
    """Common controller responses."""
    ERROR = {
        'message': doc.String
    }

    HEALTH_RESPONSE = {
        'success': doc.Boolean()
    }


@no_type_check
def _add_health_endpoint(api: API) -> None:
    """Route: /health"""
    @api.route('/health')
    @doc.summary("Health")
    @doc.description("Returns a json about the current health of the api")
    @doc.response(200, Response.HEALTH_RESPONSE, description="Health information")
    async def health(request: Request) -> HTTPResponse:  # pylint: disable=unused-variable
        _ = request  # Fake usage
        return json({'success': True})


def _add_swagger_endpoint(api: API) -> None:
    """Route: /swagger"""
    api.blueprint(swagger_blueprint)


def _add_monitoring_endpoint(api: API) -> None:
    """Route: /metrics"""
    monitor(api).expose_endpoint()


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
