"""Http related plugins."""

import asyncio
from typing import Union, Iterable, Any, no_type_check, Dict

from sanic import Sanic
from sanic.exceptions import InvalidUsage
from sanic.request import Request
from sanic.response import HTTPResponse

from pnp import validator
from pnp.api import RestAPI, APINotConfiguredError, success
from pnp.plugins.pull import AsyncPullBase
from pnp.utils import make_list, HTTP_METHODS


class Server(AsyncPullBase):
    """
    Creates a specific route on the builtin api server and listens to any call to
    that route.
    Any data passed to the endpoint will be tried to be parsed to a dictionary (json).
    If this is not possible the data will be passed as is.

    You need to enable the api via configuration to make this work.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/http.Server/index.md
    """
    def __init__(
            self, prefix_path: str, allowed_methods: Union[str, Iterable[str]] = 'GET',
            **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.prefix_path = str(prefix_path)
        self.allowed_methods = [str(m).upper() for m in make_list(allowed_methods)]
        validator.subset_of(HTTP_METHODS, allowed_methods=self.allowed_methods)

    def _add_catch_all_endpoint(self, api: Sanic) -> None:
        @no_type_check
        @api.route('/{}'.format(self.prefix_path), methods=self.allowed_methods)
        @api.route('/{}/<path:path>'.format(self.prefix_path), methods=self.allowed_methods)
        async def catch_all(request: Request, path=None) -> HTTPResponse:  # pylint: disable=unused-variable
            path = path or '/'
            try:
                data = request.json
            except InvalidUsage:
                data = request.body

            payload = dict(
                endpoint=path,
                levels=["/"] if path == "/" else path.split('/'),
                method=request.method,
                query=self._flatten_query_args(dict(request.args)),
                data=data,
                is_json=isinstance(data, dict),
                url=request.url,
                full_path="{}?{}".format(request.path, request.query_string),
                path=request.path
            )
            self.notify(payload)

            return success()

    async def async_pull(self) -> None:
        restapi = RestAPI()
        if not restapi.enabled:
            raise APINotConfiguredError()
        self._add_catch_all_endpoint(restapi.api)
        while not self.stopped:
            await asyncio.sleep(0.1)

    @staticmethod
    def _flatten_query_args(args: Any) -> Dict[Any, Any]:
        """Iterates through query args and transforms any one-element lists to single items.

        Examples:

            >>> Server._flatten_query_args({'key': 'value'})  # Return as is
            {'key': 'value'}
            >>> Server._flatten_query_args({'key': ['value']})  # One item list -> flatten
            {'key': 'value'}
            >>> # multiple items list -> no flatten
            >>> Server._flatten_query_args({'key': ['value1', 'value2']})
            {'key': ['value1', 'value2']}
            >>> Server._flatten_query_args({'key': ['']})  # Empty string -> None
            {'key': None}
            >>> Server._flatten_query_args({'key': []})  # Empty list -> None
            {'key': None}
            >>> # Multiple Empty string -> Multiple None's
            >>> Server._flatten_query_args({'key': ['', '']})
            {'key': [None, None]}
            >>> Server._flatten_query_args("notadict")  # Argument has to be a dict
            Traceback (most recent call last):
            ...
            TypeError: Argument 'args' is expected to be a (<class 'dict'>,), but is <class 'str'>

        """
        def _make_flat(item):
            if not item:
                return None
            if not isinstance(item, list):
                return item
            # item -> list
            if len(item) == 1:
                return item[0] if item[0] else None  # Empty string -> None
            return [x if x else None for x in item]

        validator.is_instance(dict, args=args)
        res = dict()
        for key, val in args.items():
            res[key] = _make_flat(val)
        return res
