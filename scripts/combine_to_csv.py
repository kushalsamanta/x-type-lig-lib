""" 
combines all the JSON files into a single CSV file

"""

import os
import json
import csv
import pandas as pd
from pymatgen.core import Structure

# Define paths
base_dir = os.getcwd()
output_csv = os.path.join(base_dir, 'consolidated_data_nc.csv')
json_dir = os.path.join(base_dir, 'phosphorus_based_int_str')  # Path to intermediate JSON files

# Define column headers for the CSV file
headers = ["Structure", "Energy", "Forces", "Stress", "Directory", "Step"]

# Open the CSV file in write mode
with open(output_csv, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headers)  # Write headers

    # Process each JSON file in the all_intermediate_information directory
    for json_filename in os.listdir(json_dir):
        if json_filename.endswith('.json'):
            json_path = os.path.join(json_dir, json_filename)
            try:
                with open(json_path, 'r') as json_file:
                    data = json.load(json_file)
                    if not isinstance(data, list):
                        continue
                    directory_name = json_filename.replace('.json', '')

                    for step_data in data:
                        structure_info = step_data.get('structure', {})
                        if not structure_info:
                            continue
                        structure_str = json.dumps(structure_info)
                        energy = step_data.get('energy', "N/A")

                        forces = step_data.get('forces', [])
                        forces_str = json.dumps(forces)
                        stresses = step_data.get('stress', [])
                        stresses_str = json.dumps(stresses)

                        writer.writerow([
                            structure_str,                # Structure in JSON format
                            energy,                       # Energy
                            forces_str,                   # Forces in JSON format
                            stresses_str,                 # Stresses in JSON format
                            directory_name,               # Directory
                            step_data.get('step', 0)      # Step
                        ])
            except json.JSONDecodeError:
                print(f"Error reading JSON file at {json_path}")
            except Exception as e:
                print(f"An error occurred: {e}")

print(f"Consolidated data saved to {output_csv}")