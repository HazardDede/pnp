import pytest

from pnp.api.endpoints import Trigger
from pnp.models import TaskModel, PullModel, PushModel
from pnp.plugins.push.simple import Nop
from tests.conftest import api_client
from tests.dummies.polling import SyncPollingDummy, AsyncPollingDummy, NoPollingDummy, ErrorPollingDummy


@pytest.mark.parametrize("clazz", [
    SyncPollingDummy,
    AsyncPollingDummy
])
def test_endpoint_working(clazz):

    polling = clazz(name='pytest_pull')
    result = []
    polling.callback(lambda pull, payload: result.append(payload))
    tasks = {
        'pytest': TaskModel(
            name='pytest',
            pull=PullModel(instance=polling),
            pushes=[PushModel(instance=Nop(name='pytest_push'))]
        )
    }
    with api_client(Trigger(tasks)) as client:
        response = client.post('/trigger?task=pytest')
        assert response.status_code == 200
        assert response.json() == {}
        assert result == [42]


def test_endpoint_no_task():
    with api_client(Trigger([])) as client:
        response = client.post('/trigger')
        assert response.status_code == 422
        assert response.json() == {
            'detail': [{
                'loc': ['query', 'task'],
                'msg': 'field required',
                'type': 'value_error.missing'
            }]
        }


def test_endpoint_unknown_task():
    tasks = {
        'pytest': TaskModel(
            name='pytest',
            pull=PullModel(instance=SyncPollingDummy(name='pytest_pull')),
            pushes=[PushModel(instance=Nop(name='pytest_push'))]
        )
    }
    with api_client(Trigger(tasks)) as client:
        response = client.post('/trigger?task=unknown')
        assert response.status_code == 422
        assert response.json() == {'detail': "Given task name 'unknown' is not a known task."}



def test_endpoint_not_a_poll():
    tasks = {
        'pytest': TaskModel(
            name='pytest',
            pull=PullModel(instance=NoPollingDummy(name='pytest_pull')),
            pushes=[PushModel(instance=Nop(name='pytest_push'))]
        )
    }
    with api_client(Trigger(tasks)) as client:
        response = client.post('/trigger?task=pytest')
        assert response.status_code == 422
        assert response.json() == {
            'detail': "Task 'pytest' does not support pull_now(). "
                      "Implement PullNowMixin / AsyncPullNowMixin for support"
        }


def test_endpoint_polling_error():
    tasks = {
        'pytest': TaskModel(
            name='pytest',
            pull=PullModel(instance=ErrorPollingDummy(name='pytest_pull')),
            pushes=[PushModel(instance=Nop(name='pytest_push'))]
        )
    }
    with api_client(Trigger(tasks)) as client:
        response = client.post('/trigger?task=pytest')
        assert response.status_code == 500
        assert response.json() == {'detail': 'While triggering the poll an error occurred.'}
