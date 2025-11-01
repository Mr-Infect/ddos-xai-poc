# src/window.py
import time
from collections import deque, Counter
from math import log2

class SlidingWindow:
    def __init__(self, seconds):
        self.seconds = seconds
        self.q = deque()
        self.ip_counter = Counter()
        self.path_counter = Counter()
        self.ua_counter = Counter()
        self.total = 0

    def add(self, ts, src_ip, path, ua):
        self.q.append((ts, src_ip, path, ua))
        self.ip_counter[src_ip] += 1
        self.path_counter[path] += 1
        if ua:
            self.ua_counter[ua] += 1
        self.total += 1
        self.evict(ts)

    def evict(self, now=None):
        if now is None:
            now = time.time()
        while self.q and now - self.q[0][0] > self.seconds:
            _, ip, path, ua = self.q.popleft()
            self.ip_counter[ip] -= 1
            if self.ip_counter[ip] <= 0:
                del self.ip_counter[ip]
            self.path_counter[path] -= 1
            if self.path_counter[path] <= 0:
                del self.path_counter[path]
            if ua:
                self.ua_counter[ua] -= 1
                if self.ua_counter[ua] <= 0:
                    del self.ua_counter[ua]
            self.total -= 1

    def features(self):
        # returns dict of features
        reqs = max(0, self.total)
        unique_ips = len(self.ip_counter)
        top_path_count = max(self.path_counter.values()) if self.path_counter else 0
        ua_entropy = self._entropy(self.ua_counter)
        return {
            "requests": reqs,
            "unique_ips": unique_ips,
            "top_path_count": top_path_count,
            "ua_entropy": ua_entropy
        }

    @staticmethod
    def _entropy(counter):
        total = sum(counter.values())
        if total == 0:
            return 0.0
        ent = 0.0
        for v in counter.values():
            p = v/total
            ent -= p * (log2(p) if p>0 else 0)
        return ent
