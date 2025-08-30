!\[alt text](https://img.shields.io/github/actions/workflow/status/kushalsamanta/x-type-lig-lib/main.yml?branch=main)

!\[GitHub tag (latest by date)](https://img.shields.io/github/v/tag/kushalsamanta/x-type-lig-lib)

!\[GitHub code size in bytes](https://img.shields.io/github/languages/code-size/kushalsamanta/x-type-lig-lib)

!\[GitHub commit activity](https://img.shields.io/github/commit-activity/y/kushalsamanta/x-type-lig-lib)



\# Table of Contents

\* \[Introduction](#intro)

\* \[Pipeline overview](#overview)

\* \[Step 1 — Extract all intermediate steps to JSON](#step1)

\* \[Step 2 — Inspect energy/force ranges (pre-filter)](#step2)

\* \[Step 3 — Take every 10th step and combine to CSV](#step3)

\* \[Step 4 — Filter outliers by energy \& forces](#step4)

\* \[Step 5 — Visualize filtered distributions](#step5)

\* \[Step 6 — Deduplicate similar structures (StructureMatcher)](#step6)

\* \[Images](#images)

\* \[Repo layout](#layout)

\* \[Notes](#notes)



<a name="intro"></a>

\# DFT Geo-Optimization Dataset Pipeline (Introduction)



This repository provides a small, repeatable workflow to curate datasets from \*\*DFT geometry-optimization\*\* runs:

1\) extract all ionic steps, 2) inspect value ranges, 3) thin near-duplicates, 4) filter outliers, 5) visualize clean histograms, and 6) deduplicate similar structures using `pymatgen.StructureMatcher`.



<a name="overview"></a>

\## Pipeline overview



1\. \*\*Extract\*\* all intermediate geo-opt steps → per-structure JSON  

2\. \*\*Inspect\*\* energy \& force ranges before filtering  

3\. \*\*Thin\*\* by keeping \*\*every 10th\*\* ionic step and \*\*combine\*\* → CSV  

4\. \*\*Filter\*\* outliers by energy and per-component forces  

5\. \*\*Visualize\*\* histograms for energy and forces  

6\. \*\*Deduplicate\*\* similar structures (StructureMatcher `stol`)



---



<a name="step1"></a>

\## Step 1 — Extract all intermediate steps to JSON



\*\*Script:\*\* \[`scripts/extract\_all\_intermediate\_info.py`](scripts/extract\_all\_intermediate\_info.py)



Use this to extract all intermediate steps during DFT optimization for different structures into JSON files.



\*\*Example:\*\* If you have a geo-opt record for `structure\_1` with intermediate steps in folders like `geo\_opt`, `geo\_opt\_2`, `geo\_opt\_3`, and so on, then all \*\*coordinates\*\*, \*\*energy\*\*, \*\*force\*\*, \*\*stress\*\*, \*\*lattice parameters\*\*, and \*\*volume\*\* from those steps will be saved into `structure\_1.json`.  

The same applies to other structures (e.g., `structure\_2.json`). All JSON files will be saved in a single directory.



---



<a name="step2"></a>

\## Step 2 — Inspect energy/force ranges (pre-filter)



\*\*Script:\*\* \[`scripts/energy\_force\_component\_distribution\_before\_filter.py`](scripts/energy\_force\_component\_distribution\_before\_filter.py)



Use this to check the ranges of \*\*energy\*\* and \*\*force\*\* values for filtering. Early geo-opt steps can have very high energies/forces that are not useful for the dataset.



---



<a name="step3"></a>

\## Step 3 — Take every 10th step and combine to CSV



\*\*Script:\*\* \[`scripts/combine\_to\_csv\_at\_each\_10th\_step.py`](scripts/combine\_to\_csv\_at\_each\_10th\_step.py)



To avoid very similar consecutive structures, take \*\*every 10th step\*\* for each structure individually (from the directory created in Step 1).  

This script then \*\*combines\*\* all per-structure JSON files into a \*\*single CSV\*\*.



---



<a name="step4"></a>

\## Step 4 — Filter outliers by energy \& forces



\*\*Script:\*\* \[`scripts/filter\_en\_force.py`](scripts/filter\_en\_force.py)



After you understand the distributions from Step 2, use this to filter out outliers in \*\*energy\*\* and \*\*per-component forces (Fx, Fy, Fz)\*\* from the CSV produced in Step 3.



---



<a name="step5"></a>

\## Step 5 — Visualize filtered distributions



\*\*Script:\*\* \[`scripts/plot\_energy\_force\_hist.py`](scripts/plot\_energy\_force\_hist.py)



Visualize the distributions of the filtered CSV dataset (energy and force components) to confirm the filtering looks sensible.



| !\[Energy distribution histogram](IMG/energy.png) | !\[Force component distributions (Fx, Fy, Fz)](IMG/forces.png) |

|:--:|:--:|

| Energy distribution | Force component distributions (Fx, Fy, Fz) |



\*(If your actual filenames are `energy\_hist.png` / `forces\_hist.png`, change the paths to `IMG/energy\_hist.png` and `IMG/forces\_hist.png`.)\*



---



<a name="step6"></a>

\## Step 6 — Deduplicate similar structures (StructureMatcher)



\*\*Tool script:\*\* \[`scripts/structure\_matcher.py`](scripts/structure\_matcher.py)



Uses `pymatgen.StructureMatcher` (tune the `stol` parameter) to remove structurally similar entries after Step 4.  

Keep the \*\*more negative energy\*\* (more stable) when two structures match.



---



<a name="images"></a>

\## Images



\- `IMG/energy.png`  

\- `IMG/forces.png`  



---



<a name="layout"></a>

\## Repo layout





