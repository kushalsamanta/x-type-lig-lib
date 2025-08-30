<h1 align="left"><b>Sequential Pipeline for Preparing the DFT Geo-Optimization Dataset</b></h1>



<p align="justify">

Follow these steps in order.

</p>



<hr/>



<h2><b>1) Extract all intermediate steps to JSON</b></h2>



<p align="justify">



<strong>Script:</strong> <code><a href="./extract-all-intermediate-info.py">extract-all-intermediate-info.py</a></code> <br><br>

Use this to extract all intermediate steps during DFT optimization for different structures into JSON files. <br><br>

Example: If you have a geo-opt record for <code>structure\_1</code> with intermediate steps in folders like <code>geo\_opt</code>, <code>geo\_opt\_2</code>, <code>geo\_opt\_3</code>, and so on, then all coordinates, energy, force, stress, lattice parameters, and volume from those steps will be saved into <code>structure\_1.json</code>. <br><br>

The same applies to other structures (e.g., <code>structure\_2.json</code>). <br><br>

All JSON files will be saved in a single directory.



</p>



<hr/>



<h2><b>2) Inspect energy/force ranges before filtering</b></h2>



<p align="justify">



<strong>Script:</strong> <code><a href="./energy-force-component-distribution-before-filter.py">energy-force-component-distribution-before-filter.py</a></code> <br><br>

Use this to check the ranges of energy and force values for filtering. <br><br>

In early geo-opt steps, energies can be very high (out of range) and not useful for the dataset; the same can happen for forces.



</p>



<hr/>



<h2><b>3) Take every 10th step and combine to a CSV</b></h2>



<p align="justify">



<strong>Script:</strong> <code><a href="./combine-to-csv-at-each-10th-step.py">combine-to-csv-at-each-10th-step.py</a></code><br><br>

To avoid very similar consecutive structures, take every 10th step for each structure individually from the folder created in Step 1. <br><br>

This script then combines all individual JSON files into a single CSV file.



</p>



<hr/>



<h2><b>4) Filter outliers by energy and forces</b></h2>

<p align="justify">

&nbsp; <strong>Script:</strong> <code><a href="./filter-en-force.py">filter-en-force.py</a></code> <br><br>      

&nbsp; After you understand the distributions from Step 2, use this to filter out outliers in energy and force values

&nbsp; from the CSV produced in Step 3.

</p>



<hr/>



<h2 style="margin-bottom:8px;"><b>5) Visualize the filtered distributions</b></h2>



<p align="justify" style="margin:0;">

&nbsp; <strong>Script:</strong> <code><a href="./plot-energy-force-hist.py">plot-energy-force-hist.py</a></code><br>

&nbsp; Visualize the distributions of the filtered CSV dataset file (energy and force components) to confirm the filtering looks sensible.

</p>

<table style="width:100%; border-collapse:collapse; margin:0;">

&nbsp; <tr>

&nbsp;   <td align="center" width="50%" style="padding:0;">

&nbsp;     <img src="../IMG/energy.png" alt="Energy distribution histogram" width="98%" style="vertical-align:middle;">

&nbsp;   </td>

&nbsp;   <td align="center" width="50%" style="padding:0;">

&nbsp;     <img src="../IMG/forces.png" alt="Force component distributions (Fx, Fy, Fz)" width="98%" style="vertical-align:middle;">

&nbsp;   </td>

&nbsp; </tr>

</table>



<hr/>



<h2><b>6) Deduplicate similar structures with StructureMatcher (pymatgen)</b></h2>



<p align="justify">



<strong>Script:</strong> <code><a href="./structure-matcher.py">structure-matcher.py</a></code><br> (from <i>pymatgen</i>) 

using the <code>stol</code> parameter <br><br>

Further filter the dataset after Step 4 by removing structurally similar entries using pymatgen’s StructureMatcher. <br><br>

Tune the <code>stol</code> parameter to control how strictly similar structures are considered duplicates.



</p>



