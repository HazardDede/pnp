from mock import patch

from pnp.plugins.pull.net import Speedtest

RESPONSE_MOCK = {
  'download': 8889157.466220528,
  'upload': 749897.4006368214,
  'ping': 37.079,
  'server': {
    'url': 'http://ham.wsqm.telekom-dienste.de:8080/speedtest/upload.php',
    'lat': '53.5653',
    'lon': '10.0014',
    'name': 'Hamburg',
    'country': 'Germany',
    'cc': 'DE',
    'sponsor': 'Deutsche Telekom',
    'id': '31469',
    'host': 'ham.wsqm.telekom-dienste.de:8080',
    'd': 3.642779142765639,
    'latency': 37.079
  },
  'timestamp': '2020-09-08T12:24:42.606125Z',
  'bytes_sent': 966656,
  'bytes_received': 11151660,
  'share': 'http://www.speedtest.net/result/12045869306.png',
  'client': {
    'ip': '42.42.42.42',
    'lat': '42.42',
    'lon': '42.42',
    'isp': 'Telekom DSL',
    'isprating': '5.0',
    'rating': '0',
    'ispdlavg': '0',
    'ispulavg': '0',
    'loggedin': '0',
    'country': 'DE'
  }
}


@patch("speedtest.Speedtest")
def test_poll_for_smoke(speedtest_mock):
    speedtest_mock.return_value.results.dict.return_value = RESPONSE_MOCK

    dut = Speedtest(name='pytest')
    res = dut._poll()

    assert res == {
        'download_speed_bps': 8889157.466220528,
        'download_speed_mbps': 8.89,
        'upload_speed_bps': 749897.4006368214,
        'upload_speed_mbps': 0.75,
        'ping_latency': 37.079,
        'result_image': 'http://www.speedtest.net/result/12045869306.png',
        'server': {
            'name': 'Deutsche Telekom',  # The sponsor of the host
            'host': 'ham.wsqm.telekom-dienste.de:8080',  # The host name
            'location': {
                'city': 'Hamburg',
                'country': 'Germany',
                'lat': '53.5653',
                'lon': '10.0014'
            }
        },
        'client': {
            'isp': 'Telekom DSL',  # Your Internet service provider
            'rating': '5.0'  # The rating of your isp
        }
    }
