from . import UserDefinedFunction


class Counter(UserDefinedFunction):
    def __init__(self, init=0, **kwargs):
        super().__init__(**kwargs)
        self.cnt = int(init)
        if self.cnt < 0:
            self.cnt = 0

    def action(self):
        try:
            return self.cnt
        finally:
            self.cnt += 1
