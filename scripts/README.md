Sequential Pipeline for Preparing the DFT Geo-Optimization Dataset

<p align="justify"> Use the following workflow to extract, inspect, filter, visualize, and deduplicate structures from DFT geometry-optimization runs. Follow the steps <b>in order</b>. </p>

1\) Extract all intermediate steps → JSON



Script: extract\_all\_intermediate\_info.py



<p align="justify"> Use this to extract <i>all intermediate steps</i> during DFT optimization for different structures into JSON files. For example, if you have a geo-opt record for <code>structure\_1</code> with intermediate steps in folders like <code>geo\_opt</code>, <code>geo\_opt\_2</code>, <code>geo\_opt\_3</code>, and so on, then all <b>coordinates</b>, <b>energy</b>, <b>force</b>, <b>stress</b>, <b>lattice parameters</b>, and <b>volume</b> from those steps will be saved into <code>structure\_1.json</code>. The same applies to other structures (e.g., <code>structure\_2.json</code>). All JSON files will be saved in a single directory. </p>

2\) Inspect energy/force ranges before filtering



Script: energy\_force\_component\_distribution\_before\_filter.py



<p align="justify"> Use this to check the ranges of <b>energy</b> and <b>force</b> values for filtration. In early geo-opt steps, energies can be very high (out of range) and not useful for the dataset; the same can happen for forces. </p>

3\) Take every 10th step and combine to a CSV



Script: combine\_to\_csv\_at\_each\_10th\_step.py



<p align="justify"> To avoid very similar consecutive structures, take <b>every 10th step</b> for each structure individually from the folder created in Step\&nbsp;1. This script then combines all individual JSON files into a single CSV file. </p>

4\) Filter outliers by energy and forces



Script: filter\_en\_force.py



<p align="justify"> After you understand the distributions from Step\&nbsp;2, use this to filter out outliers in <b>energy</b> and <b>force</b> values from the CSV produced in Step\&nbsp;3. </p>

5\) Visualize the filtered distributions



Script: plot\_energy\_force\_hist.py



<p align="justify"> Visualize the distributions of the filtered CSV dataset file (energy and force components) to confirm the filtering looks sensible. </p>

6\) Deduplicate similar structures with StructureMatcher (pymatgen)



Tool: StructureMatcher from pymatgen (tune the stol parameter)



<p align="justify"> Further filter the dataset after Step\&nbsp;4 by removing structurally similar entries using <i>pymatgen</i>’s StructureMatcher. Tune the <code>stol</code> parameter to control how strictly similar structures are considered duplicates. </p> ::contentReference\[oaicite:0]{index=0}

