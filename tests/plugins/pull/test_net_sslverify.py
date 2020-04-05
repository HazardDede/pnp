from datetime import datetime

from pnp.plugins.pull.net import SSLVerify


def test_google_cert():
    # The assumption is that google never misses the time window for
    # re-issuing

    dut = SSLVerify('www.google.com', name='pytest')
    res = dut.poll()

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
