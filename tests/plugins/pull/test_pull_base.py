import pytest

from pnp.plugins.pull import Pull, SyncPull, AsyncPull


def test_compat_no_valid_subclass():
    class NoAbstract(Pull):
        def _pull(self):
            pass

    class SyncAbstract(SyncPull):
        def _pull(self, payload):
            pass

    class AsyncAbstract(AsyncPull):
        async def _pull(self, payload):
            pass

    with pytest.raises(TypeError, match="Instance is not a valid plugin subclass"):
        NoAbstract(name='pytest')

    SyncAbstract(name='pytest')
    AsyncAbstract(name='pytest')


def test_compat_no_pull_method():
    class NoPullMethod(SyncPull):
        pass

    class NoPullMethodAsync(AsyncPull):
        pass

    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        NoPullMethod(name='pytest')

    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        NoPullMethodAsync(name='pytest')
