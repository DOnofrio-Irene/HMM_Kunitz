# Kunitz_HMM_prj
Laboratory of Bioinformatics project aiming at the generation of an HMM model for the annotation of the Kunitz domain. 
In this repository there are all the datasets, python scripts and the entire pipeline. The steps of the entire pipeline can be found inside the knz_prj.sh file.
To run this pipeline the following programms need to be installed:
- HMMER  3.3.2
- CD-HIT (version 4.8.1)
- BLAST+

## 1. SELECTION OF THE TRAINING SET
### Advanced search on PDB DATABASE
The selection of a representative training set of structurally defined proteins was carried out by means of an advanced search in the RCSB PDB database. The constraints used were: 
+ Identifier - Pfam Protein Family = PF00014
+ Refinement Resolution <= 2.50
+ Polymer Entity Sequence Lenght =  49-90 

A tabular report was customized with the following field: ```PDB ID``` and ```Auth Asym ID```.
The tabular report of the list of retrieved sequences was downloaded in CSV format. This file was cleaned up using the following command:
```
tail -n +3 PDBnogrouping.csv | grep -v "^,," | tr -d \" > PDBnogrouping.tmp && mv PDBnogrouping.tmp PDBnogrouping
```
To account for the redundancy of the PDB structures downloaded, it was necessary to perform a clustering procedure with CD-HIT. CD-HIT is  greedy incremental algorithm that starts with the longest input sequence as the first cluster representative and then processes the remaining sequences from long to short to classify each sequence as a redundant or representative sequence based on its similarities to the existing representatives. 
Since the command takes in input FASTA files, it was necessary to download the FASTA sequences of the entities downloaded from PDB.
- extract from the tabular report the PDB ID
```
cut -d "," -f 2 $PDBstructures  > FASTA_to_download.list
```



