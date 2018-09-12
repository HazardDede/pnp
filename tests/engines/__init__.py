import time
from functools import partial
from multiprocessing import Process


def run_engine(engine, tasks):
    t = Process(target=partial(engine.run, tasks=tasks))
    try:
        t.start()
        time.sleep(1)
        engine.stop()
        t.join(timeout=2)
    finally:
        if t.is_alive():
            t.terminate()
            assert False
