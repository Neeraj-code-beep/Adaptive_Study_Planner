"""
Comprehensive Automated Unit Tests for Bayesian Knowledge Tracing (BKT)
File: ml-service/tests/test_bkt.py

Tests verify:
1. Mathematical correctness against manual hand-calculations
2. Sequential inference and state isolation
3. Baum-Welch (EM) estimation mechanics
4. Classification and probability evaluation metrics
5. Non-KT baselines
"""

import unittest
import math
import os
import sys

# Ensure ml-service root is in sys.path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
ML_SERVICE_DIR = os.path.dirname(TEST_DIR)
if ML_SERVICE_DIR not in sys.path:
    sys.path.insert(0, ML_SERVICE_DIR)

import numpy as np

from app.knowledge_tracing.bkt.exceptions import (
    BKTError,
    InvalidParameterError,
    NumericalInstabilityError,
    InsufficientDataError,
)
from app.knowledge_tracing.bkt.parameters import (
    BKTParameters,
    ParameterBounds,
    SkillParameters,
    clamp_parameters_to_bounds,
)
from app.knowledge_tracing.bkt.model import (
    predict_correct_probability,
    posterior_learned_given_correct,
    posterior_learned_given_incorrect,
    apply_learning_transition,
    update_mastery,
)
from app.knowledge_tracing.bkt.inference import (
    predict_student_skill_sequence,
    predict_student_all_skills,
    initialize_student_from_history,
)
from app.knowledge_tracing.bkt.em import (
    _build_hmm_matrices,
    scaled_forward,
    scaled_backward,
    e_step_single_sequence,
    m_step,
    fit_skill_parameters,
    fit_all_skills,
)
from app.evaluation.classification_metrics import (
    accuracy,
    precision,
    recall,
    f1_score,
    roc_auc,
    confusion_matrix,
)
from app.evaluation.probability_metrics import (
    log_loss,
    brier_score,
    compute_all_metrics,
)
from app.evaluation.baselines import (
    MajorityClassBaseline,
    GlobalCorrectnessRateBaseline,
    PerSkillCorrectnessRateBaseline,
    fit_baselines,
)


