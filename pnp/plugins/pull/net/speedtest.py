"""Pull: net.Speedtest."""

import speedtest
from glom import glom

from pnp.plugins.pull import SyncPolling
from pnp.typing import Payload
from pnp.utils import bps_mbps


__EXTRA__ = 'speedtest'


OUTPUT_SPEC = {
    'download_speed_bps': 'download',  # in Bits/s
    'download_speed_mbps': ('download', bps_mbps),  # in Megabits/s
    'upload_speed_bps': 'upload',  # in Bits/s
    'upload_speed_mbps': ('upload', bps_mbps),  # in Bits/s
    'ping_latency': 'ping',  # in ms
    'result_image': 'share',  # Image provided by speedtest.net to share
    'server': {
        'name': 'server.sponsor',  # The sponsor of the host
        'host': 'server.host',  # The host name
        'location': {
            'city': 'server.name',
            'country': 'server.country',
            'lat': 'server.lat',
            'lon': 'server.lon'
        }
    },
    'client': {
        'isp': 'client.isp',  # Your Internet service provider
        'rating': 'client.isprating'  # The rating of your isp
    }
}


class Speedtest(SyncPolling):
    """
    Periodically tests your real internet download / upload speed as well as the ping latency.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#net-speedtest
    """

    def _poll(self) -> Payload:
        client = speedtest.Speedtest()
        client.get_servers()
        client.get_best_server()
        client.download(threads=None)
        client.upload(threads=None)
        client.results.share()

        res = client.results.dict()
        return glom(res, OUTPUT_SPEC)
