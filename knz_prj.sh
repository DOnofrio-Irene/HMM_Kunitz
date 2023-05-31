#!/bin/sh

#pipeline to build an HMM for Kunitz domain annotation

#-----------------------------------------------------------------------------------------------------------
#- SELECTION OF THE TRAINING SET -
#- Downloaded csv ofmthe tabular report of the results of the advanced search on PDB
PDBstructures='PDBnogrouping.csv'  

#- cleanup of the csv file (removal of the header, deletion of those lines starting with ',,' to take into account only the first chain, removal of the quotes)
tail -n +3 $PDBstructures | grep -v "^,," | tr -d \" > $PDBstructures.tmp && mv $PDBstructures.tmp $PDBstructures

#- clustering using cd-hit 
#- FASTA files download (in order to do this, we need only the PDB ID without specifying the chain)
cut -d "," -f 2 $PDBstructures  > FASTA_to_download.list
cd singleFASTA
for i in  `cat ../FASTA_to_download.list`; do wget https://www.rcsb.org/fasta/entry/$i ; done 
for i in `cat ../FASTA_to_download.list` ; do cat $i ; done > ../PDBnogrouping.fasta  
cd ..
#- filtering the target chains, using the first field contained in the csv file downloaded from PDB
cut -d "," -f 1 $PDBstructures > PDBchains_nogrouping.list 
#- python script to filter the FASTA sequences to exclude the chains not of interest 
python3 filteringFASTA.py PDBchains_nogrouping.list PDBnogrouping.fasta filtered_PDBnogrouping.fasta
#- cd-hit command to cluster
cd-hit -i filtered_PDBnogrouping.fasta -o seeds.fasta -c 0.95 

#-----------------------------------------------------------------------------------------------------------
#- MSA GENERATION with PDBeFold webserver -
#- PDBefold takes in input the list of the PDB ID + Auth Asym ID: 
grep '^>' seeds.fasta | cut -d "|" -f1 | cut -c2- > entityIDs_seeds.list
python extract_chainIDs_seeds.py entityIDs_seeds.list $PDBstructures training_seqs.list
#- Launch PDBefold for a multiple sequence alignment with the training_seqs.list 

#-----------------------------------------------------------------------------------------------------------
#- HMM GENERATION -
hmmbuild kunitz.hmm seeds_MSA.seq

#-----------------------------------------------------------------------------------------------------------
#- TEST SET PREPARATION - 

#- download ids list of non_kuntiz (#569126) and kunitz(#390) (PF00014) from UniProtKB/Swiss-Prot
#- download FASTA of non_kuntiz (#569126) and kunitz(#390) (PF00014) from UniProtKB/Swiss-Prot

kunitz_ids='allkunitz_IDs.list'
non_kunitz_ids='all_nonkunitz_IDs.list'

kunitz_fasta='allkunitz.fasta'
non_kunitz_fasta='all_non_kunitz.fasta'
#- remove col name
tail +2 $non_kunitz_ids  > $non_kunitz_ids.tmp && mv $non_kunitz_ids.tmp $non_kunitz_ids
tail +2 $kunitz_ids  > $kunitz_ids.tmp && mv $kunitz_ids.tmp $kunitz_ids

#- mapp to UniProtKB/Swiss-Prot PDB IDs of proteins used for training hmm mapping to UniProtKB/Swiss-Prot (UNIPROT mapping tool)
https://www.uniprot.org/id-mapping

ids_mapped='mapped_IDs.tsv' 
#- remove header
tail +2 $ids_mapped | cut -f 2 > $ids_mapped.tmp && mv $ids_mapped.tmp $ids_mapped 


#- find high similar seqS in the test set(UniProtKB/Swiss-Prot) using blastpgb  (for a fair test of the HMM)
fasta_db='uniprot_sprot.fasta' #569516
makeblastdb -in $fasta_db -out $fasta_db -dbtype prot
blastpgp -i seeds.fasta -d $fasta_db -m 8 -o blastpgp_results.bl8

#- rank based on the sequence identity value
sort -k 3 -n -r  blastpgp_results.bl8 > tmp && mv tmp blastpgp_results.bl8
#- select only the sequences that got a S.I. > 95% and copy the UniProt IDs into a new file
awk '$3 >= 95.00' blastpgp_results.bl8 > morethan95%.bl8
awk -F '|' '{print $3}' morethan95%.bl8 > redundant_seqs.list

#- check if all the sequences used for the training are removed from the set test, to do so compare the mapped_IDs list with the IDs obtained from the 95% filtering with blastpgp
comm <(sort redundant_seqs.list) <(sort  $ids_mapped)  

#- create the list of redundant sequences to be removed, merging the two unique results
ids_toremove='toberemoved_seqs.list'
sort -u $ids_mapped redundant_seqs.list > $ids_toremove

#- using a python script remove the  redundant sequences from the test set
python3 rem_fasta_seqs.py $ids_toremove uniprot_sprot.fasta swissprot_nonredundant.fasta


#-----------------------------------------------------------------------------------------------------------
# - MODEL TESTING -
#- run hmmsearch on the test set
hmmsearch --cpu 4 --max --noali --tblout hmmsearch_results kunitz.hmm swissprot_nonredundant.fasta

#- extract only ID and e-val columns from the hmmsearch results file
grep -v "^#" hmmsearch_results | awk -v OFS="\t" '$1=$1' | cut -f1 | cut -d '|' -f 2 > id_list
grep -v "^#" hmmsearch_results| awk -v OFS="\t" '$1=$1' | cut -f5 > eval_list
paste id_list eval_list > parsed_hmmsearch_results && rm id_list eval_list 

#- delete from the all Kunitz UniProt identifiers list the ones which were excluded from the database before running the hmmsearch (which are all Kunitz)
grep -v -x -f $ids_toremove $kunitz_ids > allkunitz_nonredun_IDs.list 


#- from the hmmsearch command results create two subsets of equal size containing the UNIPROT ID, the e-value and the label (1 = Kunitz, 0 = non-Kunitz). The script takes also into account the IDs that weren't shown in the hmmsearch command results and reintroduce them with a fictional e-value (999) and the correct label
python subsets-creation.py parsed_hmmsearch_results allkunitz_nonredun_IDs.list $non_kunitz_ids subset1 subset2 

#to check the correctness of the subsets creation
sort -u subset1 subset2 | wc #check if the number is equal to the total entries of swissprot without the redundant IDs
comm -12 <(sort subset1) <(sort subset2) | wc #check if the two subsets don't share any entries


#-----------------------------------------------------------------------------------------------------------
#- E-VALUE OPTIMIZATION AND PERFORMANCE EVALUATION-
#- optimization on one subset and testing the best threshold on the other
for i in `seq 1 12`
do
python3 performance.py subset1 1e-$i 
done > optimization_results1.txt 

python performance.py subset2 <insert the best threshold on the other>

#swapp the roles
for i in `seq 1 12`
do
python3 performance.py subset2 1e-$i 
done > optimization_results2.txt 

python performance.py subset1 <insert the best threshold on the other>

#- test on the whole test set
python performance.py <(cat subset1 subset2) <insert the average of the best thresholds of the optimizations> > final_results.txt

#to check the alignment of the FP and FN
hmmsearch --cpu 4 --max -Z 569482 -o O62247.out kunitz.hmm O62247.fasta
hmmsearch --cpu 4 --max -Z 569482 -o D3GGZ8_out kunitz.hmm D3GGZ8.fasta

#- graphical visualization of the results
python graphs.py optimization_results1.txt optimization_results2.txt final_results.txt