class TestBKTMathematics(unittest.TestCase):
    """Verifies mathematical updates against independently calculated hand examples."""

    def setUp(self):
        # Known test parameters:
        # L0 = 0.20, T = 0.15, G = 0.25, S = 0.10
        self.p_init = 0.20
        self.p_learn = 0.15
        self.p_guess = 0.25
        self.p_slip = 0.10

    def test_predict_correct_probability(self):
        """
        P(C=1) = p * (1 - S) + (1 - p) * G
        = 0.20 * 0.90 + 0.80 * 0.25 = 0.18 + 0.20 = 0.38
        """
        pred = predict_correct_probability(self.p_init, self.p_guess, self.p_slip)
        self.assertAlmostEqual(pred, 0.38, places=6)

    def test_posterior_learned_given_correct(self):
        """
        P(L | C=1) = [p * (1 - S)] / P(C=1)
        = 0.18 / 0.38 = 9/19 ≈ 0.4736842
        """
        post = posterior_learned_given_correct(self.p_init, self.p_guess, self.p_slip)
        self.assertAlmostEqual(post, 9.0 / 19.0, places=6)

    def test_posterior_learned_given_incorrect(self):
        """
        P(L | C=0) = [p * S] / P(C=0)
        Numerator = 0.20 * 0.10 = 0.02
        P(C=0) = 1 - 0.38 = 0.62 (or 0.20*0.10 + 0.80*0.75 = 0.02 + 0.60 = 0.62)
        P(L | C=0) = 0.02 / 0.62 = 1/31 ≈ 0.032258
        """
        post = posterior_learned_given_incorrect(self.p_init, self.p_guess, self.p_slip)
        self.assertAlmostEqual(post, 1.0 / 31.0, places=6)

    def test_learning_transition(self):
        """
        P(L_next) = P(L|obs) + (1 - P(L|obs)) * T
        For post = 9/19:
        P(L_next) = 9/19 + (10/19) * 0.15 = 0.473684 + 0.078947 = 0.5526315
        """
        post = 9.0 / 19.0
        p_next = apply_learning_transition(post, self.p_learn)
        expected = post + (1.0 - post) * 0.15
        self.assertAlmostEqual(p_next, expected, places=6)

    def test_update_mastery_order(self):
        """
        update_mastery must return prediction calculated BEFORE updating mastery.
        """
        pred, next_m = update_mastery(
            p_mastery=self.p_init,
            observed_correct=1,
            p_guess=self.p_guess,
            p_slip=self.p_slip,
            p_learn=self.p_learn,
        )
        self.assertAlmostEqual(pred, 0.38, places=6)
        expected_next = (9.0 / 19.0) + (10.0 / 19.0) * 0.15
        self.assertAlmostEqual(next_m, expected_next, places=6)

    def test_parameter_validation_valid(self):
        params = BKTParameters(p_init=0.3, p_learn=0.1, p_guess=0.2, p_slip=0.1)
        params.validate()  # Should not raise

    def test_parameter_validation_invalid_probabilities(self):
        with self.assertRaises(InvalidParameterError):
            BKTParameters(p_init=1.5, p_learn=0.1, p_guess=0.2, p_slip=0.1)

        with self.assertRaises(InvalidParameterError):
            BKTParameters(p_init=-0.1, p_learn=0.1, p_guess=0.2, p_slip=0.1)

    def test_parameter_validation_guess_plus_slip_ge_one(self):
        with self.assertRaises(InvalidParameterError):
            BKTParameters(p_init=0.2, p_learn=0.1, p_guess=0.6, p_slip=0.5)

    def test_numerical_stability_extreme_values(self):
        # Very low mastery
        pred_low = predict_correct_probability(1e-9, 0.25, 0.10)
        self.assertTrue(math.isfinite(pred_low))
        self.assertGreater(pred_low, 0.0)

        # Very high mastery
        pred_high = predict_correct_probability(1.0 - 1e-9, 0.25, 0.10)
        self.assertTrue(math.isfinite(pred_high))
        self.assertAlmostEqual(pred_high, 0.90, places=4)


