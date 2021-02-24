from datetime import datetime

import pytest

from pnp.plugins.pull.net import SSLVerify


@pytest.mark.asyncio
async def test_poll_google_cert():
    # The assumption is that google never misses the time window for
    # re-issuing

    dut = SSLVerify('www.google.com', name='pytest')
    res = await dut.poll()

    assert isinstance(res, dict)
    assert res['host'] == 'www.google.com'
    assert isinstance(res['payload'], dict)
    payload = res['payload']
    assert 'expires_days' in payload
    assert isinstance(payload['expires_days'], int)
    assert 'expires_at' in payload
    assert isinstance(payload['expires_at'], datetime)
    assert 'expired' in payload
    assert isinstance(payload['expired'], bool)


def test_repr():
    dut = SSLVerify('www.google.com', name='pytest')
    assert repr(dut) == "SSLVerify(host='www.google.com', interval=60, is_cron=False, name='pytest', timeout=3.0)"
