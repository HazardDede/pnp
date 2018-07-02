import json

import requests
from flask import Flask

from . import PullBase
from ...utils import make_list
from ...validator import Validator


class RestServer(PullBase):
    """
    Listens on the specified `port` for requests to any endpoint.
    Any data passed to the endpoint will be tried to be parsed to a dictionary (json). If this is not possible
    the data will be passed as is. See sections `Returns` for specific payload and examples.

    Remark: You will not able to make requests to the endpoint DELETE `/_shutdown` because it is used internally.

    Args:
        port (int): The port the rest server should listen to for requests.

    Returns:
        The callback `on_payload` will offer a payload that is a dictionary of the request made.

        Examples:
            curl -X GET 'http://localhost:5000/resource/endpoint?foo=bar&bar=baz' --data '{"baz": "bar"}'
            {
                'endpoint': 'resource/endpoint,
                'method': 'GET',
                'query': {'foo': 'bar', 'bar': 'baz'},
                'data': {'baz': 'bar'},
                'is_json': True
            }
            curl -X GET 'http://localhost:5000/resource/endpoint' --data 'no json obviously'
            {
                'endpoint': 'resource/endpoint,
                'method': 'GET',
                'query': {},
                'data': b'no json obviously',
                'is_json': False
            }

    Example configuration:

        name: rest
        pull:
          plugin: pnp.plugins.pull.rest.RestServer
          args:
            port: 5000
            allowed_methods: [GET, POST]
        push:
          plugin: pnp.plugins.push.simple.Echo

    """
    __prefix__ = "rest"

    METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

    def __init__(self, port=5000, allowed_methods='GET', **kwargs):
        super().__init__(**kwargs)
        self.port = int(port)
        self.allowed_methods = make_list(allowed_methods)
        Validator.subset_of(self.METHODS, allowed_methods=allowed_methods)

    def pull(self):
        self._create_app().run(host='0.0.0.0', port=self.port, threaded=True)

    def stop(self):
        super().stop()
        requests.delete('http://localhost:{port}/_shutdown'.format(port=str(self.port)))

    def _create_app(self):
        that = self
        app = Flask(__name__)

        @app.route('/_shutdown', methods=['DELETE'])
        def shutdown():
            that.shutdown_server()
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

        @app.route('/', defaults={'path': '/'}, methods=self.allowed_methods)
        @app.route('/<path:path>', methods=self.allowed_methods)
        def catch_all(path):
            from flask import request
            data = request.get_json(force=True, silent=True)
            if data is None:  # No valid json in request body > fallback to data
                data = request.data if request.data != b'' else None

            payload = dict(
                endpoint=path,
                levels=path.split('/'),
                method=request.method,
                query=self._flatten_query_args(dict(request.args)),
                data=data,
                is_json=isinstance(data, dict)
            )
            that.notify(payload)

            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

        return app

    @staticmethod
    def shutdown_server():
        from flask import request
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')  # pragma: no cover
        func()

    @staticmethod
    def _flatten_query_args(args):
        """Iterates through query args and transforms any one-element lists to single items.

        Examples:

            >>> RestServer._flatten_query_args({'key': 'value'})  # Return as is
            {'key': 'value'}
            >>> RestServer._flatten_query_args({'key': ['value']})  # One item list -> flatten
            {'key': 'value'}
            >>> RestServer._flatten_query_args({'key': ['value1', 'value2']})  # multiple items list -> no flatten
            {'key': ['value1', 'value2']}
            >>> RestServer._flatten_query_args({'key': ['']})  # Empty string -> None
            {'key': None}
            >>> RestServer._flatten_query_args({'key': []})  # Empty list -> None
            {'key': None}
            >>> RestServer._flatten_query_args({'key': ['', '']})  # Multiple Empty string -> Multiple None's
            {'key': [None, None]}
            >>> RestServer._flatten_query_args("notadict")  # Argument has to be a dict
            Traceback (most recent call last):
            ...
            TypeError: Argument 'args' is expected to be a (<class 'dict'>,), but is <class 'str'>

        """
        def _make_flat(item):
            if not isinstance(item, list):
                return item
            # item -> list
            if len(item) == 0:
                return None
            if len(item) == 1:
                return item[0] if item[0] else None  # Empty string -> None
            return [x if x else None for x in item]

        Validator.is_instance(dict, args=args)
        res = dict()
        for key, val in args.items():
            res[key] = _make_flat(val)
        return res
