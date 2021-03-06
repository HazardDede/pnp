import time
from functools import partial
from multiprocessing import Process


def run_engine(engine, tasks):
    t = Process(target=partial(engine.start, tasks=tasks))
    try:
        t.start()
        time.sleep(1)
        engine._stop()
        t.join(timeout=2)
    finally:
        if t.is_alive():
            t.terminate()
            assert False
