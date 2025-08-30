<h2><b>1) Extract all intermediate steps to JSON</b></h2>



<p align="justify">

&nbsp; <strong>Script:</strong>

&nbsp; <a href="./extract\_all\_intermediate\_info.py">extract\_all\_intermediate\_info.py</a><br><br>

&nbsp; Use this to extract all intermediate steps during DFT optimization for different structures into JSON files. <br><br>

&nbsp; Example: If you have a geo-opt record for <code>structure\_1</code> with intermediate steps in folders like

&nbsp; <code>geo\_opt</code>, <code>geo\_opt\_2</code>, <code>geo\_opt\_3</code>, and so on, then all coordinates,

&nbsp; energy, force, stress, lattice parameters, and volume from those steps will be saved into

&nbsp; <code>structure\_1.json</code>. <br><br>

&nbsp; The same applies to other structures (e.g., <code>structure\_2.json</code>). <br><br>

&nbsp; All JSON files will be saved in a single directory.

</p>



<hr/>



<h2><b>2) Inspect energy/force ranges before filtering</b></h2>

<p align="justify">

&nbsp; <strong>Script:</strong>

&nbsp; <a href="./energy\_force\_component\_distribution\_before\_filter.py">energy\_force\_component\_distribution\_before\_filter.py</a><br><br>

&nbsp; Use this to check the ranges of energy and force values for filtering. In early geo-opt steps, energies can be

&nbsp; very high (out of range) and not useful for the dataset; the same can happen for forces.

</p>



<hr/>



<h2><b>3) Take every 10th step and combine to a CSV</b></h2>

<p align="justify">

&nbsp; <strong>Script:</strong>

&nbsp; <a href="./combine\_to\_csv\_at\_each\_10th\_step.py">combine\_to\_csv\_at\_each\_10th\_step.py</a><br><br>

&nbsp; To avoid very similar consecutive structures, take every 10th step for each structure individually from the folder

&nbsp; created in Step 1. This script then combines all individual JSON files into a single CSV file.

</p>



<hr/>



<h2><b>4) Filter outliers by energy and forces</b></h2>

<p align="justify">

&nbsp; <strong>Script:</strong>

&nbsp; <a href="./filter\_en\_force.py">filter\_en\_force.py</a><br><br>

&nbsp; After you understand the distributions from Step 2, use this to filter out outliers in energy and force values

&nbsp; from the CSV produced in Step 3.

</p>



<hr/>



<h2 style="margin-bottom:8px;"><b>5) Visualize the filtered distributions</b></h2>

<p align="justify" style="margin:0;">

&nbsp; <strong>Script:</strong>

&nbsp; <a href="./plot\_energy\_force\_hist.py">plot\_energy\_force\_hist.py</a><br>

&nbsp; Visualize the distributions of the filtered CSV dataset file (energy and force components).

</p>



<p align="center" style="margin-top:6px;">

&nbsp; <a href="../IMG/"><img src="../IMG/energy.png" alt="Energy distribution histogram" width="49%"></a>

&nbsp; <a href="../IMG/"><img src="../IMG/forces.png" alt="Force component distributions (Fx, Fy, Fz)" width="49%"></a>

</p>



<hr/>



<h2><b>6) Deduplicate similar structures with StructureMatcher (pymatgen)</b></h2>

<p align="justify">

&nbsp; <strong>Tool script:</strong>

&nbsp; <a href="./structure\_matcher.py">structure\_matcher.py</a>

&nbsp; (uses <i>pymatgen</i>’s <code>StructureMatcher</code> and the <code>stol</code> parameter).<br><br>

&nbsp; Further filter the dataset after Step 4 by removing structurally similar entries using pymatgen’s StructureMatcher.

&nbsp; Tune the <code>stol</code> parameter to control how strictly similar structures are considered duplicates.

</p>

