import json
import numpy as np

def analyze_model(artifact_path):
    print("=" * 60)
    print("ANALYSIS OF:", artifact_path)
    print("=" * 60)
    with open(artifact_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    skills = data["per_skill_parameters"]["skill_map"]
    print(f"Total skills fitted: {len(skills)}")
    print(f"Fallback skills count: {data['summary']['fallback_skills_count']}")
    print(f"Global fallback params: {data['summary']['global_fallback_params']}")

    p_init = [v["p_init"] for v in skills.values()]
    p_learn = [v["p_learn"] for v in skills.values()]
    p_guess = [v["p_guess"] for v in skills.values()]
    p_slip = [v["p_slip"] for v in skills.values()]

    for name, vals in [("P(L0)", p_init), ("P(T)", p_learn), ("P(G)", p_guess), ("P(S)", p_slip)]:
        print(f"{name:8s}: mean={np.mean(vals):.4f}, median={np.median(vals):.4f}, std={np.std(vals):.4f}, min={np.min(vals):.4f}, max={np.max(vals):.4f}")

    guess_bound = sum(1 for g in p_guess if g >= 0.49)
    slip_bound = sum(1 for s in p_slip if s >= 0.49)
    init_near_zero = sum(1 for l in p_init if l <= 0.05)
    init_near_one = sum(1 for l in p_init if l >= 0.90)
    learn_near_zero = sum(1 for t in p_learn if t <= 0.01)
    
    print("\nDegeneracy / Boundary Analysis:")
    print(f"  P(G) near boundary (>= 0.49): {guess_bound}")
    print(f"  P(S) near boundary (>= 0.49): {slip_bound}")
    print(f"  P(L0) <= 0.05: {init_near_zero}")
    print(f"  P(L0) >= 0.90: {init_near_one}")
    print(f"  P(T) <= 0.01:  {learn_near_zero}")

if __name__ == "__main__":
    analyze_model(r"N:\adaptive-study-planner\ml-service\models\artifacts\bkt_protocol_a.json")
    analyze_model(r"N:\adaptive-study-planner\ml-service\models\artifacts\bkt_protocol_b.json")
