import logging
import os
import sys

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=LOG_LEVEL)


def main():
    if len(sys.argv) != 2:
        raise ValueError("Expecting exactly one argument (zway request url to test)")
    from pnp.plugins.pull.zway import ZwayPoll

    def run(url):
        zway = ZwayPoll(url=url, name='zway-test', interval='1s')

        def on_payload(plugin, payload):
            logging.info("Return from Z-Way API: " + str(payload))
            zway.stop()
        zway.on_payload = on_payload
        zway.pull()

    run(sys.argv[1])


if __name__ == '__main__':
    main()
