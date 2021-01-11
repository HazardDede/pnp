"""Http related plugins."""

import asyncio
from typing import Union, Iterable, Any

from pnp import validator
from pnp.api import RestAPI, APINotConfiguredError
from pnp.api.endpoints import CatchAllRoute, CatchAllRequest
from pnp.plugins.pull import AsyncPull
from pnp.utils import make_list, HTTP_METHODS


class Server(AsyncPull):
    """
    Creates a specific route on the builtin api server and listens to any call to
    that route.
    Any data passed to the endpoint will be tried to be parsed to a dictionary (json).
    If this is not possible the data will be passed as is.

    You need to enable the api via configuration to make this work.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/http.Server/index.md
    """
    __REPR_FIELDS__ = ['allowed_methods', 'prefix_path']

    def __init__(
            self, prefix_path: str, allowed_methods: Union[str, Iterable[str]] = 'GET',
            **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.prefix_path = str(prefix_path)
        self.allowed_methods = [str(m).upper() for m in make_list(allowed_methods)]
        validator.subset_of(HTTP_METHODS, allowed_methods=self.allowed_methods)

    async def _incoming(self, request: CatchAllRequest):
        def _make_clean(item):
            if not item:  # Empty string or empty list
                return None
            if not isinstance(item, list):
                return item
            # item -> list
            if len(item) == 1:
                return item[0] if item[0] else None  # Empty string -> None
            return [x for x in item if x]

        query_params = {}
        for param_key, param_value in request.query_params.items():
            value = _make_clean(param_value)
            if value:
                query_params[param_key] = value

        payload = dict(
            endpoint=request.endpoint,
            levels=request.levels,
            method=request.method,
            query=query_params,
            data=request.data,
            is_json=request.is_json_data,
            url=request.url,
            full_path=request.full_path,
            path=request.path
        )
        self.notify(payload)

    async def _pull(self) -> None:
        restapi = RestAPI()
        if not restapi.enabled:
            raise APINotConfiguredError()
        CatchAllRoute(
            route_prefix=self.prefix_path,
            allowed_methods=self.allowed_methods,
            callback=self._incoming
        ).attach(restapi.fastapi)

        while not self.stopped:
            await asyncio.sleep(0.1)
