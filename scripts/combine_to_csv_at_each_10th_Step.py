"""
We convert the JSON files to a CSV file, and we take the 
Intermediate steps at each 10th step (vary the step
size accordingly), to avoid the very similar structures
for our dataset.
"""

#!/usr/bin/env python3
import os
import json
import csv

# Define paths
base_dir = os.getcwd()
output_csv = os.path.join(base_dir, 'consolidated_data_mol_plus_nc.csv')
json_dir = os.path.join(base_dir, 'phosphorus_based_int_str')  # Path to intermediate JSON files

# CSV headers (unchanged)
headers = ["Structure", "Energy", "Forces", "Stress", "Directory", "Step"]

SAMPLE_EVERY = 10
GAP_THRESHOLD = 5  # include highest folder's last step if >5 beyond last sampled

def geo_idx(name: str) -> int:
    """
    Map geo_opt folder name to an index:
      'geo_opt' -> 1
      'geo_opt_2' -> 2, etc.
    Unknown formats return 0.
    """
    if name == "geo_opt":
        return 1
    if name.startswith("geo_opt_"):
        try:
            return int(name.split("_")[2])
        except Exception:
            return 0
    return 0

def parse_step(val):
    try:
        return int(val)
    except Exception:
        return -1

def select_steps_for_folder(entries, is_highest: bool, sample_every=SAMPLE_EVERY, gap_threshold=GAP_THRESHOLD):
    """
    entries: list of dicts with at least 'step'
    Rules:
      - If len(entries) < 10: take only the last step.
      - Else (>=10):
          * skip the first two steps in this folder,
          * take every `sample_every`th step by step number (step % sample_every == 0),
          * if is_highest:
              include the last step too ONLY IF (last_step - last_sampled_step) > gap_threshold
              (if no sampled steps exist, include the last step).
    """
    entries_sorted = sorted(entries, key=lambda e: parse_step(e.get("step", -1)))
    if not entries_sorted:
        return []

    # < 10 steps: just take the last
    if len(entries_sorted) < 10:
        return [entries_sorted[-1]]

    # >= 10 steps: sample each 10th, skipping the first two steps
    first_two = {parse_step(entries_sorted[0].get("step", -1)),
                 parse_step(entries_sorted[1].get("step", -1))}
    selected = []
    selected_steps = set()

    for e in entries_sorted:
        s = parse_step(e.get("step", -1))
        if s < 0:
            continue
        if s in first_two:
            continue
        if s % sample_every == 0:
            if s not in selected_steps:
                selected.append(e)
                selected_steps.add(s)

    # Highest folder: possibly include the very last step if it’s far enough beyond last sampled
    if is_highest:
        last_e = entries_sorted[-1]
        last_s = parse_step(last_e.get("step", -1))
        # If nothing sampled, include last
        if not selected_steps:
            if last_s >= 0:
                selected.append(last_e)
        else:
            max_sampled = max(selected_steps)
            if last_s - max_sampled > gap_threshold:
                # include last if not already there
                if last_e not in selected:
                    selected.append(last_e)

    # Keep order by step
    selected = sorted(selected, key=lambda e: parse_step(e.get("step", -1)))
    return selected

# Open the CSV file in write mode
with open(output_csv, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headers)  # Write headers

    # Process each JSON file in the directory
    for json_filename in os.listdir(json_dir):
        if not json_filename.endswith('.json'):
            continue

        json_path = os.path.join(json_dir, json_filename)
        try:
            with open(json_path, 'r') as json_file:
                data = json.load(json_file)

            if not isinstance(data, list):
                continue

            directory_name = json_filename.replace('.json', '')

            # Group by geo_opt_folder
            groups = {}
            for step_data in data:
                gof = step_data.get("geo_opt_folder")
                step = step_data.get("step", None)
                if gof is None or step is None:
                    continue
                groups.setdefault(gof, []).append(step_data)

            if not groups:
                continue

            # Determine the highest geo_opt folder present
            folder_indices = {gof: geo_idx(gof) for gof in groups.keys()}
            valid_folders = {gof: idx for gof, idx in folder_indices.items() if idx > 0}
            if not valid_folders:
                continue
            highest_folder = max(valid_folders, key=lambda k: valid_folders[k])

            # Select entries per folder and write rows
            for gof, entries in groups.items():
                is_highest = (gof == highest_folder)
                selected_entries = select_steps_for_folder(entries, is_highest=is_highest)

                for step_data in selected_entries:
                    structure_info = step_data.get('structure', {})
                    if not structure_info:
                        continue
                    structure_str = json.dumps(structure_info)

                    energy = step_data.get('energy', "N/A")
                    forces_str = json.dumps(step_data.get('forces', []))
                    stresses_str = json.dumps(step_data.get('stress', []))
                    step_val = step_data.get('step', 0)

                    writer.writerow([
                        structure_str,          # Structure in JSON format
                        energy,                 # Energy
                        forces_str,             # Forces in JSON format
                        stresses_str,           # Stress in JSON format
                        directory_name,         # Directory (from JSON file name)
                        step_val                # Step
                    ])

        except json.JSONDecodeError:
            print(f"Error reading JSON file at {json_path}")
        except Exception as e:
            print(f"An error occurred for {json_path}: {e}")

print(f"Consolidated data saved to {output_csv}")