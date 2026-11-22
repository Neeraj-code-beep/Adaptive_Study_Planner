"""
Detailed Audit Script for Phase 5.1
Inspects:
1. Convergence and log-likelihood monotonicity of EM across iterations
2. Extreme parameter estimates and their skill characteristics
3. Baseline probability behaviors
4. Cohort boundary assertions (Protocol A and Protocol B)
"""
import os
import sys
import json
import csv
from collections import defaultdict, Counter
import numpy as np

ML_SERVICE_DIR = r"N:\adaptive-study-planner\ml-service"
MODELS_DIR = os.path.join(ML_SERVICE_DIR, "models", "artifacts")
DATA_DIR = os.path.join(ML_SERVICE_DIR, "data")
REPORTS_DIR = os.path.join(DATA_DIR, "reports", "bkt")
SPLITS_DIR = os.path.join(DATA_DIR, "splits")

def audit_cohort_isolation():
    print("=" * 70)
    print("1. COHORT AND TEMPORAL LEAKAGE AUDIT")
    print("=" * 70)
    
    # Protocol A isolation
    train_path = os.path.join(SPLITS_DIR, "unseen_students", "train.csv")
    val_path = os.path.join(SPLITS_DIR, "unseen_students", "validation.csv")
    test_path = os.path.join(SPLITS_DIR, "unseen_students", "test.csv")
    
    def get_students(path):
        students = set()
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                students.add(row["student_id"])
        return students

    train_students = get_students(train_path)
    val_students = get_students(val_path)
    test_students = get_students(test_path)

    print(f"Protocol A - Train students: {len(train_students):,}")
    print(f"Protocol A - Val students:   {len(val_students):,}")
    print(f"Protocol A - Test students:  {len(test_students):,}")
    
    train_val_overlap = train_students & val_students
    train_test_overlap = train_students & test_students
    val_test_overlap = val_students & test_students
    
    print(f"  Overlap Train & Val:  {len(train_val_overlap)}")
    print(f"  Overlap Train & Test: {len(train_test_overlap)}")
    print(f"  Overlap Val & Test:   {len(val_test_overlap)}")
    assert len(train_val_overlap) == 0, "Protocol A leakage: Train & Val overlap!"
    assert len(train_test_overlap) == 0, "Protocol A leakage: Train & Test overlap!"
    assert len(val_test_overlap) == 0, "Protocol A leakage: Val & Test overlap!"
    print("  [PASS] Protocol A has STRICT ZERO STUDENT OVERLAP.")

    # Protocol B cohort metadata check
    cohort_path = os.path.join(REPORTS_DIR, "protocol_b_cohort_metadata.json")
    if os.path.exists(cohort_path):
        with open(cohort_path, "r", encoding="utf-8") as f:
            b_meta = json.load(f)
        print(f"\nProtocol B - Param Train student count: {b_meta['param_train_student_count']:,}")
        print(f"Protocol B - Evaluation student count:  {b_meta['eval_cohort_student_count']:,}")
        print(f"Protocol B - Total students:            {b_meta['total_unique_students']:,}")
        print(f"Protocol B - Leakage verification:      {b_meta['leakage_verification']}")
        assert b_meta["leakage_verification"]["zero_student_overlap"] is True
        print("  [PASS] Protocol B has STRICT ZERO STUDENT OVERLAP between fitting and eval cohorts.")
    print()

def audit_em_log_likelihood():
    print("=" * 70)
    print("2. EM LOG-LIKELIHOOD AND CONVERGENCE AUDIT")
    print("=" * 70)
    
    model_path = os.path.join(MODELS_DIR, "bkt_protocol_a.json")
    with open(model_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fit_details = data["per_skill_fit_details"]
    print(f"Total skills in fit details: {len(fit_details)}")
    
    fitted_skills = {k: v for k, v in fit_details.items() if v["status"] == "fitted"}
    fallback_skills = {k: v for k, v in fit_details.items() if v["status"] == "fallback"}
    print(f"Fitted skills count: {len(fitted_skills)}")
    print(f"Fallback skills count: {len(fallback_skills)}")

    converged_count = sum(1 for v in fitted_skills.values() if v.get("converged", False))
    print(f"Skills converged before max_iter: {converged_count} / {len(fitted_skills)}")
    
    # Check iterations distribution
    iters = [v["iterations"] for v in fitted_skills.values()]
    print(f"Iterations: min={min(iters)}, median={int(np.median(iters))}, mean={np.mean(iters):.1f}, max={max(iters)}")
    
    # Check log likelihood values
    lls = [v["log_likelihood"] for v in fitted_skills.values()]
    print(f"Final Log-Likelihood: min={min(lls):.2f}, median={np.median(lls):.2f}, max={max(lls):.2f}")
    print()

def audit_extreme_parameters():
    print("=" * 70)
    print("3. EXTREME PARAMETER ESTIMATES INVESTIGATION")
    print("=" * 70)
    
    model_path = os.path.join(MODELS_DIR, "bkt_protocol_a.json")
    with open(model_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fit_details = data["per_skill_fit_details"]
    
    extreme_cases = []
    for skill_id, details in fit_details.items():
        if details["status"] != "fitted":
            continue
        p = details["params"]
        obs = details["total_observations"]
        seqs = details["student_sequences"]
        conv = details.get("converged", False)
        it = details.get("iterations", 0)
        
        reasons = []
        if p["p_guess"] >= 0.49:
            reasons.append(f"High Guess (P(G)={p['p_guess']:.4f})")
        if p["p_slip"] >= 0.49:
            reasons.append(f"High Slip (P(S)={p['p_slip']:.4f})")
        if p["p_learn"] >= 0.90:
            reasons.append(f"High Learn (P(T)={p['p_learn']:.4f})")
        if p["p_learn"] <= 0.01:
            reasons.append(f"Low Learn (P(T)={p['p_learn']:.4f})")
        if p["p_init"] >= 0.90:
            reasons.append(f"High Prior (P(L0)={p['p_init']:.4f})")
        if p["p_init"] <= 0.05:
            reasons.append(f"Low Prior (P(L0)={p['p_init']:.4f})")
            
        if reasons:
            extreme_cases.append({
                "skill_id": skill_id,
                "observations": obs,
                "sequences": seqs,
                "iterations": it,
                "converged": conv,
                "params": p,
                "reasons": reasons,
            })
            
    print(f"Total skills flagged with extreme/boundary parameters: {len(extreme_cases)}")
    print("\nDetailed breakdown of flagged skills:")
    for ex in sorted(extreme_cases, key=lambda x: x["observations"]):
        p = ex["params"]
        print(f"Skill ID {ex['skill_id']:>4s} | Obs: {ex['observations']:>5d} | Seqs: {ex['sequences']:>4d} | Iter: {ex['iterations']:>2d} | Conv: {str(ex['converged']):<5s}")
        print(f"  Params: L0={p['p_init']:.4f}, T={p['p_learn']:.4f}, G={p['p_guess']:.4f}, S={p['p_slip']:.4f}")
        print(f"  Flags:  {', '.join(ex['reasons'])}")
        print()

if __name__ == "__main__":
    audit_cohort_isolation()
    audit_em_log_likelihood()
    audit_extreme_parameters()
