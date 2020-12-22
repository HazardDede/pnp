from tests.conftest import api_client


def test_endpoint():
    with api_client() as client:
        response = client.get('/version')
        assert response.status_code == 200
        from pnp import __version__
        assert response.json()['version'] == __version__
