from __future__ import annotations

from collections import defaultdict
from time import perf_counter

from logger import logger


class Timer:
    val: float = 0.0
    clicks: int = 0
    name: str | None
    enters: int = 0

    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.val -= perf_counter()
        self.enters += 1
        return self

    def __exit__(self, *args):
        self.val += perf_counter()
        if self.name is not None:
            self.click()
            logger.info(f"{self.name} {self}.")

    def __repr__(self):
        if self.enters != self.clicks and self.enters > 0:
            return (
                pprint(self.val / self.clicks)
                + f" / {self.enters / self.clicks:.1f} = "
                + pprint(self.val / self.enters)
            )
        else:
            return pprint(self.val / self.clicks)

    def click(self):
        self.clicks += 1

    def reset(self):
        self.val = 0
        self.clicks = 0
        self.enters = 0


def pprint(t):
    if t >= 1:
        scale = 1
        unit = "s"
    elif t >= 1e-3:
        scale = 1e3
        unit = "ms"
    elif t >= 1e-6:
        scale = 1e6
        unit = "μs"
    else:
        scale = 1e9
        unit = "ns"
    return f"{scale * t:.1f}{unit}"


TIMERS: dict[str, Timer] = defaultdict(Timer)


def timeit(name: str):
    def _timeit(fun):
        def wrapped(*args, **kwargs):
            with TIMERS[name]:
                return fun(*args, **kwargs)

        return wrapped

    return _timeit