class TestBKTSequences(unittest.TestCase):
    """Verifies sequence processing and state isolation."""

    def setUp(self):
        self.params = BKTParameters(p_init=0.20, p_learn=0.15, p_guess=0.25, p_slip=0.10)
        self.skill_params = SkillParameters(fallback_params=self.params)
        self.skill_params.set_params("101", self.params)

    def test_single_response_sequence(self):
        seq = [{"correct": 1}]
        results = predict_student_skill_sequence(seq, self.params)
        self.assertEqual(len(results), 1)
        self.assertAlmostEqual(results[0]["prediction"], 0.38, places=5)
        self.assertAlmostEqual(results[0]["mastery_before"], 0.20, places=5)

    def test_multi_response_sequence_mastery_growth(self):
        """Consistent correct answers must strictly increase latent mastery."""
        seq = [{"correct": 1}, {"correct": 1}, {"correct": 1}]
        results = predict_student_skill_sequence(seq, self.params)
        m0 = results[0]["mastery_before"]
        m1 = results[0]["mastery_after"]
        m2 = results[1]["mastery_after"]
        m3 = results[2]["mastery_after"]
        self.assertLess(m0, m1)
        self.assertLess(m1, m2)
        self.assertLess(m2, m3)

    def test_incorrect_response_decreases_mastery(self):
        """An incorrect response must drop mastery relative to before evidence update."""
        seq = [{"correct": 1}, {"correct": 0}]
        results = predict_student_skill_sequence(seq, self.params)
        m_after_corr = results[0]["mastery_after"]
        # In step 2, mastery_before is m_after_corr.
        # But after observing 0, the posterior is much lower.
        post_inc = posterior_learned_given_incorrect(m_after_corr, self.params.p_guess, self.params.p_slip)
        self.assertLess(post_inc, m_after_corr)

    def test_empty_sequence(self):
        results = predict_student_skill_sequence([], self.params)
        self.assertEqual(results, [])

    def test_independent_student_states(self):
        """Two students learning the same skill must maintain independent mastery states."""
        s1 = [{"skill_id": "101", "correct": 1}, {"skill_id": "101", "correct": 1}]
        s2 = [{"skill_id": "101", "correct": 0}, {"skill_id": "101", "correct": 0}]

        res1 = predict_student_all_skills(s1, self.skill_params)
        res2 = predict_student_all_skills(s2, self.skill_params)

        self.assertGreater(res1[-1]["mastery_after"], res2[-1]["mastery_after"])

    def test_independent_skill_states(self):
        """A student practicing two skills must have independent mastery for each."""
        p_other = BKTParameters(p_init=0.80, p_learn=0.05, p_guess=0.20, p_slip=0.10)
        self.skill_params.set_params("202", p_other)

        interactions = [
            {"skill_id": "101", "correct": 1},
            {"skill_id": "202", "correct": 0},
        ]
        res = predict_student_all_skills(interactions, self.skill_params)

        # First interaction was on skill 101 with p_init=0.20
        self.assertAlmostEqual(res[0]["mastery_before"], 0.20, places=5)
        # Second interaction was on skill 202 with p_init=0.80
        self.assertAlmostEqual(res[1]["mastery_before"], 0.80, places=5)

    def test_history_initialization(self):
        history = [
            {"skill_id": "101", "correct": 1},
            {"skill_id": "101", "correct": 1},
        ]
        states = initialize_student_from_history(history, self.skill_params)
        self.assertIn("101", states)
        self.assertGreater(states["101"], 0.20)


class TestBKTExpectationMaximization(unittest.TestCase):
    """Verifies Baum-Welch / EM parameter estimation mechanics."""

    def test_hmm_matrices_construction(self):
        params = BKTParameters(p_init=0.2, p_learn=0.1, p_guess=0.25, p_slip=0.1)
        pi, A, B = _build_hmm_matrices(params)

        self.assertAlmostEqual(pi[0], 0.8)
        self.assertAlmostEqual(pi[1], 0.2)
        # Absorbing state: A[1, 0] == 0, A[1, 1] == 1
        self.assertAlmostEqual(A[1, 0], 0.0)
        self.assertAlmostEqual(A[1, 1], 1.0)
        # Transition: A[0, 1] == T
        self.assertAlmostEqual(A[0, 1], 0.1)
        # Emission
        self.assertAlmostEqual(B[0, 1], 0.25)  # Guess
        self.assertAlmostEqual(B[1, 0], 0.10)  # Slip

    def test_scaled_forward_sum_to_one(self):
        params = BKTParameters(p_init=0.2, p_learn=0.1, p_guess=0.25, p_slip=0.1)
        pi, A, B = _build_hmm_matrices(params)
        obs = [1, 0, 1, 1]
        alpha_hat, c = scaled_forward(obs, pi, A, B)

        for t in range(len(obs)):
            self.assertAlmostEqual(float(np.sum(alpha_hat[t])), 1.0, places=5)

    def test_e_step_gamma_sum_to_one(self):
        params = BKTParameters(p_init=0.2, p_learn=0.1, p_guess=0.25, p_slip=0.1)
        pi, A, B = _build_hmm_matrices(params)
        obs = [0, 1, 1]
        estep = e_step_single_sequence(obs, pi, A, B)
        gamma = estep["gamma"]

        for t in range(len(obs)):
            self.assertAlmostEqual(float(np.sum(gamma[t])), 1.0, places=5)

    def test_em_parameter_fitting_synthetic(self):
        """EM should converge and produce valid probability parameters."""
        # Synthetic sequences: 10 students, each answering [0, 0, 1, 1]
        sequences = [[0, 0, 1, 1] for _ in range(10)]
        res = fit_skill_parameters(
            student_sequences=sequences,
            max_iterations=30,
            n_restarts=1,
            random_seed=42,
        )
        params = res["params"]
        self.assertTrue(0.0 <= params.p_init <= 1.0)
        self.assertTrue(0.0 <= params.p_learn <= 1.0)
        self.assertTrue(0.0 <= params.p_guess <= 0.5)
        self.assertTrue(0.0 <= params.p_slip <= 0.5)
        self.assertLess(params.p_guess + params.p_slip, 1.0)

    def test_em_reproducible_with_seed(self):
        seqs = [[1, 0, 1], [0, 1, 1], [1, 1, 1]]
        res1 = fit_skill_parameters(seqs, n_restarts=2, random_seed=42)
        res2 = fit_skill_parameters(seqs, n_restarts=2, random_seed=42)
        self.assertAlmostEqual(res1["params"].p_init, res2["params"].p_init, places=6)
        self.assertAlmostEqual(res1["params"].p_learn, res2["params"].p_learn, places=6)


