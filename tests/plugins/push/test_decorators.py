import pytest

from pnp.plugins.push import enveloped, PushBase, parse_envelope, drop_envelope


@pytest.yield_fixture(scope='function')
def push_enveloped():
    class _Dummy(PushBase):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        @enveloped
        def push(self, envelope, payload):
            """Push, push!"""
            return envelope, payload

        @enveloped
        async def async_push(self, envelope, payload):
            """Push, push!"""
            return envelope, payload
    yield _Dummy(name='pytest')


def test_enveloped_for_doc(push_enveloped):
    assert push_enveloped.push.__doc__ == "Push, push!"
    assert push_enveloped.async_push.__doc__ == "Push, push!"


@pytest.mark.asyncio
async def test_enveloped_for_correct_split(push_enveloped):
    push = push_enveloped
    assert push.push({}) == ({}, {})
    assert push.push(None) == ({}, None)
    assert push.push({'data': 'value'}) == ({}, 'value')
    assert push.push({'payload': 'value'}) == ({}, 'value')
    assert push.push({'key': 'any'}) == ({}, {'key': 'any'})
    assert push.push({'data': 'value', 'header': 'head'}) == ({'header': 'head'}, 'value')

    assert await push.async_push({}) == ({}, {})
    assert await push.async_push(None) == ({}, None)
    assert await push.async_push({'data': 'value'}) == ({}, 'value')
    assert await push.async_push({'payload': 'value'}) == ({}, 'value')
    assert await push.async_push({'key': 'any'}) == ({}, {'key': 'any'})
    assert await push.async_push({'data': 'value', 'header': 'head'}) == ({'header': 'head'}, 'value')


def test_parse_envelope_for_doc():
    class _Dummy(PushBase):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        @parse_envelope('val')
        def push(self, envelope, payload):
            """Push, push!"""
            return envelope, payload

        @parse_envelope('val')
        async def async_push(self, envelope, payload):
            """Push, push!"""
            return envelope, payload

    assert _Dummy(name='pytest').push.__doc__ == "Push, push!"
    assert _Dummy(name='pytest').async_push.__doc__ == "Push, push!"


@pytest.mark.asyncio
async def test_parse_envelope():
    class _Dummy(PushBase):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        @parse_envelope('key1')
        @parse_envelope('key2')
        def push(self, key1, key2, envelope=None, payload=None):
            """Push, push!"""
            return key1, key2, envelope, payload

        @parse_envelope('key1')
        @parse_envelope('key2')
        async def async_push(self, key1, key2, envelope=None, payload=None):
            """Push, push!"""
            return key1, key2, envelope, payload

    dut = _Dummy(name='pytest')
    assert dut.push(None, None) == (None, None, None, None)
    assert dut.push({}, {}) == (None, None, {}, {})
    assert dut.push({}, {'key': 'value'}) == (None, None, {}, {'key': 'value'})
    assert dut.push({'anykey': 'anyval'}, {}) == (None, None, {'anykey': 'anyval'}, {})
    assert dut.push({'key1': 'value1'}, {}) == ('value1', None, {'key1': 'value1'}, {})
    assert (dut.push({'key1': 'value1', 'key2': 'value2'}, {})
            == ('value1', 'value2', {'key1': 'value1', 'key2': 'value2'}, {}))
    assert (dut.push({'key1': 'value1'}, 'payload')
            == ('value1', None, {'key1': 'value1'}, 'payload'))

    dut = _Dummy(name='pytest')
    assert await dut.async_push(None, None) == (None, None, None, None)
    assert await dut.async_push({}, {}) == (None, None, {}, {})
    assert await dut.async_push({}, {'key': 'value'}) == (None, None, {}, {'key': 'value'})
    assert await dut.async_push({'anykey': 'anyval'}, {}) == (None, None, {'anykey': 'anyval'}, {})
    assert await dut.async_push({'key1': 'value1'}, {}) == ('value1', None, {'key1': 'value1'}, {})
    assert (await dut.async_push({'key1': 'value1', 'key2': 'value2'}, {})
            == ('value1', 'value2', {'key1': 'value1', 'key2': 'value2'}, {}))
    assert (await dut.async_push({'key1': 'value1'}, 'payload')
            == ('value1', None, {'key1': 'value1'}, 'payload'))


def test_parse_envelope_with_parser():
    class _Dummy(PushBase):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        @staticmethod
        def parse_key1(val):
            return 'transformed: {}'.format(val)

        @parse_envelope('key1')
        def push(self, key1, envelope=None, payload=None):
            """Push, push!"""
            return key1, envelope, payload

    dut = _Dummy(name='pytest')
    assert (dut.push({'key1': 'val1'}, 'datadata')
            == ('transformed: val1', {'key1': 'val1'}, 'datadata'))


def test_parse_envelope_with_instance_var():
    class _Dummy(PushBase):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.key1 = 'instance'

        @parse_envelope('key1')
        def push(self, key1, envelope=None, payload=None):
            """Push, push!"""
            return key1, envelope, payload

    dut = _Dummy(name='pytest')
    assert (dut.push(None, 'datadata')
            == ('instance', None, 'datadata'))


@pytest.mark.asyncio
async def test_enveloped_parse_envelope_combination():
    class _Dummy(PushBase):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        @enveloped
        @parse_envelope('key1')
        @parse_envelope('key2')
        def push(self, key1, key2, envelope=None, payload=None):
            """Push, push!"""
            return key1, key2, envelope, payload

        @enveloped
        @parse_envelope('key1')
        @parse_envelope('key2')
        async def async_push(self, key1, key2, envelope=None, payload=None):
            """Push, push!"""
            return key1, key2, envelope, payload

    dut = _Dummy(name='pytest')
    assert (dut.push({'data': 'datadata', 'key1': 'val1'})
            == ('val1', None, {'key1': 'val1'}, 'datadata'))
    assert (dut.push({'data': 'datadata', 'key1': 'val1', 'key2': 'val2'})
            == ('val1', 'val2', {'key1': 'val1', 'key2': 'val2'}, 'datadata'))
    assert (dut.push({'data': 'datadata', 'anykey': 'anyval'})
            == (None, None, {'anykey': 'anyval'}, 'datadata'))

    assert (await dut.async_push({'data': 'datadata', 'key1': 'val1'})
            == ('val1', None, {'key1': 'val1'}, 'datadata'))
    assert (await dut.async_push({'data': 'datadata', 'key1': 'val1', 'key2': 'val2'})
            == ('val1', 'val2', {'key1': 'val1', 'key2': 'val2'}, 'datadata'))
    assert (await dut.async_push({'data': 'datadata', 'anykey': 'anyval'})
            == (None, None, {'anykey': 'anyval'}, 'datadata'))


@pytest.mark.asyncio
async def test_drop_envelope():
    class _Dummy(PushBase):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        @enveloped
        @drop_envelope
        def push(self, payload):
            return payload

        @enveloped
        @drop_envelope
        async def async_push(self, payload):
            return payload

    dut = _Dummy(name='pytest')
    assert dut.push({'data': 'datadata', 'key1': 'val1'}) == 'datadata'

    assert await dut.async_push({'data': 'datadata', 'key1': 'val1'}) == 'datadata'