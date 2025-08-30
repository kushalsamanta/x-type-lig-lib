<h1 align="left"><b>Sequential Pipeline for Preparing the DFT Geo-Optimization Dataset</b></h1>



<p align="justify">

Follow these steps in order.

</p>



<hr/>



<h2><b>1) Extract all intermediate steps to JSON</b></h2>



<p align="justify">



<strong>Script:</strong> <code>extract\_all\_intermediate\_info.py</code> <br><br>

Use this to extract all intermediate steps during DFT optimization for different structures into JSON files. <br><br>

Example: If you have a geo-opt record for <code>structure\_1</code> with intermediate steps in folders like <code>geo\_opt</code>, <code>geo\_opt\_2</code>, <code>geo\_opt\_3</code>, and so on, then all coordinates, energy, force, stress, lattice parameters, and volume from those steps will be saved into <code>structure\_1.json</code>. <br><br>

The same applies to other structures (e.g., <code>structure\_2.json</code>). <br><br>

All JSON files will be saved in a single directory.



</p>



<hr/>



<h2><b>2) Inspect energy/force ranges before filtering</b></h2>



<p align="justify">



<strong>Script:</strong> <code>energy\_force\_component\_distribution\_before\_filter.py</code> <br><br>

Use this to check the ranges of energy and force values for filtering. <br><br>

In early geo-opt steps, energies can be very high (out of range) and not useful for the dataset; the same can happen for forces.



</p>



<hr/>



<h2><b>3) Take every 10th step and combine to a CSV</b></h2>



<p align="justify">



<strong>Script:</strong> <code>combine\_to\_csv\_at\_each\_10th\_step.py</code> <br><br>

To avoid very similar consecutive structures, take every 10th step for each structure individually from the folder created in Step 1. <br><br>

This script then combines all individual JSON files into a single CSV file.



</p>



<hr/>



<h2><b>4) Filter outliers by energy and forces</b></h2>



<p align="justify">



<strong>Script:</strong> <code>filter\_en\_force.py</code> <br><br>

After you understand the distributions from Step 2, use this to filter out outliers in energy and force values from the CSV produced in Step 3.



</p>



<hr/>



<h2><b>5) Visualize the filtered distributions</b></h2>

<p><strong>Script:</strong> <code>plot\_energy\_force\_hist.py</code><br>

Visualize the distributions of the filtered CSV dataset file (energy and force components) to confirm the filtering looks sensible.</p>



<p align="center">

&nbsp; <img src="../IMG/energy.png" alt="Energy distribution histogram" width="49%"> 

&nbsp; <img src="../IMG/forces.png" alt="Force component distributions (Fx, Fy, Fz)" width="49%">

</p>

<hr/>



<h2><b>6) Deduplicate similar structures with StructureMatcher (pymatgen)</b></h2>



<p align="justify">



<strong>Tool:</strong> <code>StructureMatcher</code> (from <i>pymatgen</i>) using the <code>stol</code> parameter <br><br>

Further filter the dataset after Step 4 by removing structurally similar entries using pymatgen’s StructureMatcher. <br><br>

Tune the <code>stol</code> parameter to control how strictly similar structures are considered duplicates.



</p>



