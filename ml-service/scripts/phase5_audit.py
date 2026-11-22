"""
Phase 5 Audit Script: Comprehensive audit of Phase 4 outputs
"""
import csv
import os
import json
from collections import Counter, defaultdict

RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "as.csv")
CLEANED_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "assistments_cleaned.csv")
SPLITS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "splits")

def audit_deduplication():
    """Audit the (order_id, skill_id) deduplication policy."""
    print("=" * 70)
    print("AUDIT 1: DEDUPLICATION ANALYSIS")
    print("=" * 70)

    # Count order_id uniqueness across ALL raw rows
    all_order_ids = []
    valid_rows = []
    total_raw = 0

    with open(RAW_PATH, "r", encoding="ISO-8859-1") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_raw += 1
            all_order_ids.append(row["order_id"])
            sid = row.get("skill_id", "").strip()
            sname = row.get("skill_name", "").strip()
            if sid and sid.lower() not in ("nan", "null") and sname and sname.lower() not in ("nan", "null"):
                valid_rows.append(row)

    unique_all_oids = len(set(all_order_ids))
    print(f"Total raw rows: {total_raw}")
    print(f"Unique order_ids (all rows): {unique_all_oids}")
    print(f"order_id IS globally unique: {unique_all_oids == total_raw}")
    print()

    # For valid-skill rows, analyze (order_id, skill_id) duplicates
    os_pairs = [(r["order_id"], r.get("skill_id", "").strip()) for r in valid_rows]
    unique_os = len(set(os_pairs))
    dup_os = len(os_pairs) - unique_os
    print(f"Valid-skill rows: {len(valid_rows)}")
    print(f"Unique (order_id, skill_id) pairs: {unique_os}")
    print(f"Duplicate (order_id, skill_id) rows: {dup_os}")
    print()

    # Examine what differs in duplicate rows
    os_groups = defaultdict(list)
    for r in valid_rows:
        key = (r["order_id"], r.get("skill_id", "").strip())
        os_groups[key].append(r)

    dup_groups = {k: v for k, v in os_groups.items() if len(v) > 1}
    print(f"Number of duplicate groups: {len(dup_groups)}")

    # Check if correct values differ within duplicate groups
    correct_differs = 0
    correct_same = 0
    for key, rows in dup_groups.items():
        corrects = set(r["correct"] for r in rows)
        if len(corrects) > 1:
            correct_differs += 1
        else:
            correct_same += 1

    print(f"Duplicate groups where 'correct' differs: {correct_differs}")
    print(f"Duplicate groups where 'correct' is identical: {correct_same}")
    print()

    # Show a few examples of duplicates
    print("Sample duplicate groups (first 3):")
    for i, (key, rows) in enumerate(dup_groups.items()):
        if i >= 3:
            break
        print(f"  Group key: order_id={key[0]}, skill_id={key[1]}")
        for r in rows:
            print(f"    correct={r['correct']}, attempt_count={r.get('attempt_count','?')}, "
                  f"original={r.get('original','?')}, problem_id={r.get('problem_id','?')}, "
                  f"opportunity(original)={r.get('opportunity(Default)','?')}, "
                  f"opportunity_orig={r.get('opportunity (Unique-step)','?')}")
        print()

    # Check which column(s) differ in duplicates
    print("Columns that differ within duplicate groups (sample of 100 groups):")
    differing_cols = Counter()
    for i, (key, rows) in enumerate(dup_groups.items()):
        if i >= 100:
            break
        cols = rows[0].keys()
        for col in cols:
            vals = set(r.get(col, "") for r in rows)
            if len(vals) > 1:
                differing_cols[col] += 1
    for col, count in differing_cols.most_common():
        print(f"  {col}: differs in {count}/100 sampled groups")

    # Check if first row kept (streaming order) preserves first occurrence
    print()
    print("Deduplication policy: first-seen row is retained (streaming order).")
    print("This preserves the row with the LOWEST CSV line number for each (order_id, skill_id).")
    print()

    # Check order_id uniqueness per user
    user_order_pairs = defaultdict(list)
    for r in valid_rows:
        user_order_pairs[(r["user_id"], r["order_id"])].append(r)
    tied_uo = sum(1 for v in user_order_pairs.values() if len(v) > 1)
    print(f"(user_id, order_id) pairs with multiple rows (multi-skill questions): {tied_uo}")

    return {
        "total_raw": total_raw,
        "unique_order_ids": unique_all_oids,
        "order_id_globally_unique": unique_all_oids == total_raw,
        "valid_skill_rows": len(valid_rows),
        "duplicate_os_rows": dup_os,
        "correct_differs_in_dups": correct_differs,
        "correct_same_in_dups": correct_same,
        "tied_user_order_pairs": tied_uo,
    }


