from tests.conftest import api_client


def test_endpoint():
    with api_client() as client:
        response = client.get('/docs')
        assert response.status_code == 200
