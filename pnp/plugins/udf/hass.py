from . import UserDefinedFunction


class State (UserDefinedFunction):
    __prefix__ = 'hass'

    def __init__(self, url, token, timeout=10, **kwargs):
        super().__init__(**kwargs)
        self.url = str(url)
        self.token = str(token)
        self.timeout = timeout and int(timeout)
        if self.timeout <= 0:
            self.timeout = None  # Basically means no timeout

    def action(self, entity_id, attribute=None):
        from requests import get
        import urllib.parse as urlparse

        entity_id = str(entity_id)
        attribute = attribute and str(attribute)
        url = urlparse.urljoin(self.url, '/api/states/{entity_id}'.format(**locals()))
        headers = {
            'Authorization': 'Bearer {self.token}'.format(**locals()),
            'content-type': 'application/json',
        }

        response = get(url, headers=headers, timeout=self.timeout)
        if response.status_code != 200:
            raise RuntimeError("Failed to fetch the state for {entity_id} @ {self.url}"
                               "\nHttp Code: {response.status_code}"
                               "\nMessage: {response.text}".format(**locals()))

        if attribute:
            return response.json().get('attributes', {}).get(str(attribute))

        return response.json().get('state', None)