def audit_multi_skill():
    """Audit multi-skill delimiter rows in cleaned data."""
    print()
    print("=" * 70)
    print("AUDIT 2: MULTI-SKILL INTERACTION ANALYSIS")
    print("=" * 70)

    delimiters = ["~~", "--"]  # ASSISTments uses ~~ for multi-skill
    multi_skill_count = 0
    multi_skill_examples = []
    skill_id_to_names = defaultdict(set)
    total = 0
    skill_ids = set()
    skill_names = set()

    with open(CLEANED_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            sname = row["skill_name"]
            sid = row["skill_id"]
            skill_ids.add(sid)
            skill_names.add(sname)
            skill_id_to_names[sid].add(sname)

            is_multi = any(d in sname for d in delimiters)
            if is_multi:
                multi_skill_count += 1
                if len(multi_skill_examples) < 10:
                    multi_skill_examples.append({
                        "skill_id": sid,
                        "skill_name": sname,
                        "correct": row["correct"],
                        "student_id": row["student_id"],
                    })

    print(f"Total cleaned rows: {total}")
    print(f"Unique skill_ids: {len(skill_ids)}")
    print(f"Unique skill_names: {len(skill_names)}")
    print(f"Multi-skill rows (containing ~~ or --): {multi_skill_count}")
    print(f"Multi-skill percentage: {multi_skill_count / total * 100:.2f}%")
    print()

    # Identify which skill_ids are multi-skill
    multi_skill_ids = set()
    for sid, names in skill_id_to_names.items():
        for name in names:
            if any(d in name for d in delimiters):
                multi_skill_ids.add(sid)
    print(f"Distinct skill_ids with multi-skill labels: {len(multi_skill_ids)}")
    print()

    print("Examples of multi-skill labels:")
    for ex in multi_skill_examples:
        name_trunc = ex["skill_name"][:80]
        print(f"  skill_id={ex['skill_id']}, name=\"{name_trunc}\", correct={ex['correct']}")

    # Absolute Value analysis
    print()
    print("=" * 70)
    print("AUDIT 3: ABSOLUTE VALUE SKILL ID MAPPING")
    print("=" * 70)
    abs_val_ids = set()
    abs_val_counts = Counter()
    with open(CLEANED_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "Absolute Value" == row["skill_name"].strip():
                abs_val_ids.add(row["skill_id"])
                abs_val_counts[row["skill_id"]] += 1
    print(f"'Absolute Value' maps to skill_ids: {abs_val_ids}")
    for sid, cnt in abs_val_counts.items():
        print(f"  skill_id={sid}: {cnt} interactions")

    return {
        "total": total,
        "multi_skill_count": multi_skill_count,
        "multi_skill_ids": list(multi_skill_ids),
        "unique_skill_ids": len(skill_ids),
        "unique_skill_names": len(skill_names),
        "abs_val_ids": list(abs_val_ids),
    }


def audit_correctness_semantics():
    """Audit what 'correct' represents using original and attempt_count."""
    print()
    print("=" * 70)
    print("AUDIT 4: CORRECTNESS SEMANTICS")
    print("=" * 70)

    # Analyze original column distribution in cleaned data
    original_dist = Counter()
    correct_by_original = defaultdict(Counter)
    attempt_dist = Counter()

    with open(CLEANED_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            orig = row.get("original", "?")
            corr = row["correct"]
            att = row.get("attempt_count", "?")
            original_dist[orig] += 1
            correct_by_original[orig][corr] += 1
            attempt_dist[att] += 1

    print("Distribution of 'original' field in cleaned data:")
    for val, cnt in sorted(original_dist.items()):
        print(f"  original={val}: {cnt} rows")
        for c, cc in sorted(correct_by_original[val].items()):
            rate = cc / cnt * 100
            print(f"    correct={c}: {cc} ({rate:.2f}%)")

    print()
    print("Distribution of 'attempt_count' in cleaned data (top 10):")
    for val, cnt in attempt_dist.most_common(10):
        print(f"  attempt_count={val}: {cnt} rows")

    # Check if scaffolding rows (original=0) are present
    scaffold_count = original_dist.get("0", 0)
    main_count = original_dist.get("1", 0)
    print()
    print(f"Main problems (original=1): {main_count}")
    print(f"Scaffolding problems (original=0): {scaffold_count}")
    print(f"Percentage scaffolding: {scaffold_count / (main_count + scaffold_count) * 100:.2f}%" if (main_count + scaffold_count) > 0 else "N/A")

    # In raw data, check original distribution
    print()
    print("--- Raw data original distribution ---")
    raw_orig = Counter()
    with open(RAW_PATH, "r", encoding="ISO-8859-1") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_orig[row.get("original", "?")] += 1
    for val, cnt in sorted(raw_orig.items()):
        print(f"  original={val}: {cnt} rows")


def audit_correctness_rate():
    """Final correctness rate verification."""
    print()
    print("=" * 70)
    print("AUDIT 5: CORRECTED CORRECTNESS RATES")
    print("=" * 70)

    # Cleaned dataset
    total = 0; c0 = 0; c1 = 0
    with open(CLEANED_PATH, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            total += 1
            if row["correct"] == "1": c1 += 1
            else: c0 += 1
    actual_rate = c1 / total * 100
    print(f"Cleaned: total={total}, c0={c0}, c1={c1}, rate={actual_rate:.4f}%")
    print(f"Phase 4 reported rate: 69.53% -- INCORRECT")
    print(f"Actual rate: {actual_rate:.2f}% -- CORRECT")
    print()

    # Protocol A splits
    for name in ["train", "validation", "test"]:
        path = os.path.join(SPLITS_DIR, "unseen_students", f"{name}.csv")
        t = 0; s0 = 0; s1 = 0
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                t += 1
                if row["correct"] == "1": s1 += 1
                else: s0 += 1
        print(f"Protocol A {name}: total={t}, c0={s0}, c1={s1}, rate={s1/t*100:.4f}%")

    print()
    # Protocol B splits
    for name in ["history", "future_test"]:
        path = os.path.join(SPLITS_DIR, "known_students_future", f"{name}.csv")
        t = 0; s0 = 0; s1 = 0
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                t += 1
                if row["correct"] == "1": s1 += 1
                else: s0 += 1
        print(f"Protocol B {name}: total={t}, c0={s0}, c1={s1}, rate={s1/t*100:.4f}%")


if __name__ == "__main__":
    dedup_results = audit_deduplication()
    multi_results = audit_multi_skill()
    audit_correctness_semantics()
    audit_correctness_rate()

    print()
    print("=" * 70)
    print("AUDIT SUMMARY")
    print("=" * 70)
    print(json.dumps(dedup_results, indent=2))
    print(json.dumps(multi_results, indent=2))
