"""
Probability Evaluation Metrics
File: ml-service/app/evaluation/probability_metrics.py

Implements calibration and scoring metrics for continuous probability predictions:
- Log Loss (Binary Cross-Entropy) with documented clipping
- Brier Score (Mean Squared Error)
- Comprehensive metric aggregator
"""

from typing import List, Dict, Any, Optional, Tuple
import math
import numpy as np

from app.evaluation.classification_metrics import (
    accuracy,
    precision,
    recall,
    f1_score,
    roc_auc,
    confusion_matrix,
)

# Documented probability clipping threshold to prevent log(0)
CLIP_EPSILON = 1e-15


def log_loss(
    y_true: List[int],
    y_pred_proba: List[float],
    eps: float = CLIP_EPSILON,
) -> float:
    """
    Computes Binary Cross-Entropy (Log Loss).
    
    Formula:
        - 1/N * sum [ y_i * log(p_i) + (1 - y_i) * log(1 - p_i) ]
        
    Probabilities are clipped to [eps, 1 - eps] for numerical stability.
    """
    if not y_true:
        return 0.0

    total_loss = 0.0
    N = len(y_true)

    for yt, yp in zip(y_true, y_pred_proba):
        p_clipped = max(eps, min(1.0 - eps, float(yp)))
        if yt == 1:
            total_loss -= math.log(p_clipped)
        else:
            total_loss -= math.log(1.0 - p_clipped)

    return total_loss / N


def brier_score(
    y_true: List[int], y_pred_proba: List[float]
) -> float:
    """
    Computes Brier Score: Mean Squared Error of probability predictions.
    
    Formula:
        1/N * sum (p_i - y_i)^2
    """
    if not y_true:
        return 0.0

    total_sq_err = sum((float(yp) - float(yt)) ** 2 for yt, yp in zip(y_true, y_pred_proba))
    return total_sq_err / len(y_true)


def compute_calibration_bins(
    y_true: List[int],
    y_pred_proba: List[float],
    n_bins: int = 10,
) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Computes Expected Calibration Error (ECE) and reliability diagram bins.
    
    Bins predictions into M equal-width bins in [0, 1]:
        [0, 1/M), [1/M, 2/M), ..., [(M-1)/M, 1.0]
        
    For each bin b:
        - count: number of instances in bin
        - pred_mean: average predicted probability
        - observed_mean: empirical correctness rate
        - abs_error: |pred_mean - observed_mean|
        
    ECE formula:
        sum_{b=1}^M (N_b / N) * |pred_mean_b - observed_mean_b|
        
    Returns:
        (ece, bins_data)
    """
    if not y_true:
        return 0.0, []

    y_arr = np.array(y_true, dtype=np.int32)
    p_arr = np.array(y_pred_proba, dtype=np.float64)
    N = len(y_arr)

    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    bins_data = []
    total_ece = 0.0

    for b in range(n_bins):
        lo = bin_edges[b]
        hi = bin_edges[b + 1]

        if b == n_bins - 1:
            mask = (p_arr >= lo) & (p_arr <= hi)
        else:
            mask = (p_arr >= lo) & (p_arr < hi)

        bin_count = int(np.sum(mask))
        if bin_count > 0:
            pred_mean = float(np.mean(p_arr[mask]))
            true_mean = float(np.mean(y_arr[mask]))
            abs_diff = abs(pred_mean - true_mean)
            total_ece += (bin_count / N) * abs_diff
        else:
            pred_mean = 0.0
            true_mean = 0.0
            abs_diff = 0.0

        bins_data.append({
            "bin_index": b + 1,
            "bin_lower": round(float(lo), 4),
            "bin_upper": round(float(hi), 4),
            "count": bin_count,
            "pred_mean": round(float(pred_mean), 6),
            "observed_mean": round(float(true_mean), 6),
            "calibration_error": round(float(abs_diff), 6),
        })

    return round(float(total_ece), 6), bins_data


def expected_calibration_error(
    y_true: List[int],
    y_pred_proba: List[float],
    n_bins: int = 10,
) -> float:
    """Computes Expected Calibration Error (ECE) across n equal-width bins."""
    ece, _ = compute_calibration_bins(y_true, y_pred_proba, n_bins)
    return ece


def compute_all_metrics(
    y_true: List[int],
    y_pred_proba: List[float],
    threshold: float = 0.5,
    n_bins: int = 10,
) -> Dict[str, Any]:
    """
    Computes the complete suite of classification and probability quality metrics,
    including discrimination (ROC-AUC), scoring (Log Loss, Brier), and calibration (ECE).
    """
    N = len(y_true)
    if N == 0:
        return {
            "n_observations": 0,
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "roc_auc": None,
            "log_loss": 0.0,
            "brier_score": 0.0,
            "ece": 0.0,
            "positive_rate_actual": 0.0,
            "positive_rate_predicted": 0.0,
            "calibration_bins": [],
        }

    n_pos = sum(1 for y in y_true if y == 1)
    n_neg = N - n_pos
    cm = confusion_matrix(y_true, y_pred_proba, threshold)
    pred_pos = cm["tp"] + cm["fp"]
    ece, cal_bins = compute_calibration_bins(y_true, y_pred_proba, n_bins)

    return {
        "n_observations": N,
        "n_positive": n_pos,
        "n_negative": n_neg,
        "positive_rate_actual": round(n_pos / N, 6),
        "positive_rate_predicted": round(pred_pos / N, 6),
        "accuracy": round(accuracy(y_true, y_pred_proba, threshold), 6),
        "precision": round(precision(y_true, y_pred_proba, threshold), 6),
        "recall": round(recall(y_true, y_pred_proba, threshold), 6),
        "f1": round(f1_score(y_true, y_pred_proba, threshold), 6),
        "roc_auc": round(roc_auc(y_true, y_pred_proba), 6) if roc_auc(y_true, y_pred_proba) is not None else None,
        "log_loss": round(log_loss(y_true, y_pred_proba), 6),
        "brier_score": round(brier_score(y_true, y_pred_proba), 6),
        "ece": ece,
        "confusion_matrix": cm,
        "calibration_bins": cal_bins,
    }
