"""
if you want to check the energy and force value range after all filtration, 
Just to check what the actual range of energy and force values you are preparing
for training the M3GNET model.

input: 

python range_energy_force_from_csv.py --csv consolidated_data_10th_step_after_str_mat.csv"

output:

cat energy_force_range_summary.csv
metric,min,max,count_or_note
Energy (eV),-937.025435,-531.335548,parsed=5324; invalid=0
Fx (eV/Å),-3.567422e+01,4.106523e+01,vectors=1134539
Fy (eV/Å),-3.873667e+01,3.418310e+01,vectors=1134539
Fz (eV/Å),-4.427018e+01,4.585486e+01,vectors=1134539

"""

#!/usr/bin/env python3
import csv
import json
import argparse
import math
from typing import Optional, Tuple, Iterable, Any

def parse_float(x: Any) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None

def iter_force_triplets(forces_field: str) -> Iterable[Tuple[float, float, float]]:
    """
    Yield (fx, fy, fz) tuples from a JSON-encoded forces field.
    Accepts formats like:
      [[fx, fy, fz], ...]  or  [{"fx":..,"fy":..,"fz":..}, ...]  or {"x":..,"y":..,"z":..}
    """
    try:
        data = json.loads(forces_field)
    except Exception:
        return  # malformed JSON -> no yields

    # Normalize to a list of triplets (even if it's a single dict)
    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list):
        return

    for item in data:
        fx = fy = fz = None
        if isinstance(item, (list, tuple)) and len(item) >= 3:
            fx, fy, fz = item[0], item[1], item[2]
        elif isinstance(item, dict):
            # try common keys
            for kx, ky, kz in (("fx", "fy", "fz"), ("x", "y", "z")):
                if kx in item and ky in item and kz in item:
                    fx, fy, fz = item[kx], item[ky], item[kz]
                    break
        # Convert to floats if possible
        fx = parse_float(fx)
        fy = parse_float(fy)
        fz = parse_float(fz)
        if fx is not None and fy is not None and fz is not None:
            yield (fx, fy, fz)

def main():
    ap = argparse.ArgumentParser(description="Extract Energy and component-wise Force ranges from CSV.")
    ap.add_argument("--csv", required=True, help="Path to input CSV (expects columns: Energy, Forces)")
    ap.add_argument("--out-csv", default="energy_force_range_summary.csv",
                    help="Optional output CSV summary filename (default: energy_force_range_summary.csv)")
    args = ap.parse_args()

    E_min = math.inf
    E_max = -math.inf
    n_energy = 0
    n_energy_invalid = 0

    Fx_min = math.inf; Fx_max = -math.inf
    Fy_min = math.inf; Fy_max = -math.inf
    Fz_min = math.inf; Fz_max = -math.inf
    n_force_vecs = 0
    n_rows_forces_missing = 0

    with open(args.csv, "r", newline="") as f:
        r = csv.DictReader(f)
        # --- Energy ---
        for row in r:
            # ENERGY
            e = parse_float(row.get("Energy", None))
            if e is None:
                n_energy_invalid += 1
            else:
                E_min = e if e < E_min else E_min
                E_max = e if e > E_max else E_max
                n_energy += 1

            # FORCES
            forces_field = row.get("Forces", "")
            had_any = False
            for fx, fy, fz in iter_force_triplets(forces_field):
                had_any = True
                Fx_min = fx if fx < Fx_min else Fx_min
                Fx_max = fx if fx > Fx_max else Fx_max
                Fy_min = fy if fy < Fy_min else Fy_min
                Fy_max = fy if fy > Fy_max else Fy_max
                Fz_min = fz if fz < Fz_min else Fz_min
                Fz_max = fz if fz > Fz_max else Fz_max
                n_force_vecs += 1
            if not had_any:
                n_rows_forces_missing += 1

    # Print summary
    print("=== Summary: Energy & Force Ranges ===")
    if n_energy > 0:
        print(f"Energy range (eV): min={E_min:.6f}, max={E_max:.6f}  | parsed={n_energy}, invalid/missing={n_energy_invalid}")
    else:
        print(f"Energy: no valid values found. invalid/missing rows={n_energy_invalid}")

    if n_force_vecs > 0:
        print(f"Force component ranges (eV/Å):")
        print(f"  Fx: min={Fx_min:.6e}, max={Fx_max:.6e}")
        print(f"  Fy: min={Fy_min:.6e}, max={Fy_max:.6e}")
        print(f"  Fz: min={Fz_min:.6e}, max={Fz_max:.6e}")
        print(f"Total force vectors parsed: {n_force_vecs}  | rows with no/invalid forces: {n_rows_forces_missing}")
    else:
        print(f"Forces: no valid vectors found. rows with no/invalid forces: {n_rows_forces_missing}")

    # Write a tiny CSV summary
    with open(args.out_csv, "w", newline="") as fout:
        w = csv.writer(fout)
        w.writerow(["metric", "min", "max", "count_or_note"])
        if n_energy > 0:
            w.writerow(["Energy (eV)", f"{E_min:.6f}", f"{E_max:.6f}", f"parsed={n_energy}; invalid={n_energy_invalid}"])
        else:
            w.writerow(["Energy (eV)", "", "", f"parsed=0; invalid={n_energy_invalid}"])
        if n_force_vecs > 0:
            w.writerow(["Fx (eV/Å)", f"{Fx_min:.6e}", f"{Fx_max:.6e}", f"vectors={n_force_vecs}"])
            w.writerow(["Fy (eV/Å)", f"{Fy_min:.6e}", f"{Fy_max:.6e}", f"vectors={n_force_vecs}"])
            w.writerow(["Fz (eV/Å)", f"{Fz_min:.6e}", f"{Fz_max:.6e}", f"vectors={n_force_vecs}"])
        else:
            w.writerow(["Fx (eV/Å)", "", "", f"vectors=0"])
            w.writerow(["Fy (eV/Å)", "", "", f"vectors=0"])
            w.writerow(["Fz (eV/Å)", "", "", f"vectors=0"])

    print(f"\nSummary CSV written to: {args.out_csv}")

if __name__ == "__main__":
    main()