# src/detector.py
import time
import math
from collections import deque

class EWMADetector:
    def __init__(self, alpha=0.2, warmup=10):
        self.alpha = alpha
        self.mean = None
        self.var = None
        self.count = 0
        self.warmup = warmup
        self.history = deque(maxlen=500)

    def update(self, value):
        """Update EWMA mean and variance online."""
        self.count += 1
        self.history.append(value)
        if self.mean is None:
            self.mean = value
            self.var = 0.0
            return
        self.mean = self.alpha * value + (1 - self.alpha) * self.mean
        # simple EWMA variance
        diff = value - self.mean
        self.var = self.alpha * (diff * diff) + (1 - self.alpha) * (self.var if self.var is not None else 0.0)

    def zscore(self, value):
        std = math.sqrt(self.var) if self.var and self.var>0 else 1.0
        return (value - self.mean) / std if self.mean is not None else 0.0

class CompositeScorer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.det_req = EWMADetector(alpha=0.1)
        self.det_ips = EWMADetector(alpha=0.1)
        self.det_path = EWMADetector(alpha=0.1)
        self.det_ua = EWMADetector(alpha=0.1)

    def score(self, feat):
        self.det_req.update(feat['requests'])
        self.det_ips.update(feat['unique_ips'])
        self.det_path.update(feat['top_path_count'])
        self.det_ua.update(feat['ua_entropy'])

        z_req = self.det_req.zscore(feat['requests'])
        z_ips = self.det_ips.zscore(feat['unique_ips'])
        z_path = self.det_path.zscore(feat['top_path_count'])
        z_ua = self.det_ua.zscore(feat['ua_entropy'])

        # simple weighted composite score
        contributions = {
            "requests": max(0, z_req),
            "unique_ips": max(0, z_ips),
            "top_path_count": max(0, z_path),
            "ua_entropy": max(0, z_ua)
        }
        # normalize and score 0-100
        raw = 0.5*contributions['requests'] + 0.3*contributions['unique_ips'] + 0.1*contributions['top_path_count'] + 0.1*contributions['ua_entropy']
        score = max(0.0, min(100.0, raw * 10.0))  # scale factor
        return {
            "score": score,
            "z": {"requests": z_req, "unique_ips": z_ips, "top_path_count": z_path, "ua_entropy": z_ua},
            "contributions": contributions
        }

    def is_alert(self, score_obj):
        cfg = self.cfg
        thresh = cfg.get("alert_zscore_threshold", 4.0)
        if score_obj['z']['requests'] >= thresh or score_obj['z']['unique_ips'] >= thresh:
            return True
        if score_obj['score'] >= cfg.get("min_score", 60) and score_obj['z']['requests'] > 2.0:
            return True
        return False
