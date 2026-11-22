"""
Phase 5.2 Verification Script
Extracts detailed calibration, EM convergence, extreme parameter evidence,
and artifact integrity metrics.
"""

import json
import csv
import os
from collections import defaultdict

def verify_calibration():
    print("=" * 70)
    print("1. CALIBRATION METRICS & RELIABILITY BINS VERIFICATION")
    print("=" * 70)
    
    with open('N:/adaptive-study-planner/ml-service/data/reports/bkt/protocol_a_results.json') as f:
        ra = json.load(f)
    with open('N:/adaptive-study-planner/ml-service/data/reports/bkt/protocol_b_results.json') as f:
        rb = json.load(f)
        
    splits = [
        ('Protocol A Validation (N=45,297)', ra['results']['validation']),
        ('Protocol A Test (N=52,141)', ra['results']['test']),
        ('Protocol B Future Test (N=19,910)', rb['results']['future_test'])
    ]
    
    models = [
        ('bkt', 'BKT'),
        ('per_skill_rate', 'Per-Skill Rate Baseline'),
        ('global_correctness_rate', 'Global Rate Baseline'),
        ('majority_class', 'Majority Class (Smoothed)'),
        ('majority_class_hard', 'Majority Class (Hard)')
    ]
    
    for split_title, split_data in splits:
        print(f"\n>>> {split_title} <<<")
        for m_key, m_name in models:
            if m_key not in split_data:
                continue
            m = split_data[m_key]
            ece = m.get('ece', None)
            print(f"\nModel: {m_name}")
            print(f"  N={m['n_observations']}, Accuracy={m['accuracy']:.4f}, AUC={m['roc_auc']}, LogLoss={m['log_loss']:.4f}, Brier={m['brier_score']:.4f}, ECE={ece}")
            bins = m.get('calibration_bins', [])
            empty_bins = 0
            for b in bins:
                if b['count'] == 0:
                    empty_bins += 1
                print(f"    Bin {b['bin_index']:2d} [{b['bin_lower']:.1f}, {b['bin_upper']:.1f}]: count={b['count']:6d}, pred={b['pred_mean']:.4f}, obs={b['observed_mean']:.4f}, err={b['calibration_error']:.4f}")
            print(f"  Empty bins excluded from error calculation: {empty_bins} / 10")

