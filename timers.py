from __future__ import annotations

from time import perf_counter
from collections import defaultdict
from logger import logger


class Timer:
    val: float = 0.0
    cnt: int = 0
    name: str | None

    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.val -= perf_counter()
        return self

    def __exit__(self, *args):
        self.val += perf_counter()
        self.cnt += 1
        if self.name is not None:
            logger.info(f"{self.name} {self}.")

    def __repr__(self):
        return pprint(self.val / self.cnt)

    def reset(self):
        self.val = 0


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
