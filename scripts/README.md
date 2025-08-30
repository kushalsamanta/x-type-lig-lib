\# Sequential Pipeline for Preparing the DFT Geo-Optimization Dataset



Follow these steps in order.



---



\## 1) Extract all intermediate steps to JSON



\*\*Script:\*\* \[`extract\_all\_intermediate\_info.py`](./extract\_all\_intermediate\_info.py)



Use this to extract all intermediate steps during DFT optimization for different structures into JSON files.



Example: If you have a geo-opt record for `structure\_1` with intermediate steps in folders like `geo\_opt`, `geo\_opt\_2`, `geo\_opt\_3`, and so on, then all coordinates, energy, force, stress, lattice parameters, and volume from those steps will be saved into `structure\_1.json`.



The same applies to other structures (e.g., `structure\_2.json`).



All JSON files will be saved in a single directory.



---



\## 2) Inspect energy/force ranges before filtering



\*\*Script:\*\* \[`energy\_force\_component\_distribution\_before\_filter.py`](./energy\_force\_component\_distribution\_before\_filter.py)



Use this to check the ranges of energy and force values for filtering.



In early geo-opt steps, energies can be very high (out of range) and not useful for the dataset; the same can happen for forces.



---



\## 3) Take every 10th step and combine to a CSV



\*\*Script:\*\* \[`combine\_to\_csv\_at\_each\_10th\_step.py`](./combine\_to\_csv\_at\_each\_10th\_step.py)



To avoid very similar consecutive structures, take every 10th step for each structure individually from the folder created in Step 1.



This script then combines all individual JSON files into a single CSV file.



---



\## 4) Filter outliers by energy and forces



\*\*Script:\*\* \[`filter\_en\_force.py`](./filter\_en\_force.py)



After you understand the distributions from Step 2, use this to filter out outliers in energy and force values from the CSV produced in Step 3.



---



\## 5) Visualize the filtered distributions



\*\*Script:\*\* \[`plot\_energy\_force\_hist.py`](./plot\_energy\_force\_hist.py)



Visualize the distributions of the filtered CSV dataset file (energy and force components) to confirm the filtering looks sensible.



\[Open images folder](../IMG/)



| \[!\[Energy distribution histogram](../IMG/energy.png)](../IMG/) | \[!\[Force component distributions (Fx, Fy, Fz)](../IMG/forces.png)](../IMG/) |

|:--:|:--:|

| Energy distribution | Force component distributions (Fx, Fy, Fz) |



---



\## 6) Deduplicate similar structures with StructureMatcher (pymatgen)



\*\*Tool script:\*\* \[`structure\_matcher.py`](./structure\_matcher.py) (uses `pymatgen.StructureMatcher` and the `stol` parameter)



Further filter the dataset after Step 4 by removing structurally similar entries using pymatgen’s StructureMatcher.



Tune the `stol` parameter to control how strictly similar structures are considered duplicates.



