import logging

from tests.conftest import api_client


def test_endpoint():
    with api_client() as client:
        response = client.post('/loglevel?level=ERROR')

        assert response.status_code == 200
        assert response.json() == {}
        assert logging.getLogger().level == logging.ERROR

        response = client.post('/loglevel?level=INFO')

        assert response.status_code == 200
        assert response.json() == {}
        assert logging.getLogger().level == logging.INFO


def test_endpoint_no_log_level():
    with api_client() as client:
        response = client.post('/loglevel')

        assert response.status_code == 422
        assert response.json() == {
            'detail': [{
                'loc': ['query', 'level'],
                'msg': 'field required',
                'type': 'value_error.missing'
            }]
        }


def test_endpoint_unknown_log_level():
    with api_client() as client:
        response = client.post('/loglevel?level=UNKNOWN')

        assert response.status_code == 422
        assert response.json() == {
            'detail': [{
                'ctx': {
                    'pattern': '^DEBUG|INFO|WARNING|ERROR|CRITICAL$'
                },
                'loc': ['query', 'level'],
                'msg': 'string does not match regex '
                '"^DEBUG|INFO|WARNING|ERROR|CRITICAL$"',
                'type': 'value_error.str.regex'
            }]
        }
