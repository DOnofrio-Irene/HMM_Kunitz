#!/usr/bin/python
from sys import argv

def get_training_list(training_IDs):
    training_list = list()
    with open(training_IDs) as f:
        for line in f:
            line = line.strip()
            training_list.append(line)
    return training_list

def remove_seq(training_list, complete_fasta_file, fasta_file_without_training):
    with open(complete_fasta_file) as f1, open(fasta_file_without_training, 'w') as f2: 
        copy = False
        for line in f1:
            line = line.rstrip() 
            if line.startswith('>'): 
                id = line.split('|')[1]                           
                if id in training_list:   #if the sequence is in the training list
                   copy = False
                   print(line)
                else:                                     #if the sequence is not in the training list
                    copy = True
                    f2.write(line + '\n')
            else:                                         #sequence line
                if copy == True: 
                    f2.write(line + '\n')
                
    

if __name__ == "__main__":
    if len(argv) != 4:
        print("ERROR: uncorrect number of arguments.")
        exit(1)
    training_IDs = argv[1]
    complete_fasta_file = argv[2]
    fasta_file_without_training = argv[3]
    training_list = get_training_list(training_IDs)
    remove_seq(training_list, complete_fasta_file, fasta_file_without_training)
   
