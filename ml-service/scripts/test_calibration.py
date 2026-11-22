"""
Compute Calibration (ECE and Reliability Bins) for Protocol A and Protocol B
"""
import os
import json
import csv
import math
import numpy as np
from collections import defaultdict

ML_SERVICE_DIR = r"N:\adaptive-study-planner\ml-service"
REPORTS_DIR = os.path.join(ML_SERVICE_DIR, "data", "reports", "bkt")
MODELS_DIR = os.path.join(ML_SERVICE_DIR, "models", "artifacts")
SPLITS_DIR = os.path.join(ML_SERVICE_DIR, "data", "splits")

def compute_ece_and_bins(y_true, y_pred_proba, n_bins=10):
    """
    Computes Expected Calibration Error (ECE) and reliability diagram bins.
    Bins are equal-width in [0, 1].
    """
    y_true = np.array(y_true, dtype=np.int32)
    y_pred = np.array(y_pred_proba, dtype=np.float64)
    N = len(y_true)
    if N == 0:
        return 0.0, []

    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    bins_data = []
    total_ece = 0.0

    for b in range(n_bins):
        lo = bin_edges[b]
        hi = bin_edges[b + 1]
        
        # Include upper boundary on the last bin
        if b == n_bins - 1:
            mask = (y_pred >= lo) & (y_pred <= hi)
        else:
            mask = (y_pred >= lo) & (y_pred < hi)

        bin_count = int(np.sum(mask))
        if bin_count > 0:
            pred_mean = float(np.mean(y_pred[mask]))
            true_mean = float(np.mean(y_true[mask]))
            abs_diff = abs(pred_mean - true_mean)
            weighted_diff = (bin_count / N) * abs_diff
            total_ece += weighted_diff
        else:
            pred_mean = 0.0
            true_mean = 0.0
            abs_diff = 0.0

        bins_data.append({
            "bin_index": b + 1,
            "bin_range": [round(lo, 2), round(hi, 2)],
            "count": bin_count,
            "pred_mean": round(pred_mean, 4),
            "observed_mean": round(true_mean, 4),
            "abs_error": round(abs_diff, 4),
        })

    return round(float(total_ece), 6), bins_data

if __name__ == "__main__":
    # Test with synthetic example
    y_true = [1, 1, 0, 0, 1, 0, 1, 1]
    y_pred = [0.9, 0.8, 0.2, 0.1, 0.6, 0.4, 0.7, 0.65]
    ece, bins = compute_ece_and_bins(y_true, y_pred, n_bins=5)
    print("Synthetic ECE:", ece)
    print("Synthetic Bins:", json.dumps(bins, indent=2))
