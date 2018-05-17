import sys
import time

from . import PullBase


class Count(PullBase):

    def __init__(self, from_cnt=0, to_cnt=None, wait=5, **kwargs):
        super().__init__(**kwargs)
        self.from_cnt = from_cnt
        self.to_cnt = to_cnt
        self.wait = wait

    def pull(self):
        for i in range(self.from_cnt, self.to_cnt or sys.maxsize):
            self.notify(i)
            if self.stopped:
                break
            time.sleep(self.wait)
