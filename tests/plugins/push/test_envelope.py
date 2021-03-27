import pytest

from pnp.plugins.push import SyncPush, AsyncPush
from pnp.plugins.push.envelope import Envelope


@pytest.mark.asyncio
async def test_unwrap_sync():
    class TestPush(SyncPush):
        @Envelope.unwrap
        def _push(self, envelope, payload):
            """Push, push!"""
            return envelope, payload

    dut = TestPush(name='pytest')
    assert await dut.push({'env': 'test', 'payload': 'data'}) == ({'env': 'test'}, 'data')
    assert await dut.push({'env': 'test', 'data': 'data'}) == ({'env': 'test'}, 'data')
    assert await dut.push("payload") == ({}, "payload")
    assert await dut.push({"foo": "bar"}) == ({}, {"foo": "bar"})
    assert await dut.push({"payload": "payload"}) == ({}, "payload")
    assert await dut.push({"data": "payload"}) == ({}, "payload")
    assert dut._push.__doc__ == "Push, push!"


@pytest.mark.asyncio
async def test_unwrap_async():
    class TestPush(AsyncPush):
        @Envelope.unwrap
        async def _push(self, envelope, payload):
            """Push, push!"""
            return envelope, payload

    dut = TestPush(name='pytest')
    assert await dut.push({'env': 'test', 'payload': 'data'}) == ({'env': 'test'}, 'data')
    assert await dut.push({'env': 'test', 'data': 'data'}) == ({'env': 'test'}, 'data')
    assert dut._push.__doc__ == "Push, push!"


@pytest.mark.asyncio
async def test_parse_sync():
    class TestPush(SyncPush):
        @Envelope.unwrap
        @Envelope.parse("k1")
        @Envelope.parse("k2")
        def _push(self, k1, k2, envelope, payload):
            """Push, push!"""
            return k1, k2, envelope, payload

    dut = TestPush(name="pytest")
    assert await dut.push({'k1': 'v1', 'k2': 'v2', 'payload': 'data'}) == ('v1', 'v2', {'k1': 'v1', 'k2': 'v2'}, "data")
    assert await dut.push({'k1': 'v1', 'payload': 'data'}) == ('v1', None, {'k1': 'v1'}, "data")
    assert dut._push.__doc__ == "Push, push!"


@pytest.mark.asyncio
async def test_parse_async():
    class TestPush(SyncPush):
        @Envelope.unwrap
        @Envelope.parse("k1")
        @Envelope.parse("k2")
        async def _push(self, k1, k2, envelope, payload):
            """Push, push!"""
            return k1, k2, envelope, payload

    dut = TestPush(name="pytest")
    assert await dut.push({'k1': 'v1', 'k2': 'v2', 'payload': 'data'}) == ('v1', 'v2', {'k1': 'v1', 'k2': 'v2'}, "data")
    assert await dut.push({'k1': 'v1', 'payload': 'data'}) == ('v1', None, {'k1': 'v1'}, "data")
    assert dut._push.__doc__ == "Push, push!"


@pytest.mark.asyncio
async def test_parse_async_with_parser():
    class TestPush(SyncPush):

        def parse_k1(self, val):
            _ = self
            return 'transformed: {}'.format(val)

        @Envelope.unwrap
        @Envelope.parse("k1")
        async def _push(self, k1, envelope, payload):
            """Push, push!"""
            return k1, envelope, payload

    dut = TestPush(name="pytest")
    assert await dut.push({'k1': 'v1', 'payload': 'data'}) == ('transformed: v1', {'k1': 'v1'}, "data")
    assert dut._push.__doc__ == "Push, push!"


@pytest.mark.asyncio
async def test_parse_async_with_attribute():
    class TestPush(SyncPush):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.k1 = "attr: v1"

        @Envelope.unwrap
        @Envelope.parse("k1")
        async def _push(self, k1, envelope, payload):
            """Push, push!"""
            return k1, envelope, payload

    dut = TestPush(name="pytest")
    assert await dut.push({'payload': 'data'}) == ('attr: v1', {}, "data")
    assert await dut.push({'k1': 'v1', 'payload': 'data'}) == ('v1', {'k1': 'v1'}, "data")
    assert dut._push.__doc__ == "Push, push!"


@pytest.mark.asyncio
async def test_drop_sync():
    class TestPush(SyncPush):
        @Envelope.unwrap
        @Envelope.parse("k1")
        @Envelope.drop
        def _push(self, k1, payload):
            """Push, push!"""
            return k1, payload

    dut = TestPush(name="pytest")
    assert await dut.push({'payload': 'data'}) == (None, "data")
    assert await dut.push({'k1': 'v1', 'payload': 'data'}) == ('v1', "data")
    assert dut._push.__doc__ == "Push, push!"


@pytest.mark.asyncio
async def test_drop_async():
    class TestPush(SyncPush):
        @Envelope.unwrap
        @Envelope.parse("k1")
        @Envelope.drop
        async def _push(self, k1, payload):
            """Push, push!"""
            return k1, payload

    dut = TestPush(name="pytest")
    assert await dut.push({'payload': 'data'}) == (None, "data")
    assert await dut.push({'k1': 'v1', 'payload': 'data'}) == ('v1', "data")
    assert dut._push.__doc__ == "Push, push!"