def verify_em_convergence():
    print("\n" + "=" * 70)
    print("2. EM CONVERGENCE DETAILED VERIFICATION")
    print("=" * 70)
    
    for p in ['protocol_a', 'protocol_b']:
        with open(f'N:/adaptive-study-planner/ml-service/models/artifacts/bkt_{p}.json') as f:
            d = json.load(f)
        details = d['per_skill_fit_details']
        fitted = [v for v in details.values() if v['status'] == 'fitted']
        fallback = [v for v in details.values() if v['status'] == 'fallback']
        converged = [v for v in fitted if v.get('converged', False)]
        max_iter = [v for v in fitted if not v.get('converged', False)]
        iters = [v['iterations'] for v in fitted]
        
        # Check LL improvement monotonicity
        print(f"\nArtifact: bkt_{p}.json")
        print(f"  Total skills: {len(details)}")
        print(f"  Fitted: {len(fitted)}, Fallback: {len(fallback)}")
        print(f"  Converged before max_iter: {len(converged)} ({len(converged)/len(fitted)*100:.2f}%)")
        print(f"  Reached max_iter (30): {len(max_iter)} ({len(max_iter)/len(fitted)*100:.2f}%)")
        iters_sorted = sorted(iters)
        median_it = iters_sorted[len(iters)//2]
        print(f"  Iterations: Min={min(iters)}, Median={median_it}, Mean={sum(iters)/len(iters):.2f}, Max={max(iters)}")
        
        # Check convergence warning types
        warning_counts = defaultdict(int)
        for v in details.values():
            for w in v.get('warnings', []):
                warning_counts[w.split(':')[0]] += 1
        print("  Warning categories:")
        for w_type, cnt in warning_counts.items():
            print(f"    {w_type}: {cnt}")

def verify_extreme_parameters_with_dataset():
    print("\n" + "=" * 70)
    print("3. EXTREME PARAMETER INVESTIGATION WITH EMPIRICAL DATASET EVIDENCE")
    print("=" * 70)
    
    # Load dataset to extract empirical metrics per skill
    csv_path = 'N:/adaptive-study-planner/ml-service/data/processed/assistments_cleaned.csv'
    
    skill_stats = defaultdict(lambda: {
        'total_obs': 0,
        'correct_obs': 0,
        'first_obs': 0,
        'first_correct': 0,
        'scaffolding_obs': 0,
        'students': set(),
        'skill_name': ''
    })
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            sid = r['skill_id']
            st = skill_stats[sid]
            st['skill_name'] = r['skill_name']
            st['total_obs'] += 1
            st['students'].add(r['student_id'])
            c = int(r['correct'])
            st['correct_obs'] += c
            if r['original'] == '0':
                st['scaffolding_obs'] += 1
            if r['attempt_count'] == '1':
                st['first_obs'] += 1
                st['first_correct'] += c
                
    with open('N:/adaptive-study-planner/ml-service/models/artifacts/bkt_protocol_a.json') as f:
        da = json.load(f)
        
    skills_to_inspect = [
        # Extreme Guess
        ('50', 'Ordering Fractions', 'Guess bound P(G)=0.50'),
        ('26', 'Angles on Parallel Lines', 'Guess bound P(G)=0.50'),
        ('298', 'Area Triangle', 'Guess bound P(G)=0.50'),
        ('314', 'Angles - Obtuse, Acute, Right', 'Guess bound P(G)=0.50'),
        ('362', 'Parts of a Polynomial', 'Guess bound P(G)=0.50'),
        # Extreme Slip
        ('299', 'Surface Area Cylinder', 'Slip bound P(S)=0.50'),
        ('350', 'Solving Systems of Linear Equations', 'Slip bound P(S)=0.50'),
        # High Learning
        ('333', 'Finding Slope From Equation', 'High learn P(T)=0.999'),
        ('110', 'Understanding Probabilities', 'High learn P(T)=0.985'),
        ('371', 'Simplifying Expressions positive exponents', 'High learn P(T)=0.938'),
        # Low Learning / High Initial
        ('32', 'Nets of 3D Figures', 'High prior P(L0)=0.994, Low T=0.001'),
        ('307', 'Volume Rectangular Prism', 'High prior P(L0)=0.933, Low T=0.001'),
        ('204', 'Percents', 'Low learn P(T)=0.001')
    ]
    
    print("\nEmpirical evidence for flagged extreme skills:")
    for sid, label, reason in skills_to_inspect:
        st = skill_stats[sid]
        n_obs = st['total_obs']
        n_stud = len(st['students'])
        acc = st['correct_obs'] / n_obs if n_obs else 0.0
        first_acc = st['first_correct'] / st['first_obs'] if st['first_obs'] else 0.0
        scaff_pct = st['scaffolding_obs'] / n_obs * 100 if n_obs else 0.0
        
        params = da['per_skill_parameters']['skill_map'].get(sid, {})
        print(f"\nSkill {sid}: {st['skill_name']} ({reason})")
        print(f"  Fitted BKT: L0={params.get('p_init', 0):.4f}, T={params.get('p_learn', 0):.4f}, G={params.get('p_guess', 0):.4f}, S={params.get('p_slip', 0):.4f}")
        print(f"  Measured Dataset Evidence: Total Obs={n_obs}, Students={n_stud}, Overall Acc={acc:.4f}, First-Attempt Acc={first_acc:.4f}, Scaffolding={scaff_pct:.1f}%")

def verify_artifact_integrity():
    print("\n" + "=" * 70)
    print("4. ARTIFACT INTEGRITY & GITIGNORE CHECK")
    print("=" * 70)
    
    # Check Phase 4 data
    raw_path = 'N:/adaptive-study-planner/ml-service/data/raw/as.csv'
    clean_path = 'N:/adaptive-study-planner/ml-service/data/processed/assistments_cleaned.csv'
    print(f"Raw dataset exists: {os.path.exists(raw_path)}, size={os.path.getsize(raw_path):,} bytes")
    print(f"Cleaned dataset exists: {os.path.exists(clean_path)}, size={os.path.getsize(clean_path):,} bytes")
    
    # Check row count of cleaned
    with open(clean_path, 'r', encoding='utf-8') as f:
        clean_rows = sum(1 for _ in f) - 1
    print(f"Cleaned dataset rows: {clean_rows:,} (Must be exactly 324,449)")
    
    # Check gitignore
    gitignore_path = 'N:/adaptive-study-planner/.gitignore'
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        gi = f.read()
    print("Gitignore includes models/artifacts: ", "models/artifacts" in gi or "*.json" in gi or "models/" in gi)
    print("Gitignore includes data/reports: ", "data/reports" in gi or "reports/" in gi or "*.json" in gi)

if __name__ == '__main__':
    verify_calibration()
    verify_em_convergence()
    verify_extreme_parameters_with_dataset()
    verify_artifact_integrity()