class TestEvaluationMetrics(unittest.TestCase):
    """Verifies classification and probability calibration metrics."""

    def test_confusion_matrix_and_accuracy(self):
        y_true = [1, 1, 0, 0]
        y_pred = [0.8, 0.4, 0.2, 0.9]  # threshold=0.5 -> [1, 0, 0, 1]
        cm = confusion_matrix(y_true, y_pred, threshold=0.5)
        self.assertEqual(cm["tp"], 1)
        self.assertEqual(cm["fn"], 1)
        self.assertEqual(cm["tn"], 1)
        self.assertEqual(cm["fp"], 1)
        self.assertAlmostEqual(accuracy(y_true, y_pred, threshold=0.5), 0.5)

    def test_precision_recall_f1(self):
        y_true = [1, 1, 0]
        y_pred = [0.8, 0.8, 0.8]  # All predicted 1: TP=2, FP=1, FN=0
        p = precision(y_true, y_pred, 0.5)
        r = recall(y_true, y_pred, 0.5)
        f1 = f1_score(y_true, y_pred, 0.5)
        self.assertAlmostEqual(p, 2.0 / 3.0)
        self.assertAlmostEqual(r, 1.0)
        self.assertAlmostEqual(f1, 2.0 * (2/3 * 1) / (2/3 + 1))

    def test_roc_auc_perfect(self):
        y_true = [0, 0, 1, 1]
        y_pred = [0.1, 0.2, 0.8, 0.9]
        auc = roc_auc(y_true, y_pred)
        self.assertAlmostEqual(auc, 1.0)

    def test_roc_auc_single_class_is_none(self):
        y_true = [1, 1, 1]
        y_pred = [0.2, 0.5, 0.8]
        self.assertIsNone(roc_auc(y_true, y_pred))

    def test_log_loss_perfect(self):
        y_true = [1, 0]
        y_pred = [1.0, 0.0]  # will be clipped to eps and 1-eps
        loss = log_loss(y_true, y_pred)
        self.assertLess(loss, 1e-10)

    def test_brier_score(self):
        y_true = [1, 0]
        y_pred = [0.8, 0.2]
        # (0.8 - 1)^2 = 0.04, (0.2 - 0)^2 = 0.04 -> mean = 0.04
        brier = brier_score(y_true, y_pred)
        self.assertAlmostEqual(brier, 0.04, places=6)

    def test_expected_calibration_error(self):
        from app.evaluation.probability_metrics import expected_calibration_error, compute_calibration_bins
        # Perfectly calibrated predictions:
        # 10 examples predicting 0.8 where exactly 8 are correct
        # 10 examples predicting 0.2 where exactly 2 are correct
        y_true = [1]*8 + [0]*2 + [1]*2 + [0]*8
        y_pred = [0.8]*10 + [0.2]*10
        ece, bins = compute_calibration_bins(y_true, y_pred, n_bins=10)
        self.assertAlmostEqual(ece, 0.0, places=4)

    def test_ece_miscalibrated(self):
        from app.evaluation.probability_metrics import expected_calibration_error
        # Overconfident predictions: predicts 0.9, but true is all 0
        y_true = [0, 0, 0, 0]
        y_pred = [0.9, 0.9, 0.9, 0.9]
        ece = expected_calibration_error(y_true, y_pred, n_bins=10)
        self.assertAlmostEqual(ece, 0.9, places=4)


