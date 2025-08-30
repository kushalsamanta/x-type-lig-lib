"""
to remove the similar structures further, we apply the structure
matcher using stol=0.01 (or fine-tuned change stol < 0.01),
keeping other parameters False and high.
"""

#!/usr/bin/env python3
import os
import csv
import json
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed

from pymatgen.core import Structure
from pymatgen.analysis.structure_matcher import StructureMatcher

# -------- Config --------
# NOTE: "more negative energy" == numerically smaller float -> keep the minimum
INPUT_CSV  = os.environ.get("INPUT_CSV",  "consolidated_data_10th_step_filtered_E-1050_to_-500__F-100_to_100.csv")
OUTPUT_CSV = os.environ.get("OUTPUT_CSV", "consolidated_data_10th_step_after_str_mat.csv")
PREFER_MORE_NEGATIVE_ENERGY = True   # keep the more negative (lower) energy

# Workers: default to SLURM cpus-per-task if present, else all local cores
def _default_workers():
    for key in ("SLURM_CPUS_PER_TASK", "SLURM_CPUS_ON_NODE"):
        v = os.environ.get(key)
        if v and v.isdigit() and int(v) > 0:
            return int(v)
    return (os.cpu_count() or 4)
N_WORKERS = int(os.environ.get("N_WORKERS", _default_workers()))

# StructureMatcher parameters (yours)
SM_KW = dict(
    ltol=1, stol=0.01, angle_tol=5,
    primitive_cell=False, scale=False,
    attempt_supercell=False, allow_subset=False,
)

HEADERS = ["Structure", "Energy", "Forces", "Stress", "Directory", "Step"]

def parse_energy(x):
    try:
        return float(x)
    except Exception:
        return None

# --- fast composition signature from structure dict (no Structure() yet) ---
def comp_signature_from_sdict(sd):
    counts = {}
    for site in sd.get("sites", []):
        for sp in site.get("species", []):
            el  = sp.get("element")
            occ = sp.get("occu", sp.get("occupancy", 1.0))
            if el is None:
                continue
            counts[el] = counts.get(el, 0.0) + float(occ)
    return tuple(sorted((el, round(cnt, 6)) for el, cnt in counts.items()))

def load_rows(csv_path):
    rows = []
    with open(csv_path, "r", newline="") as f:
        r = csv.DictReader(f)
        missing = [h for h in HEADERS if h not in r.fieldnames]
        if missing:
            raise ValueError(f"Missing columns in {csv_path}: {missing}")
        for row in r:
            rows.append({h: row.get(h, "") for h in HEADERS})
    return rows

def bucket_globally(rows):
    """
    First-pass bucketing by (composition signature, nsites).
    Parse JSON once; store sd in row["_sdict"] to avoid re-parsing.
    """
    buckets = defaultdict(list)
    unparsable = []
    for row in rows:
        try:
            sd = json.loads(row["Structure"])
        except Exception:
            row["_sdict"]  = None
            row["_energy"] = parse_energy(row.get("Energy"))
            unparsable.append(row)
            continue

        row["_sdict"]  = sd
        row["_energy"] = parse_energy(row.get("Energy"))
        nsites   = len(sd.get("sites", []))
        comp_sig = comp_signature_from_sdict(sd)
        buckets[(comp_sig, nsites)].append(row)
    return buckets, unparsable

