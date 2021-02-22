"""Pull: simple.RunOnce."""

from typing import Any

from pnp.config import load_pull_from_snippet
from pnp.plugins import Plugin
from pnp.plugins.pull import AsyncPull
from pnp.typing import Payload


class RunOnce(AsyncPull):
    """
    Takes another valid `plugins.pull.Polling` component and immediately executes it and ventures
    down the given `plugins.push` components. If no component is given it will simple execute the
    push chain.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#simple-runonce
    """

    __REPR_FIELDS__ = ['model']

    def __init__(self, poll: Any = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.model = None
        self.wrapped = None
        if poll:
            self.model = load_pull_from_snippet(poll, base_path=self.base_path, name=self.name)
            self.wrapped = self.model.instance

            if not self.wrapped.supports_pull_now:
                raise TypeError(
                    "Pull does not support pull_now()."
                    " Implement PullNowMixin / AsyncPullNowMixin for support"
                )

    @property
    def can_exit(self) -> bool:
        return True  # pragma: no cover

    async def _pull(self) -> None:
        if not self.wrapped:
            self.notify({})  # Just notify about an empty dict
        else:
            def callback(plugin: Plugin, payload: Payload) -> None:
                _ = plugin  # Fake usage
                self.notify(payload)

            self.wrapped.callback(callback)
            await self.wrapped.pull_now()
