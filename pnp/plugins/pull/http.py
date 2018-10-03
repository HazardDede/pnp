import json

import requests
from flask import Flask

from . import PullBase
from ...utils import auto_str_ignore, make_list, HTTP_METHODS
from ...validator import Validator


@auto_str_ignore(ignore_list=['server'])
class Server(PullBase):
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

    SERVER_IMPL = ['gevent', 'flask']

    def __init__(self, port=5000, allowed_methods='GET', server_impl='gevent', **kwargs):
        super().__init__(**kwargs)
        self.port = int(port)
        self.allowed_methods = [m.upper() for m in make_list(allowed_methods)]
        Validator.subset_of(HTTP_METHODS, allowed_methods=self.allowed_methods)

        self.server_impl = server_impl
        Validator.one_of(self.SERVER_IMPL, server_impl=self.server_impl)

        # Instance of the actual http server (wsgi)
        self.server = None

    def pull(self):
        app = self._create_app()
        if self.server_impl == 'flask':
            # Running the flask app with flask development server (do not use for production!)
            app.run(host='0.0.0.0', port=self.port, threaded=True)
            self.server = app
        elif self.server_impl == 'gevent':
            from gevent.pywsgi import WSGIServer
            self.server = WSGIServer(('', self.port), app)
            self.server.serve_forever()

    def stop(self):
        super().stop()
        if self.server_impl == 'flask':
            requests.delete('http://localhost:{port}/_shutdown'.format(port=str(self.port)))
        elif self.server_impl == 'gevent':
            self.server.stop()

    def _create_app(self):
        that = self
        app = Flask(__name__)

        if self.server_impl == 'flask':
            # We need to register a shutdown endpoint, to end the serving if using the flask development server
            @app.route('/_shutdown', methods=['DELETE'])
            def shutdown():
                from flask import request
                func = request.environ.get('werkzeug.server.shutdown')
                if func is None:
                    raise RuntimeError('Not running with the Werkzeug Server')  # pragma: no cover
                func()
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
                levels=["/"] if path == "/" else path.split('/'),
                method=request.method,
                query=self._flatten_query_args(dict(request.args)),
                data=data,
                is_json=isinstance(data, dict),
                url=request.url,
                full_path=request.full_path,
                path=request.path
            )
            that.notify(payload)

            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

        return app

    @staticmethod
    def _flatten_query_args(args):
        """Iterates through query args and transforms any one-element lists to single items.

        Examples:

            >>> Server._flatten_query_args({'key': 'value'})  # Return as is
            {'key': 'value'}
            >>> Server._flatten_query_args({'key': ['value']})  # One item list -> flatten
            {'key': 'value'}
            >>> Server._flatten_query_args({'key': ['value1', 'value2']})  # multiple items list -> no flatten
            {'key': ['value1', 'value2']}
            >>> Server._flatten_query_args({'key': ['']})  # Empty string -> None
            {'key': None}
            >>> Server._flatten_query_args({'key': []})  # Empty list -> None
            {'key': None}
            >>> Server._flatten_query_args({'key': ['', '']})  # Multiple Empty string -> Multiple None's
            {'key': [None, None]}
            >>> Server._flatten_query_args("notadict")  # Argument has to be a dict
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