def dedup_bucket(items):
    """
    Deduplicate a single bucket (same composition + site count).
    Do a second coarse lattice bucketing to reduce O(n^2) comparisons.
    Returns (kept_rows, match_logs)
    """
    matcher = StructureMatcher(**SM_KW)
    sub = defaultdict(list)

    # Build sub-buckets by coarse lattice
    for r in items:
        sd = r["_sdict"]
        try:
            s = Structure.from_dict(sd)
        except Exception:
            r["_structure"] = None
            sub[("UNPARSEABLE", id(r))].append(r)
            continue

        r["_structure"] = s
        a, b, c = s.lattice.abc
        al, be, ga = s.lattice.angles
        coarse = (round(a, 2), round(b, 2), round(c, 2),
                  round(al, 1), round(be, 1), round(ga, 1))
        sub[coarse].append(r)

    kept = []
    logs = []  # rows of dicts for printing later

    for coarse_key, grp in sub.items():
        reps = []  # current representatives

        for cand in grp:
            sc = cand["_structure"]
            if sc is None:
                reps.append(cand)
                continue

            match_idx = None
            for j, rep in enumerate(reps):
                sr = rep["_structure"]
                if sr is None:
                    continue
                try:
                    if matcher.fit(sc, sr):
                        match_idx = j
                        break
                except Exception:
                    pass

            if match_idx is None:
                reps.append(cand)
            else:
                # compute RMS and MAX displacement between the pair
                rms, maxd = (None, None)
                try:
                    rms, maxd = matcher.get_rms_dist(sc, reps[match_idx]["_structure"])
                except Exception:
                    pass

                # decide which one to keep: MORE NEGATIVE energy (smaller float)
                action = "kept_old"
                if PREFER_MORE_NEGATIVE_ENERGY:
                    e_new = cand["_energy"]
                    e_old = reps[match_idx]["_energy"]
                    if e_new is not None and (e_old is None or e_new < e_old):
                        reps[match_idx] = cand
                        action = "replaced_with_new"

                # prepare a compact log line (we'll print later in main)
                kept_row  = reps[match_idx] if action == "replaced_with_new" else reps[match_idx]
                other_row = cand if action == "kept_old" else (reps[match_idx] if action=="replaced_with_new" else cand)
                logs.append({
                    "coarse": coarse_key,
                    "rms": rms, "max": maxd,
                    "kept_dir":  kept_row.get("Directory"), "kept_step":  kept_row.get("Step"), "kept_E":  kept_row.get("Energy"),
                    "other_dir": other_row.get("Directory"), "other_step": other_row.get("Step"), "other_E": other_row.get("Energy"),
                    "decision": action
                })

        kept.extend(reps)

    # strip helpers before returning
    for r in kept:
        r.pop("_structure", None)
        r.pop("_sdict", None)
        r.pop("_energy", None)

    return kept, logs

def main():
    if not os.path.exists(INPUT_CSV):
        raise FileNotFoundError(f"Input CSV not found: {INPUT_CSV}")

    rows = load_rows(INPUT_CSV)
    buckets, unparsable = bucket_globally(rows)

    kept_all = []
    logs_all = []

    # parallelize over buckets
    with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
        futures = {ex.submit(dedup_bucket, items): key for key, items in buckets.items()}
        for fut in as_completed(futures):
            kept, logs = fut.result()
            kept_all.extend(kept)
            logs_all.extend(logs)

    # add unparsable rows verbatim
    kept_all.extend(unparsable)

    # write output CSV
    with open(OUTPUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS)
        w.writeheader()
        for r in kept_all:
            w.writerow({h: r.get(h, "") for h in HEADERS})

    print(f"[OK] Deduplicated: kept {len(kept_all)} of {len(rows)} rows")
    print(f"[OK] Output -> {OUTPUT_CSV}")
    print(f"[INFO] Workers: {N_WORKERS}")

    # print match details to SLURM stdout
    if logs_all:
        print("\n[Match details] (one line per matched pair)")
        for L in logs_all:
            rms  = "nan" if L["rms"] is None else f"{L['rms']:.4f}"
            mxd  = "nan" if L["max"] is None else f"{L['max']:.4f}"
            print(
                f"coarse={L['coarse']} | RMS={rms} Å, MAX={mxd} Å | "
                f"kept=({L['kept_dir']}, step {L['kept_step']}, E={L['kept_E']}) | "
                f"other=({L['other_dir']}, step {L['other_step']}, E={L['other_E']}) | "
                f"decision={L['decision']}"
            )

if __name__ == "__main__":
    main()