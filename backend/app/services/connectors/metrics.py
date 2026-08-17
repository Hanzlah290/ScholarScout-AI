import time
from typing import Dict, Any, List

class RequestMetricsTracker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.total_requests: int = 0
        self.unique_urls: set = set()
        self.duplicate_requests: int = 0
        self.failed_requests: int = 0
        self.status_codes: Dict[int, int] = {}
        self.bytes_downloaded: int = 0
        self.latencies: List[float] = []

    def record_request(self, url: str, status_code: int, response_size: int, latency_sec: float, failed: bool = False):
        self.total_requests += 1
        if url in self.unique_urls:
            self.duplicate_requests += 1
        else:
            self.unique_urls.add(url)

        if failed:
            self.failed_requests += 1

        self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1
        self.bytes_downloaded += response_size
        self.latencies.append(latency_sec)

    def get_report(self) -> Dict[str, Any]:
        latencies_sorted = sorted(self.latencies) if self.latencies else [0.0]
        n = len(latencies_sorted)
        p50 = latencies_sorted[int(n * 0.50)] if n > 0 else 0.0
        p95 = latencies_sorted[int(n * 0.95)] if n > 0 else 0.0
        avg_latency = sum(self.latencies) / n if n > 0 else 0.0

        return {
            "total_requests": self.total_requests,
            "unique_urls": len(self.unique_urls),
            "duplicate_requests": self.duplicate_requests,
            "failed_requests": self.failed_requests,
            "status_codes": self.status_codes,
            "bytes_downloaded": self.bytes_downloaded,
            "avg_latency_sec": round(avg_latency, 3),
            "p50_latency_sec": round(p50, 3),
            "p95_latency_sec": round(p95, 3),
        }

metrics_tracker = RequestMetricsTracker()