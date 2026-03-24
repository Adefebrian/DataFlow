import time
from functools import wraps
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    def __init__(self):
        self.counters: dict[str, int] = {}
        self.histograms: dict[str, list[float]] = {}
        self.gauges: dict[str, float] = {}

    def increment(self, name: str, value: int = 1):
        self.counters[name] = self.counters.get(name, 0) + value

    def record_time(self, name: str, duration: float):
        if name not in self.histograms:
            self.histograms[name] = []
        self.histograms[name].append(duration)

    def set_gauge(self, name: str, value: float):
        self.gauges[name] = value

    def get_stats(self) -> dict[str, Any]:
        stats = {
            "counters": self.counters.copy(),
            "gauges": self.gauges.copy(),
            "histograms": {},
        }

        for name, values in self.histograms.items():
            if values:
                sorted_values = sorted(values)
                stats["histograms"][name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "p50": sorted_values[len(sorted_values) // 2],
                    "p95": sorted_values[int(len(sorted_values) * 0.95)],
                    "p99": sorted_values[int(len(sorted_values) * 0.99)],
                }

        return stats

    def reset(self):
        self.counters.clear()
        self.histograms.clear()
        self.gauges.clear()


metrics = MetricsCollector()


def track_time(metric_name: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                metrics.record_time(metric_name, duration)
                metrics.increment(f"{metric_name}.success")

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                metrics.record_time(metric_name, duration)
                metrics.increment(f"{metric_name}.success")

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


import asyncio
