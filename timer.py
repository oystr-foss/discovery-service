from typing import Optional
from datetime import datetime


class Timer(object):
    def __init__(self):
        self.start: Optional[datetime] = None
        self.end: Optional[datetime] = None

    def diff(self, reset: bool = True):
        if self.start and self.end:
            total = (self.end - self.start).seconds
            if reset:
                self.start = None
                self.end = None

            return total
        return 0
