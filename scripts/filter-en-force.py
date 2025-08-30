"""
Convert all the JSON files into a single CSV file
Where the file will contain the filtered energy &
Force values that we decided from the previous code
"energy_force_component_distribution_before_filter.py"

We can plot the energy and force distributions. 
"""

#!/usr/bin/env python3
import csv, os, sys, json

# === Config ===
IN_CSV  = "consolidated_data_10th_step.csv"   # or pass as first CLI arg
EMIN    = -1050.0
EMAX    = -500.0
FMIN    = -100.0
FMAX    =  100.0

if len(sys.argv) > 1:
    IN_CSV = sys.argv[1]

base, ext = os.path.splitext(IN_CSV)
OUT_CSV = f"{base}_filtered_E{int(EMIN)}_to_{int(EMAX)}__F{int(FMIN)}_to_{int(FMAX)}{ext}"

def parse_float(x):
    try:
        return float(x)
    except Exception:
        return None

def forces_components_in_range(forces_json_str, fmin, fmax):
    """
    forces_json_str: JSON string of [[Fx,Fy,Fz], ...]
    Returns (ok, count_components). ok=True iff EVERY parsed component is within [fmin,fmax].
    """
    try:
        data = json.loads(forces_json_str)
    except Exception:
        return (False, 0)

    total = 0
    for vec in data if isinstance(data, list) else []:
        if not (isinstance(vec, (list, tuple)) and len(vec) >= 3):
            continue
        for comp in (vec[0], vec[1], vec[2]):
            val = parse_float(comp)
            if val is None:
                return (False, total)
            total += 1
            if not (fmin <= val <= fmax):
                return (False, total)
    return (total > 0, total)

kept = 0
dropped_energy = 0
dropped_force  = 0
invalid_energy = 0
invalid_forces = 0
total_rows = 0

with open(IN_CSV, "r", newline="") as fin, open(OUT_CSV, "w", newline="") as fout:
    r = csv.DictReader(fin)
    fieldnames = r.fieldnames or []
    if "Energy" not in fieldnames or "Forces" not in fieldnames:
        raise ValueError("Input CSV must contain 'Energy' and 'Forces' columns.")
    w = csv.DictWriter(fout, fieldnames=fieldnames)
    w.writeheader()

    for row in r:
        total_rows += 1

        # Energy filter
        e = parse_float(row.get("Energy", ""))
        if e is None:
            invalid_energy += 1
            continue
        if not (EMIN <= e <= EMAX):
            dropped_energy += 1
            continue

        # Force per-component filter
        ok, ncomp = forces_components_in_range(row.get("Forces", ""), FMIN, FMAX)
        if not ok:
            if ncomp == 0:
                invalid_forces += 1
            else:
                dropped_force += 1
            continue

        # Passed both filters
        w.writerow(row)
        kept += 1

print(f"Input:            {IN_CSV}")
print(f"Output:           {OUT_CSV}")
print(f"Total rows read:  {total_rows}")
print(f"Kept rows:        {kept}")
print(f"Dropped (energy): {dropped_energy}  [Energy not in [{EMIN}, {EMAX}] eV]")
print(f"Dropped (forces): {dropped_force}   [Some Fx/Fy/Fz outside [{FMIN}, {FMAX}] eV/Å]")
print(f"Invalid Energy:   {invalid_energy}  [non-numeric or missing]")
print(f"Invalid Forces:   {invalid_forces}  [missing/invalid JSON or no components]")