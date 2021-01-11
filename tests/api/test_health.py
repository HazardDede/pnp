from tests.conftest import api_client


def test_endpoint():
    with api_client() as client:
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json() == {"success": True}
