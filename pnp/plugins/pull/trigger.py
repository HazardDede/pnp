"""Contains so called trigger pulls that wrap polling pulls to decouple them from the
actual polling / scheduling mechanism. Instead of regular polling they can be run
by various external triggers (such as calling a web endpoint)."""

from abc import abstractmethod

import asyncio
from box import Box

from . import PullBase, AsyncPullBase, Polling
from .. import load_optional_module
from ...config import PULL
from ...models import TaskModel
from ...utils import auto_str_ignore


@auto_str_ignore(['model'])
class TriggerBase(PullBase):
    """Base class for all trigger pulls. Manages instantiation of the wrapped polling
    component."""

    def __init__(self, poll, **kwargs):
        super().__init__(**kwargs)
        poll_config = PULL.validate(poll)
        self.model = TaskModel.mk_pull(
            Box({'name': self.name, 'pull': poll_config}),
            base_path=self.base_path
        )
        self.wrapped = self.model.instance

        if not isinstance(self.wrapped, Polling):
            raise TypeError("The component to wrap has to be a polling component")

    @abstractmethod
    def pull(self):
        pass  # pragma: no cover


class Web(TriggerBase, AsyncPullBase):
    """Wraps a poll-based pull and provides a rest-endpoint to externally trigger the
    poll action.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/trigger.Web/index.md

    """

    EXTRA = 'http-server'

    CONF_ERROR = 'error'
    CONF_PAYLOAD = 'payload'
    CONF_SUCCESS = 'success'

    def __init__(self, port, endpoint='/trigger', **kwargs):
        super().__init__(**kwargs)

        self.port = int(port)
        self.endpoint = endpoint and str(endpoint)  # Preserve None
        if not self.endpoint:
            self.endpoint = '/'
        if not self.endpoint.startswith('/'):
            self.endpoint = '/' + self.endpoint

    def pull(self) -> None:
        return self._call_async_pull_from_sync()

    async def async_pull(self) -> None:
        app = self._make_app()
        server = app.create_server(host='0.0.0.0', port=self.port)
        asyncio.ensure_future(server)

        while not self.stopped:
            await asyncio.sleep(0.2)

        server.close()

    def _make_app(self):
        sanic = load_optional_module('sanic', self.EXTRA)
        response = load_optional_module('sanic.response', self.EXTRA)
        app = sanic.Sanic()

        @app.route(self.endpoint)
        async def trigger(request):  # pylint: disable=unused-argument,unused-variable
            try:
                if self.wrapped.supports_async_poll:
                    res = await self.wrapped.async_poll()
                else:
                    loop = asyncio.get_event_loop()
                    res = await loop.run_in_executor(None, self.wrapped.poll)
                self.notify(res)
                return response.json({
                    self.CONF_SUCCESS: True,
                    self.CONF_PAYLOAD: res
                }, 200)
            except Exception as ex:  # pylint: disable=broad-except
                self.logger.exception(ex)
                return response.json({
                    self.CONF_SUCCESS: False,
                    self.CONF_ERROR: str(ex)
                }, 500)

        return app
