"""
Baseline Models for Knowledge Tracing Comparison
File: ml-service/app/evaluation/baselines.py

Implements three required non-KT baseline models:
1. MajorityClassBaseline: Predicts the majority class (1.0 or 0.0) from training data.
2. GlobalCorrectnessRateBaseline: Predicts the global training correctness rate.
3. PerSkillCorrectnessRateBaseline: Predicts the per-skill training correctness rate.

All baselines strictly use training data ONLY to prevent leakage.
"""

from typing import List, Dict, Any, Optional
from collections import Counter, defaultdict


class MajorityClassBaseline:
    """
    Predicts the majority class from training data.
    
    To avoid infinite/extreme Log Loss from assigning hard 0.0 or 1.0 probabilities
    to probabilistic calibration metrics, the baseline uses Laplace smoothing on
    the training class distribution by default:
        P(C=1) = (N_correct + 1) / (N_total + 2)
        
    If hard=True is specified, it returns discrete 1.0 or 0.0.
    """
    def __init__(self, smoothed: bool = True):
        self.smoothed = smoothed
        self.majority_label: int = 1
        self.majority_prob_smoothed: float = 0.5
        self.majority_prob_hard: float = 1.0

    def fit(self, train_labels: List[int]) -> "MajorityClassBaseline":
        if not train_labels:
            self.majority_label = 1
            self.majority_prob_smoothed = 0.5
            self.majority_prob_hard = 1.0
            return self

        counts = Counter(train_labels)
        n_pos = counts.get(1, 0)
        n_neg = counts.get(0, 0)
        n_total = len(train_labels)

        self.majority_label = 1 if n_pos >= n_neg else 0
        self.majority_prob_hard = 1.0 if self.majority_label == 1 else 0.0
        # Laplace smoothing: (N_pos + 1) / (N_total + 2)
        self.majority_prob_smoothed = (n_pos + 1.0) / (n_total + 2.0)
        return self

    def predict(self, n: int, hard: Optional[bool] = None) -> List[float]:
        use_hard = self.smoothed is False if hard is None else hard
        val = self.majority_prob_hard if use_hard else self.majority_prob_smoothed
        return [val] * n

    @property
    def prediction_probability(self) -> float:
        return self.majority_prob_hard if not self.smoothed else self.majority_prob_smoothed


class GlobalCorrectnessRateBaseline:
    """
    Predicts the overall proportion of correct answers in training data.
    Uses Laplace smoothing to prevent 0.0 or 1.0 probabilities on small/skewed samples:
        P(C=1) = (sum(y_train) + 1) / (N_train + 2)
    """
    def __init__(self):
        self.global_rate: float = 0.5

    def fit(self, train_labels: List[int]) -> "GlobalCorrectnessRateBaseline":
        if not train_labels:
            self.global_rate = 0.5
            return self
        n_corr = sum(train_labels)
        n_tot = len(train_labels)
        # Laplace smoothing
        self.global_rate = (n_corr + 1.0) / (n_tot + 2.0)
        return self

    def predict(self, n: int) -> List[float]:
        return [self.global_rate] * n


class PerSkillCorrectnessRateBaseline:
    """
    Predicts the historical correctness rate for each skill in training data.
    Uses Laplace smoothing per skill:
        P(C=1 | skill) = (N_{correct, skill} + 1) / (N_{total, skill} + 2)
    Falls back to the Laplace-smoothed global training rate for unseen skills.
    """
    def __init__(self):
        self.skill_rates: Dict[str, float] = {}
        self.global_rate: float = 0.5

    def fit(self, train_records: List[Dict[str, Any]]) -> "PerSkillCorrectnessRateBaseline":
        if not train_records:
            return self

        skill_correct = defaultdict(int)
        skill_total = defaultdict(int)
        total_correct = 0

        for r in train_records:
            sid = str(r["skill_id"])
            corr = int(r["correct"])
            skill_correct[sid] += corr
            skill_total[sid] += 1
            total_correct += corr

        # Global Laplace-smoothed fallback rate
        self.global_rate = (total_correct + 1.0) / (len(train_records) + 2.0)

        # Per-skill Laplace-smoothed rate
        self.skill_rates = {
            sid: (skill_correct[sid] + 1.0) / (skill_total[sid] + 2.0)
            for sid in skill_total
        }
        return self

    def predict_single(self, skill_id: Any) -> float:
        return self.skill_rates.get(str(skill_id), self.global_rate)

    def predict_sequence(self, records: List[Dict[str, Any]]) -> List[float]:
        return [self.predict_single(r.get("skill_id", "")) for r in records]


def fit_baselines(train_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Fits all three baselines using training records only."""
    train_labels = [int(r["correct"]) for r in train_records]

    maj_smoothed = MajorityClassBaseline(smoothed=True).fit(train_labels)
    maj_hard = MajorityClassBaseline(smoothed=False).fit(train_labels)
    glob = GlobalCorrectnessRateBaseline().fit(train_labels)
    skill = PerSkillCorrectnessRateBaseline().fit(train_records)

    return {
        "majority_class": maj_smoothed,
        "majority_class_hard": maj_hard,
        "global_correctness_rate": glob,
        "per_skill_rate": skill,
    }
