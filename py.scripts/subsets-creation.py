from sys import argv
import random
''' This Python script takes in input the results of hmmsearch program and gives as output two randomly splitted and equally sized subsets, in which each entries is associated with the corresponding E-value and the label (0,1)'''

def get_results_dict(hmm_results):
    """ Create a dictionary of the results of the hmmsearch command"""
    results_dict = {}
    with open(hmm_results, 'r') as f:
        for line in f:
            line = line.strip().split()
            key = line[0]
            value = line[1]
            results_dict[key] = value
    lenght = len(results_dict)
    return results_dict

def create_kunitz_matrix(dict, kunitz_IDs):
    """Create a matrix containing all the proteins with a Kunitz domain associated with the e-value and the classification label (1)"""
    kunitz_matrix = []
    with open(kunitz_IDs, 'r') as f2:
        for line in f2:
            line = line.rstrip()
            if line in dict.keys():
                row = [line, dict[line], '1'] 
            else:
                row = [line, '999', '1']       
            kunitz_matrix.append(row)         
    return kunitz_matrix
    
def create_nonkunitz_matrix(dict, nonkunitz_IDs):
    """Create a matrix containing all the proteins not belonging to the Kunitz family associated with the e-value and the classification label (0)"""
    nonkunitz_matrix = []
    with open(nonkunitz_IDs, 'r') as f2:
        for line in f2:
            line = line.rstrip()
            if line in dict.keys():
                row = [line, dict[line], '0']  
            else:
                row = [line, '999', '0']       
            nonkunitz_matrix.append(row)
    return nonkunitz_matrix

def create_submatrices(matrix):
    """ Takes in input a matrix, shuffle it and returns two submatrices (of equal length)"""
    #Shuffle the matrix
    random.Random(42).shuffle(matrix)

    #Divide the matrix
    size = len(matrix)
    half_size = size // 2

    submatrix1 = matrix[:half_size + (size % 2)]
    submatrix2 = matrix[half_size:]

    return submatrix1, submatrix2

def create_subsets(submatrix1_1, submatrix1_2, submatrix2_1, submatrix2_2, outputfile1, outputfile2):
    with open(outputfile1, 'w') as out1:
        merged_matrix1 = submatrix1_1 + submatrix2_1
        for row in merged_matrix1:
            out1.write(' '.join(row) + '\n')
    with open(outputfile2, 'w') as out2:
        merged_matrix2 = submatrix1_2 + submatrix2_2
        for row in merged_matrix2:
            out2.write(' '.join(row) + '\n')

    
    


if __name__ == '__main__':

    if len(argv) != 6:
        print("ERROR: Invalid number of arguments")
        exit(1)
        
    hmm_results = argv[1]
    kunitz_IDs = argv[2]
    nonkunitz_IDs = argv[3]
    subset1 = argv[4]
    subset2 = argv[5]
    results_dict = get_results_dict(hmm_results)
    kunitz_matrix = create_kunitz_matrix(results_dict, kunitz_IDs)
    nonkunitz_matrix = create_nonkunitz_matrix(results_dict, nonkunitz_IDs)
    submatrix1_1, submatrix1_2 = create_submatrices(kunitz_matrix)
    submatrix0_1, submatrix0_2 = create_submatrices(nonkunitz_matrix)
    create_subsets(submatrix1_1, submatrix1_2, submatrix0_1, submatrix0_2, subset1, subset2)
