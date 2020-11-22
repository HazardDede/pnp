"""Contains a catch all route."""

from typing import Iterable, Callable, Awaitable, List, Dict, Union, Any

from fastapi import FastAPI
from pydantic import BaseModel  # pylint: disable=no-name-in-module
from starlette.requests import Request
from typeguard import typechecked

from pnp import validator
from pnp.api.models import HealthResponse
from pnp.utils import HTTP_METHODS
from .base import Endpoint


class CatchAllRequest(BaseModel):
    """Incoming request that is passed as an argument to the callback when
    a request hits the specified route."""
    endpoint: str
    levels: List[str]
    method: str
    query_params: Dict[str, Union[List[Any], Any]]
    data: Any
    is_json_data: bool
    url: str
    full_path: str
    path: str


# Callback when a request hits the route
CatchAllCallback = Callable[[CatchAllRequest], Awaitable[None]]


class CatchAllRoute(Endpoint):
    """Catch all requests under a specific route prefix."""

    @typechecked
    def __init__(
            self, route_prefix: str, allowed_methods: Iterable[str], callback: CatchAllCallback
    ):
        self.route_prefix = str(route_prefix)
        self.allowed_methods = list(allowed_methods)
        self.callback = callback
        validator.subset_of(HTTP_METHODS, allowed_methods=self.allowed_methods)

    async def _endpoint_root(self, request: Request) -> HealthResponse:
        """Any requests made to this endpoint will be tracked by the attached
        pull.http.Server component."""
        return await self._process_request(request, '/')

    async def _endpoint_subpath(self, request: Request, sub_path: str) -> HealthResponse:
        """Any requests made to this endpoint will be tracked by the attached
        pull.http.Server component."""
        return await self._process_request(request, sub_path)

    async def _process_request(self, request: Request, path: str) -> HealthResponse:
        assert self.callback

        try:
            data = await request.json()
            is_json = True
        except ValueError:
            data = (await request.body())
            if data == b"":
                data = None
            is_json = False

        query_params: Dict[str, Any] = {}
        for param_key in request.query_params:
            # print(param_key, value, request.query_params.getlist(key))
            val = request.query_params.getlist(param_key)
            if len(val) == 1:
                query_params[param_key] = val[0]  # Single item list only
            else:
                query_params[param_key] = val

        callback_request = CatchAllRequest(
            endpoint=path,
            levels=["/"] if path == "/" else path.split('/'),
            method=request.method,
            query_params=query_params,
            data=data,
            is_json_data=is_json,
            url=str(request.url),
            full_path="{}?{}".format(request.url.path, request.url.query),
            path=request.url.path
        )

        await self.callback(callback_request)
        return HealthResponse()

    def attach(self, fastapi: FastAPI) -> None:
        """Attach the endpoint to the serving component."""
        for method in self.allowed_methods:
            fun = getattr(fastapi, method.lower(), None)
            if fun:
                fun(
                    path=f"/{self.route_prefix}",
                    response_model=HealthResponse,
                )(self._endpoint_root)
                fun(
                    path=f"/{self.route_prefix}/{{sub_path:path}}",
                    response_model=HealthResponse
                )(self._endpoint_subpath)
