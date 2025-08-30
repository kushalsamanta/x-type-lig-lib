"""
Convert the JSON files to a CSV file, taking the intermediate 
steps at each 10th step to avoid similar structures
in our dataset.
"""
#!/usr/bin/env python3
import os
import json
import csv

# Define paths
base_dir = os.getcwd()
output_csv = os.path.join(base_dir, 'consolidated_data_10th_step.csv')
json_dir = os.path.join(base_dir, 'phosphorus_based_int_str')  # Path to intermediate JSON files

# CSV headers (unchanged)
headers = ["Structure", "Energy", "Forces", "Stress", "Directory", "Step"]

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

def select_steps_for_folder(entries, is_highest: bool):
    """
    entries: list of step_data dicts (must include 'step')
    Returns a filtered list according to the rules:
      - If len(entries) < 10: take only the last step (override skip-first-two).
      - Else: take every 10th step by 'step' value (step % 10 == 0),
              skipping the first two steps of this folder.
      - If is_highest: always include the last step.
    """
    # Normalize and sort by step (ensure integers)
    def parse_step(e):
        try:
            return int(e.get("step", -1))
        except Exception:
            return -1

    entries_sorted = sorted(entries, key=parse_step)
    if not entries_sorted:
        return []

    # < 10 steps: take last only
    if len(entries_sorted) < 10:
        return [entries_sorted[-1]]

    # ≥ 10 steps case
    first_two_steps = {parse_step(entries_sorted[0]), parse_step(entries_sorted[1])}
    selected = []
    seen = set()
    for e in entries_sorted:
        s = parse_step(e)
        if s in (-1,):
            continue
        if s in first_two_steps:
            continue
        if s % 10 == 0:
            key = s
            if key not in seen:
                selected.append(e)
                seen.add(key)

    # Always include the last step for the highest folder
    if is_highest:
        last_e = entries_sorted[-1]
        if last_e not in selected:
            selected.append(last_e)

    # Keep order by step
    selected = sorted(selected, key=parse_step)
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
                # Guard against missing essentials
                if gof is None or step is None:
                    continue
                groups.setdefault(gof, []).append(step_data)

            if not groups:
                continue

            # Determine the highest geo_opt folder present
            folder_indices = {gof: geo_idx(gof) for gof in groups.keys()}
            # Filter out unknown (idx==0) names
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

                    forces = step_data.get('forces', [])
                    forces_str = json.dumps(forces)

                    stresses = step_data.get('stress', [])
                    stresses_str = json.dumps(stresses)

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