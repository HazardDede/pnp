net.Speedtest
^^^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.net.Speedtest   poll   speedtest    0.25.0
================================ ====== ============ ========

**Description**

Performs a speedtest of your internet connection using `speedtest.net <https://www.speedtest.net/>`_

**Arguments**

No arguments

**Result**

.. code-block:: json

    {
      "download_speed_bps": 13815345.098080076,
      "download_speed_mbps": 13.82,
      "upload_speed_bps": 1633087.176468341,
      "upload_speed_mbps": 1.63,
      "ping_latency": 19.933,
      "result_image": "http://www.speedtest.net/result/10049630297.png",
      "server": {
        "name": "Deutsche Telekom",
        "host": "ham.wsqm.telekom-dienste.de:8080",
        "location": {
          "city": "Hamburg",
          "country": "Germany",
          "lat": "53.5653",
          "lon": "10.0014"
        }
      },
      "client": {
        "isp": "Vodafone DSL",
        "rating": "3.7"
      }
    }

**Example**

.. literalinclude:: ../code-samples/plugins/pull/net.Speedtest/example.yaml
   :language: YAML