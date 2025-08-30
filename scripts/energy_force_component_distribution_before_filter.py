"""
check the distribution of energies, forces (fx, fy, and fz)
This will help us filter the range of energy, forces, or stress values we should consider in our data set before combining all the JSON files into a CSV file.

We can set the bin sizes for energy and forces accordingly.
"""


#!/usr/bin/env python3
import os
import json
import math
import csv

# ==== Config ====
JSON_DIR   = "phosphorus_based_int_str"          # folder with intermediate JSON files
OUT_CSV    = "energy_force_component_distribution_before_filter.csv"
BIN_E      = 150.0   # energy bin width (eV)
BIN_FC     = 10    # force-component bin width (eV/Å)

# --- Helpers (same step-selection you use) ---
def geo_idx(name: str) -> int:
    if name == "geo_opt":
        return 1
    if name.startswith("geo_opt_"):
        try:
            return int(name.split("_")[2])
        except Exception:
            return 0
    return 0

def select_steps_for_folder(entries, is_highest: bool):
    def parse_step(e):
        try:
            return int(e.get("step", -1))
        except Exception:
            return -1

    entries_sorted = sorted(entries, key=parse_step)
    if not entries_sorted:
        return []

    if len(entries_sorted) < 10:
        return [entries_sorted[-1]]

    first_two_steps = {parse_step(entries_sorted[0]), parse_step(entries_sorted[1])}
    selected, seen = [], set()
    for e in entries_sorted:
        s = parse_step(e)
        if s in (-1,): continue
        if s in first_two_steps: continue
        if s % 10 == 0 and s not in seen:
            selected.append(e); seen.add(s)

    if is_highest:
        last_e = entries_sorted[-1]
        if last_e not in selected:
            selected.append(last_e)

    return sorted(selected, key=parse_step)

def ffloat(x):
    try:
        return float(x)
    except Exception:
        return None

def make_hist(values, bin_width):
    vmin, vmax = min(values), max(values)
    start_bin = math.floor(vmin / bin_width) * bin_width
    end_bin   = math.ceil(vmax / bin_width) * bin_width
    if end_bin == start_bin:
        end_bin = start_bin + bin_width
    num_bins = int(round((end_bin - start_bin) / bin_width))
    edges = [start_bin + i * bin_width for i in range(num_bins + 1)]
    counts = [0] * num_bins
    for v in values:
        idx = int((v - start_bin) // bin_width)
        if idx < 0: idx = 0
        if idx >= num_bins: idx = num_bins - 1
        counts[idx] += 1
    return edges, counts

# --- Collect BEFORE filtering ---
base_dir = os.getcwd()
json_dir = os.path.join(base_dir, JSON_DIR)

energies = []
Fx, Fy, Fz = [], [], []

num_files = 0
invalid_energy = 0
invalid_force_rows = 0
force_components_parsed = 0

for json_filename in os.listdir(json_dir):
    if not json_filename.endswith(".json"):
        continue

    json_path = os.path.join(json_dir, json_filename)
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            continue

        # group by geo_opt_folder
        groups = {}
        for step_data in data:
            gof  = step_data.get("geo_opt_folder")
            step = step_data.get("step", None)
            if gof is None or step is None:
                continue
            groups.setdefault(gof, []).append(step_data)
        if not groups:
            continue

        # highest geo_opt folder
        folder_indices = {gof: geo_idx(gof) for gof in groups.keys()}
        valid_folders  = {gof: idx for gof, idx in folder_indices.items() if idx > 0}
        if not valid_folders:
            continue
        highest_folder = max(valid_folders, key=lambda k: valid_folders[k])

        # select steps (no filtering)
        for gof, entries in groups.items():
            is_highest = (gof == highest_folder)
            selected_entries = select_steps_for_folder(entries, is_highest=is_highest)

            for step_data in selected_entries:
                # energy
                e = ffloat(step_data.get("energy", None))
                if e is None:
                    invalid_energy += 1
                else:
                    energies.append(e)

                # component-wise forces
                forces = step_data.get("forces", None)
                if not isinstance(forces, list):
                    invalid_force_rows += 1
                    continue
                any_component = False
                for vec in forces:
                    if not (isinstance(vec, (list, tuple)) and len(vec) >= 3):
                        continue
                    fx = ffloat(vec[0]); fy = ffloat(vec[1]); fz = ffloat(vec[2])
                    if fx is not None: Fx.append(fx); any_component = True; force_components_parsed += 1
                    if fy is not None: Fy.append(fy); any_component = True; force_components_parsed += 1
                    if fz is not None: Fz.append(fz); any_component = True; force_components_parsed += 1
                if not any_component:
                    invalid_force_rows += 1

        num_files += 1

    except json.JSONDecodeError:
        print(f"[WARN] Could not parse JSON: {json_path}")
    except Exception as exc:
        print(f"[WARN] Error in {json_path}: {exc}")

if not energies and not (Fx or Fy or Fz):
    print("No energies or forces found. Nothing to do.")
    raise SystemExit(0)

# --- Build histograms (long-form table) ---
rows = []  # each row: [quantity, bin_start, bin_end, count]

if energies:
    e_edges, e_counts = make_hist(energies, BIN_E)
    for i in range(len(e_counts)):
        rows.append(["energy_eV", e_edges[i], e_edges[i+1], e_counts[i]])

def add_force_hist(label, arr):
    if not arr:
        return
    f_edges, f_counts = make_hist(arr, BIN_FC)
    for i in range(len(f_counts)):
        rows.append([label, f_edges[i], f_edges[i+1], f_counts[i]])

add_force_hist("Fx_eV_per_A", Fx)
add_force_hist("Fy_eV_per_A", Fy)
add_force_hist("Fz_eV_per_A", Fz)

# --- Write CSV ---
with open(os.path.join(base_dir, OUT_CSV), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["quantity", "bin_start", "bin_end", "count"])
    w.writerows(rows)

# --- Print summary ---
if energies:
    print(f"Energy range (min, max): ({min(energies):.6f}, {max(energies):.6f}) eV ; bin width={BIN_E}")
else:
    print("No valid energies.")
if Fx:
    print(f"Fx range (min, max): ({min(Fx):.6f}, {max(Fx):.6f}) eV/Å ; bin width={BIN_FC}")
else:
    print("No valid Fx values.")
if Fy:
    print(f"Fy range (min, max): ({min(Fy):.6f}, {max(Fy):.6f}) eV/Å ; bin width={BIN_FC}")
else:
    print("No valid Fy values.")
if Fz:
    print(f"Fz range (min, max): ({min(Fz):.6f}, {max(Fz):.6f}) eV/Å ; bin width={BIN_FC}")
else:
    print("No valid Fz values.")

print(f"Files processed: {num_files}")
print(f"Invalid/missing energies skipped: {invalid_energy}")
print(f"Force rows with no parseable components: {invalid_force_rows}")
print(f"Total force components parsed: {force_components_parsed}")
print(f"Histogram written to: {OUT_CSV}")