class TestBaselines(unittest.TestCase):
    """Verifies baseline estimators use only training data."""

    def test_majority_class_baseline_smoothed(self):
        train = [1, 1, 0]
        base = MajorityClassBaseline(smoothed=True).fit(train)
        preds = base.predict(3)
        # Laplace smoothed: (2 + 1) / (3 + 2) = 3/5 = 0.60
        self.assertAlmostEqual(preds[0], 0.60, places=4)
        self.assertEqual(len(preds), 3)

    def test_majority_class_baseline_hard(self):
        train = [1, 1, 0]
        base = MajorityClassBaseline(smoothed=False).fit(train)
        preds = base.predict(3, hard=True)
        self.assertEqual(preds, [1.0, 1.0, 1.0])

    def test_global_correctness_rate(self):
        train = [1, 1, 0, 0]
        base = GlobalCorrectnessRateBaseline().fit(train)
        preds = base.predict(2)
        # Laplace smoothed: (2 + 1) / (4 + 2) = 3/6 = 0.50
        self.assertAlmostEqual(preds[0], 0.50, places=4)

    def test_per_skill_rate_with_fallback(self):
        train = [
            {"skill_id": "1", "correct": 1},
            {"skill_id": "1", "correct": 0},
            {"skill_id": "2", "correct": 1},
            {"skill_id": "2", "correct": 1},
        ]
        base = PerSkillCorrectnessRateBaseline().fit(train)
        # Skill 1: (1 + 1) / (2 + 2) = 0.50
        self.assertAlmostEqual(base.predict_single("1"), 0.50, places=4)
        # Skill 2: (2 + 1) / (2 + 2) = 3/4 = 0.75
        self.assertAlmostEqual(base.predict_single("2"), 0.75, places=4)
        # Unseen skill falls back to smoothed global rate: (3 + 1) / (4 + 2) = 4/6 ≈ 0.6667
        self.assertAlmostEqual(base.predict_single("999"), 4.0 / 6.0, places=4)

    def test_baseline_empty_and_single_class_edge_cases(self):
        # Empty training data
        empty_maj = MajorityClassBaseline().fit([])
        self.assertEqual(empty_maj.predict(1), [0.5])
        empty_glob = GlobalCorrectnessRateBaseline().fit([])
        self.assertEqual(empty_glob.predict(1), [0.5])
        empty_skill = PerSkillCorrectnessRateBaseline().fit([])
        self.assertEqual(empty_skill.predict_single("101"), 0.5)

        # Single class: all correct (1)
        single_class_maj = MajorityClassBaseline(smoothed=True).fit([1, 1, 1])
        # (3 + 1) / (3 + 2) = 4/5 = 0.80
        self.assertAlmostEqual(single_class_maj.predict(1)[0], 0.80, places=4)

        # Single class: all incorrect (0)
        zero_class_maj = MajorityClassBaseline(smoothed=True).fit([0, 0, 0])
        # (0 + 1) / (3 + 2) = 1/5 = 0.20
        self.assertAlmostEqual(zero_class_maj.predict(1)[0], 0.20, places=4)


if __name__ == "__main__":
    unittest.main()
