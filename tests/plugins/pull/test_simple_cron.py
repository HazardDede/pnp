from pnp.plugins.pull import simple


def test_cron_every_minute():
    res = list()
    def on_payload(sender, payload):
        res.append(payload)

    dut = simple.Cron(expressions='*/1 * * * * every minute', name='pytest')
    dut.on_payload = on_payload

    dut.poll()
    dut.poll()
    dut.poll()

    assert len(res) == 3
    assert res[0] == dict(data='every minute')
