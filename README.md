9 Kunitz_HMM_prj
Laboratory of Bioinformatics project aiming at the generation of an HMM model for the annotation of the Kunitz domain. 
In this repository there are all the datasets, python scripts and the entire pipeline. The steps of the entire pipeline can be found inside the knz_prj.sh file.
To run this pipeline the following programms need to be installed:
- HMMER
- CD-HIT
- BLAST+

## 1. SELECTION OF THE TRAINING SET
### Advanced search on PDB DATABASE

+ Identifier - Pfam Protein Family = PF00014
+ Refinement Resolution <= 2.50
+ Polymer Entity Sequence Lenght = 49-90

The tabular report of the list of retrieved sequences was downloaded in CSV format.
