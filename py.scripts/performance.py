from sys import argv

def get_cm(input_file,t):
    fn_list = []
    fp_list = []
    cm = [[0,0],[0,0]]
    with open(input_file) as file:    
        for line in file:
            line = line.rstrip().split()
            if float(line[1]) < t:
                if line[2] == '1':
                    cm[0][0] += 1    
                else:
                    cm[1][0] += 1    
                    fp_list.append(line[0])
            else:
                if line[2] == '1':  
                    cm[0][1] += 1
                    fn_list.append(line[0])
                else:               
                    cm[1][1] += 1
        return cm, fn_list, fp_list

def get_acc(cm):
    acc = (cm[0][0]+cm[1][1])/(cm[0][0]+cm[0][1]+cm[1][0]+cm[1][1])
    return acc

def get_mcc(cm):
    mcc = ((cm[1][1]*cm[0][0])-(cm[0][1]*cm[1][0]))/((cm[0][0]+cm[1][0])*(cm[0][0]+cm[0][1])*(cm[1][1]+cm[1][0])*(cm[1][1]+cm[0][1]))**0.5
    return mcc

if __name__ == '__main__':
    if len(argv) != 3:
        print("ERROR: Invalid number of arguments")
        exit(1)
    input_file = argv[1]
    t = float(argv[2])
    cm, fn_list, fp_list = get_cm(input_file,t)
    acc = get_acc(cm)
    mcc = get_mcc(cm)
    print('th:', t, '\t', 'ACC:', acc,'\t', 'MCC:', mcc,'\t', 'CM:', cm, '\t', 'FN:',fn_list,'\t', 'FP:',fp_list)
    