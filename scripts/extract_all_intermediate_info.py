#This is script to extract the informations from the geometric optimization steps of DFT simulations. It extracts the Energy of the structure at each intermediate state as well the forces per atom (all three components), stress values, lattice parameters a, b, and c, as well the volume of the system.

import os
import json
import re
from lxml import etree

# Get current working directory
base_dir = os.getcwd()

# Output directory for intermediate data
output_dir = os.path.join(base_dir, "all_intermediate_information")
os.makedirs(output_dir, exist_ok=True)

# Function to process a vasprun.xml file
def process_vasprun(vasprun_path):
    intermediate_data = []

    try:
        with open(vasprun_path, 'rb') as f:
            parser = etree.XMLParser(recover=True)
            tree = etree.parse(f, parser)
            root = tree.getroot()

            atom_count = int(root.findtext(".//atominfo/atoms"))
            elements = [el.text for el in root.findall(".//atominfo/array[@name='atoms']/set/rc/c[1]")]
            species_list = elements * (atom_count // len(elements))

            cell_parameters = root.findall(".//structure/crystal/varray[@name='basis']/v")
            cell_parameters = [list(map(float, v.text.strip().split())) for v in cell_parameters[:3]]

            a = (cell_parameters[0][0]**2 + cell_parameters[0][1]**2 + cell_parameters[0][2]**2)**0.5
            b = (cell_parameters[1][0]**2 + cell_parameters[1][1]**2 + cell_parameters[1][2]**2)**0.5
            c = (cell_parameters[2][0]**2 + cell_parameters[2][1]**2 + cell_parameters[2][2]**2)**0.5
            alpha, beta, gamma = 90.0, 90.0, 90.0
            volume = abs(a * b * c)

            for step_index, calculation in enumerate(root.findall(".//calculation")):
                energy_tags = calculation.findall(".//energy")
                if energy_tags:
                    last_energy_tag = energy_tags[-1]
                    energy_elem = last_energy_tag.find(".//i[@name='e_fr_energy']") or \
                                  last_energy_tag.find(".//i[@name='e_wo_entrp']") or \
                                  last_energy_tag.find(".//i[@name='e_0_energy']")
                    energy = float(energy_elem.text.strip()) if energy_elem is not None else None
                else:
                    energy = None

                forces = calculation.findall(".//varray[@name='forces']/v")
                forces = [list(map(float, v.text.strip().split())) for v in forces]

                stress_values = calculation.findall(".//varray[@name='stress']/v")
                stress = [list(map(float, v.text.strip().split())) for v in stress_values[:3]] if len(stress_values) >= 3 else []

                coordinates = calculation.findall(".//varray[@name='positions']/v")
                coordinates = [list(map(float, v.text.strip().split())) for v in coordinates]

                sites = [
                    {
                        "species": [{"element": species_list[idx], "occu": 1}],
                        "abc": coord,
                        "properties": {},
                        "label": species_list[idx],
                        "xyz": [
                            coord[0] * cell_parameters[0][0] + coord[1] * cell_parameters[1][0] + coord[2] * cell_parameters[2][0],
                            coord[0] * cell_parameters[0][1] + coord[1] * cell_parameters[1][1] + coord[2] * cell_parameters[2][1],
                            coord[0] * cell_parameters[0][2] + coord[1] * cell_parameters[1][2] + coord[2] * cell_parameters[2][2],
                        ]
                    }
                    for idx, coord in enumerate(coordinates)
                ]

                intermediate_data.append({
                    "geo_opt_folder": os.path.basename(os.path.dirname(vasprun_path)),
                    "step": step_index,
                    "structure": {
                        "@module": "pymatgen.core.structure",
                        "@class": "Structure",
                        "charge": 0.0,
                        "lattice": {
                            "matrix": cell_parameters,
                            "pbc": [True, True, True],
                            "a": a,
                            "b": b,
                            "c": c,
                            "alpha": alpha,
                            "beta": beta,
                            "gamma": gamma,
                            "volume": volume
                        },
                        "properties": {},
                        "sites": sites
                    },
                    "forces": forces,
                    "stress": stress,
                    "energy": energy
                })

    except Exception:
        pass

    return intermediate_data

# Regex pattern to match folders starting with numbers
folder_pattern = re.compile(r'^\d+')

# List all folders in the current directory that start with numbers
folders_to_process = [f for f in os.listdir(base_dir) if os.path.isdir(f) and folder_pattern.match(f)]

for folder in folders_to_process:
    folder_path = os.path.join(base_dir, folder)
    geo_opt_folders = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d)) and re.match(r'geo_opt(_\d+)?$', d)]

    combined_data = []
    for geo_opt_folder in geo_opt_folders:
        geo_opt_path = os.path.join(folder_path, geo_opt_folder)
        vasprun_path = os.path.join(geo_opt_path, "vasprun.xml")

        if os.path.isfile(vasprun_path):
            combined_data.extend(process_vasprun(vasprun_path))

    if combined_data:
        output_json_path = os.path.join(output_dir, f"{folder}_intermediate_data.json")
        with open(output_json_path, 'w') as json_file:
            json.dump(combined_data, json_file, indent=4)