# Kunitz_HMM_prj
Laboratory of Bioinformatics project aiming at the generation of an HMM model for the annotation of the Kunitz domain. 
In this repository there are all the datasets, python scripts and the entire pipeline. The steps of the entire pipeline can also be found inside the knz_prj.sh file.
To run this pipeline the following programms need to be installed:
- HMMER  3.3.2
- CD-HIT (version 4.8.1)
- BLAST+

```
conda create -n hmm_kunitz blast-legacy hmmer cd-hit 
```


## 1. SELECTION OF THE TRAINING SET
### Advanced search on PDB DATABASE
Select a representative training set of structurally defined proteins using the advanced search in the [RCSB PDB database](https://www.rcsb.org/) (wwPDB consortium, 2019). The constraints used in this project are: 
+ Identifier - Pfam Protein Family = PF00014
+ Refinement Resolution <= 2.50
+ Polymer Entity Sequence Lenght =  49-90 

- Customize a tabular report with the following field: ```PDB ID``` and ```Auth Asym ID```.
- Download the tabular report of the list of retrieved sequences  in CSV format. 
- Reformat this file using the following command:
```
tail -n +3 PDBnogrouping.csv | grep -v "^,," | tr -d \" > PDBnogrouping.tmp && mv PDBnogrouping.tmp PDBnogrouping
```
> - ```tail -n +3```: to get rid of the headers
> - ```grep -v "^,,"```: to delete the lines starting with ```,,```
> - ```tr -d \" ```: to delete the quotation marks 



To account for the redundancy of the PDB structures downloaded, it is necessary to perform a clustering procedure with CD-HIT. CD-HIT is  greedy incremental algorithm that starts with the longest input sequence as the first cluster representative and then processes the remaining sequences from long to short to classify each sequence as a redundant or representative sequence based on its similarities to the existing representatives (Fu et al., 2012).

### FASTA sequences download
Since the command takes in input FASTA files, FASTA sequences of the entities fetched from PDB need to be downloaded:
- extract from the tabular report the PDB ID
```
cut -d "," -f 2 PDBnogrouping.csv  > FASTA_to_download.list
```
- Using ```wget``` download the FASTA files, looping on the list previosuly computed and redirect all the sequences in a unique multi-FASTA file
 ```
for i in  `cat FASTA_to_download.list`; do wget https://www.rcsb.org/fasta/entry/$i ; done 
for i in `cat FASTA_to_download.list` ; do cat $i ; done > PDBnogrouping.fasta  
```
In this multi-FASTA there are the sequences of the entire entities, thus it is necessary to extract only the sequences of the target chain IDs, which can be retrieved from the tabular report:
```
cut -d "," -f 1 PDBnogrouping.csv > PDBchains_nogrouping.list 
```
To filter the multi-FASTA and exclude the chains we are not interested in, run the ``` filteringFASTA.py ``` Python script:
```
python3 filteringFASTA.py PDBchains_nogrouping.list PDBnogrouping.fasta filtered_PDBnogrouping.fasta
```

### CD-HIT clustering
The cluster was performed with a threshold of 95%
```
cd-hit -i filtered_PDBnogrouping.fasta -o seeds.fasta -c 0.95 
```

## 2. MSA AND HMM GENERATION
### Mulitple structure alignment
The representative list was submitted to [PDBeFold v2.59](https://www.ebi.ac.uk/msd-srv/ssm/) alignment program to obtain a multiple structure alignment (Krissinel and Henrick, 2004). 
To compile the list with the ```PDB ID``` + ```Auth Asym ID``` to upload on PDBeFold, it is necessary to extract the two fields from the tabular report. First we extract the entity IDs from the multi-FASTA, and then we retrieve the```PDB ID``` + ```Auth Asym ID``` pairs from the tabular report, using the ```extract_chainIDs_seeds.py```  :
```
grep '^>' seeds.fasta | cut -d "|" -f1 | cut -c2- > entityIDs_seeds.list
python extract_chainIDs_seeds.py entityIDs_seeds.list PDBnogrouping.csv training_seqs.list
```
### HMM generation
The resulting seed MSA is provided as input to hmmbuild function of HMMER 3.3.2. to obtain a profile-HMM (Finn et al., 2011)
```
hmmbuild kunitz.hmm seeds_MSA.seq
```
Visualize the profile HMM logo uploading the model on [Skylign](http://skylign.org/)
## 3. TEST SET GENERATION
Download the entire UniProtKB/Swiss-Prot database, containing 569516 sequence entries (release 2023_02 of 03-May-2023), which will be the test set to validate the model. To ensure a fair evaluation of the HMM model, proteins sharing a high level of sequence identity with the representatives need to be excluded from the test set. Identification of redundant proteins is carried out using the blastpgp program (Altschul et al., 1997).
```
makeblastdb -in uniprot_sprot.fasta -out $fasta_db -dbtype prot
blastpgp -i seeds.fasta -d uniprot_sprot.fasta -m 8 -o blastpgp_results.bl8
```
The output file is ranked based on the sequence identity value, and only the sequences that showed a S.I > 95% are selected and their UniProt IDs are copied into a new file.
```
sort -k 3 -n -r  blastpgp_results.bl8 > tmp && mv tmp blastpgp_results.bl8
awk '$3 >= 95.00' blastpgp_results.bl8 > morethan95%.bl8
awk -F '|' '{print $3}' morethan95%.bl8 > redundant_seqs.list
```
To check if all the representatives are detected by blastpgp, it is necessary to compare the list of the UniProt IDs of the representatives with the list of the redundant proteins found by blastpgp.
 1. Mapp the UniProt IDs of the representatives using the [ID Mapping tool](https://www.uniprot.org/id-mapping) provided by UniProt. Upload the list of the  ```PDB ID``` + ```Auth Asym ID``` pairs and mapp from PDB to UniProtKB/Swiss-Prot. Download the TSV file (mapped_IDs.tsv).
 2. Compare the two lists:
 ``` 
 comm <(sort redundant_seqs.list) <(sort  $ids_mapped)
 ```
 3. Merge the unique results of the two lists together:
 ``` 
 sort -u mapped_IDs.tsv redundant_seqs.list > toberemoved_seqs.list
 ```
 
Use the ``` rem_fasta_seqs.py ``` Python script to remove the redundant proteins from the test set:
```
python3 rem_fasta_seqs.py $ids_toremove uniprot_sprot.fasta swissprot_nonredundant.fasta

```

## 4. MODEL TESTING
To account for the influence of database size on the E-values, the ```hmmsearch``` command from the HMMER software was run
against the entire test set, with the option ```‘--max’``` which excludes all the heuristic filters
```
hmmsearch --cpu 4 --max --noali --tblout hmmsearch_results kunitz.hmm swissprot_nonredundant.fasta
```
From the results we only need the identifiers and the correspective E-values, to extract these fields:
```
grep -v "^#" hmmsearch_results | awk -v OFS="\t" '$1=$1' | cut -f1 | cut -d '|' -f 2 > id_list
grep -v "^#" hmmsearch_results| awk -v OFS="\t" '$1=$1' | cut -f5 > eval_list
paste id_list eval_list > parsed_hmmsearch_results && rm id_list eval_list 
```

## 5. SUBSETS CREATION
In order to validate the model, it is possible to create two equally sized subsets with an equal proportion of Kunitz and non-Kunitz proteins. To do so use the ```subsets-creation.py``` Python script. This script takes in input:
- hmmsearch output results (```parsed_hmmsearch_results```)
- file containing all the non-Kunitz proteins (```non_kunitz_ids.list```)
- file containing all the Kunitz proteins without the redundant ones (```allkunitz_nonredun_IDs.list```)

```
python subsets-creation.py parsed_hmmsearch_results allkunitz_nonredun_IDs.list non_kunitz_ids.list subset1 subset2 
```

Each protein in the subsets is associated with its corresponding e-value (obtained with the hmmsearch program) and label (0 or 1 
based on the absence or presence of the Kunitz domain, respectively). The labeling process and the reintroduction of those proteins (with a fictional e-value) which weren’t shown in the hmmsearch were performed by the Python script with a comparison between the results and the lists of Kunitz and non-Kunitz proteins.

>   To retrieve the files contaning the non-Kunitz and the Kunitz proteins present in UniProtKB/Swiss-Prot use the Advance search in [UniProt](https://www.uniprot.org/):
>  - Kunitz proteins: ```(reviewed:true) AND (xref:pfam-PF00014)``` => kunitz_ids.list
>  - non-Kunitz proteins:``` (reviewed:true) NOT (xref:pfam-PF00014)``` => non_kunitz_ids.list
>  Since the list of Kunitz proteins contains also the "redundant" ones, it is necessary to filter:
>  ```
>  grep -v -x -f toberemoved_seqs.list kunitz_ids.list > allkunitz_nonredun_IDs.list 
>  ```

## 6. E-VALUE OPTIMIZATION AND PERFORMANCE MEASUREMENT
To pick the optimal E-value, able to maximize the classification performance, carry out an optimization procedure on the two subsets derived from the random splitting of the whole test set. To do so use the ```performace.py``` Python script.

1. Loop for a range of E-values the script on the first subset
2. Pick the threshold that maximizes the MCC (Matthew's correlation coefficient)
3. Test it on the second subset
4. Swap the role of the two subsets

```
#optimization on subset1
for i in `seq 1 12`
do
python3 performance.py subset1 1e-$i 
done > optimization_results1.txt 

#testing on subset2
python performance.py subset2 <insert the best threshold on the other>

#optimization on subset2
for i in `seq 1 12`
do
python3 performance.py subset2 1e-$i 
done > optimization_results2.txt 

#testing on subset1
python performance.py subset1 <insert the best threshold on the other>

```
5. Test the model on the entire validation test using the average of the two best thresholds:
```
python performance.py <(cat subset1 subset2) <insert the average of the best thresholds of the optimizations> > final_results.txt
```
6. Visualize the results of the optimization and the performance using the ```graphs.py``` Python script
```
python graphs.py optimization_results1.txt optimization_results2.txt final_results.txt
```

> In these performance measurements the Matthews correlation coefficient (MCC) was adopted to evaluate the efficacy of the model. Indeed, MCC > is a measure unaffected by the unbalanced datasets issue (Chicco and Jurman, 2020).
