"""
Classification Evaluation Metrics
File: ml-service/app/evaluation/classification_metrics.py

Implements pure Python/NumPy classification metrics for binary correctness prediction:
- Accuracy, Precision, Recall, F1 Score
- Area Under the ROC Curve (ROC-AUC) via trapezoidal integration
- Confusion Matrix
"""

from typing import List, Dict, Any, Optional
import numpy as np


def confusion_matrix(
    y_true: List[int], y_pred_proba: List[float], threshold: float = 0.5
) -> Dict[str, int]:
    """
    Computes confusion matrix at a decision threshold.
    Returns: {"tp": int, "fp": int, "tn": int, "fn": int}
    """
    tp = fp = tn = fn = 0
    for yt, yp in zip(y_true, y_pred_proba):
        pred_bin = 1 if yp >= threshold else 0
        if yt == 1 and pred_bin == 1:
            tp += 1
        elif yt == 0 and pred_bin == 1:
            fp += 1
        elif yt == 0 and pred_bin == 0:
            tn += 1
        else:
            fn += 1
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn}


def accuracy(
    y_true: List[int], y_pred_proba: List[float], threshold: float = 0.5
) -> float:
    """
    Computes classification accuracy: (TP + TN) / Total.
    """
    if not y_true:
        return 0.0
    cm = confusion_matrix(y_true, y_pred_proba, threshold)
    total = cm["tp"] + cm["tn"] + cm["fp"] + cm["fn"]
    return (cm["tp"] + cm["tn"]) / total if total > 0 else 0.0


def precision(
    y_true: List[int], y_pred_proba: List[float], threshold: float = 0.5
) -> float:
    """
    Computes precision: TP / (TP + FP).
    Returns 0.0 if TP + FP == 0 (zero-division protection).
    """
    cm = confusion_matrix(y_true, y_pred_proba, threshold)
    denom = cm["tp"] + cm["fp"]
    return cm["tp"] / denom if denom > 0 else 0.0


def recall(
    y_true: List[int], y_pred_proba: List[float], threshold: float = 0.5
) -> float:
    """
    Computes recall (true positive rate): TP / (TP + FN).
    Returns 0.0 if TP + FN == 0 (zero-division protection).
    """
    cm = confusion_matrix(y_true, y_pred_proba, threshold)
    denom = cm["tp"] + cm["fn"]
    return cm["tp"] / denom if denom > 0 else 0.0


def f1_score(
    y_true: List[int], y_pred_proba: List[float], threshold: float = 0.5
) -> float:
    """
    Computes F1 score: 2 * (Precision * Recall) / (Precision + Recall).
    Returns 0.0 if Precision + Recall == 0.
    """
    p = precision(y_true, y_pred_proba, threshold)
    r = recall(y_true, y_pred_proba, threshold)
    denom = p + r
    return (2.0 * p * r) / denom if denom > 0 else 0.0


def roc_auc(
    y_true: List[int], y_pred_proba: List[float]
) -> Optional[float]:
    """
    Computes Area Under the Receiver Operating Characteristic Curve (ROC-AUC)
    using the trapezoidal rule / Mann-Whitney U rank statistic.
    
    Returns None if y_true contains only a single class (AUC is undefined).
    """
    if not y_true or len(y_true) != len(y_pred_proba):
        return None

    y_arr = np.array(y_true, dtype=np.int32)
    p_arr = np.array(y_pred_proba, dtype=np.float64)

    n_pos = int(np.sum(y_arr == 1))
    n_neg = int(np.sum(y_arr == 0))

    if n_pos == 0 or n_neg == 0:
        return None

    # Sort descending by score; ties handled by average rank
    # argsort on negative scores gives descending order
    order = np.argsort(-p_arr, kind="mergesort")
    sorted_y = y_arr[order]
    sorted_p = p_arr[order]

    # Compute TPR and FPR at distinct threshold points
    tps = np.cumsum(sorted_y == 1, dtype=np.float64)
    fps = np.cumsum(sorted_y == 0, dtype=np.float64)

    # Find indices where score changes to avoid trapezoid distortion on ties
    distinct_mask = np.r_[sorted_p[1:] != sorted_p[:-1], True]
    distinct_indices = np.where(distinct_mask)[0]

    tpr = np.r_[0.0, tps[distinct_indices] / n_pos]
    fpr = np.r_[0.0, fps[distinct_indices] / n_neg]

    # Trapezoidal integration using pure arithmetic (immune to numpy version changes)
    auc = float(np.sum((fpr[1:] - fpr[:-1]) * (tpr[1:] + tpr[:-1]) / 2.0))
    return max(0.0, min(1.0, auc))
