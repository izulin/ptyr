from __future__ import annotations

from time import perf_counter
from collections import defaultdict


class Timer:
    val: float = 0.0

    def __enter__(self):
        self.val -= perf_counter()
        return self

    def __exit__(self, *args):
        self.val += perf_counter()

    def __repr__(self):
        return f"{self.val:.3f}"

    def reset(self):
        self.val = 0


TIMERS: dict[str, Timer] = defaultdict(Timer)
