"""Home assistant related user-defined functions."""

from pnp.plugins.udf import UserDefinedFunction
from pnp.shared.hass import HassApi
from pnp.utils import auto_str_ignore


@auto_str_ignore(['_client', 'token'])
class State(UserDefinedFunction):
    """
    Fetches the state of an entity from home assistant by a rest-api request.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/udf/hass.State/index.md
    """
    def __init__(self, url, token, timeout=10, **kwargs):
        super().__init__(**kwargs)
        self.url = str(url)
        self.token = str(token)
        self.timeout = timeout and int(timeout)
        if self.timeout <= 0:
            self.timeout = None  # Basically means no timeout
        self._client = HassApi(self.url, self.token, self.timeout)

    def action(self, entity_id, attribute=None):  # pylint: disable=arguments-differ
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
