from sys import argv
''' Python script to remove from a multiFASTA file specific sequences based on their UniProt ID '''

def filter_fasta(list, allfasta, filtered_fasta):
    with open(list) as f1, open(filtered_fasta, 'w') as f3:
        for id in f1:
            id = id.rstrip()
            with open(allfasta) as f2:
                copy = False
                for line in f2:
                    line = line.rstrip()
                    if line[0] == '>':
                        if line.split('|')[0][1:] == id:
                            copy = True
                            #print(line)
                            f3.write(line + '\n')
                        else:
                            copy = False
                    else:
                        if copy == True:
                            f3.write(line + '\n')

if __name__ == '__main__': 
    if len(argv) != 4:
        print('ERROR: Invalid number of arguments')
        exit(1)
    
    PDB_IDs = argv[1]
    allfasta = argv[2]
    filtered_fasta = argv[3]
    filter_fasta(PDB_IDs, allfasta, filtered_fasta)

   
    
