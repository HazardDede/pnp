from mock import patch

from pnp.plugins.pull.traffic import DeutscheBahn

OUTPUT = [{
    'arrival': '15:09',
    'canceled': False,
    'delay': {'delay_arrival': 0, 'delay_departure': 4},
    'departure': '09:01',
    'details': 'http://mobile.bahn.de/bin/mobil/query.exe/dox?ld=43232&n=1&i=n8.01490232.1571295344&rt=1&use_realtime_filter=1&co=C0-0&vca&HWAI=CONNECTION$C0-0!details=opened!detailsVerbund=opened!&',
    'ontime': False,
    'price': 153.0,
    'products': ['ICE'],
    'time': '6:04',
    'transfers': 1
 },
 {
    'arrival': '15:39',
    'canceled': False,
    'departure': '09:28',
    'details': 'http://mobile.bahn.de/bin/mobil/query.exe/dox?ld=43232&n=1&i=n8.01490232.1571295344&rt=1&use_realtime_filter=1&co=C0-1&vca&HWAI=CONNECTION$C0-1!details=opened!detailsVerbund=opened!&',
    'ontime': True,
    'price': 153.0,
    'products': ['ICE'],
    'time': '6:11',
    'transfers': 0
 }]


@patch('pnp.plugins.pull.traffic.Schiene')
def test_deutsche_bahn_poll(mock_schiene):
    mock_schiene.return_value.connections.return_value = OUTPUT

    dut = DeutscheBahn(name='pytest', origin='origin', destination='destination')
    res = dut.poll()
    assert res == [{
        'departure': '09:01', 'arrival': '15:09', 'travel_time': '6:04',
        'products': ['ICE'], 'transfers': 1, 'canceled': False, 'delayed': True,
        'delay_departure': 4, 'delay_arrival': 0
    }, {
        'departure': '09:28', 'arrival': '15:39', 'travel_time': '6:11',
        'products': ['ICE'], 'transfers': 0, 'canceled': False, 'delayed': False,
        'delay_departure': 0, 'delay_arrival': 0
    }]
