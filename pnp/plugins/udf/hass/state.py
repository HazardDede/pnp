"""UDF: hass.State."""
from typing import Any, Optional

from pnp.plugins.udf import UserDefinedFunction
from pnp.shared.hass import HassApi
from pnp.typing import UrlLike


class State(UserDefinedFunction):
    """
    Fetches the state of an entity from home assistant by a rest-api request.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#id2
    """
    __REPR_FIELDS__ = ['timeout', 'url']

    def __init__(self, url: UrlLike, token: str, timeout: int = 10, **kwargs: Any):
        super().__init__(**kwargs)
        self.url = str(url)
        self.token = str(token)
        self.timeout: Optional[int] = timeout and int(timeout)
        if self.timeout <= 0:
            self.timeout = None  # Basically means no timeout
        self._client = HassApi(self.url, self.token, self.timeout)

    def _action(self, entity_id: str, attribute: Optional[str] = None) -> Any:
        """
        Calls the home assistant api to fetch the state of the given entity (or one of it's
        attributes).

        Args:
            entity_id (str): The entity id of the entity state of interest.
            attribute: Optionally specify an attribute of the entity.

        Returns:
            Returns the state of the entity itself or - if argument attribute is set - the state
            of the specified attribute of that entity.
        """
        entity_id = str(entity_id)
        attribute = attribute and str(attribute)
        endpoint = 'states/{entity_id}'.format(**locals())

        try:
            response = self._client.call(endpoint)
        except RuntimeError as exc:
            raise RuntimeError(
                "Failed to fetch the state for {entity_id} @ {self.url}".format(**locals())
            ) from exc

        if attribute:
            return response.get('attributes', {}).get(str(attribute))

        return response.get('state', None)

    def action(self, *args: Any, **kwargs: Any) -> Any:
        return self._action(*args, **kwargs)
