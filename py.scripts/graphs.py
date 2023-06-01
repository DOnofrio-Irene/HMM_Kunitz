#!/usr/bin/python
""" python script to visualize the results of an optimization procedure for an HMM model"""
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize
import pandas as pd
from sys import argv


def MCCvsEvalue(data1, data2):
    """ displays the relationship between MCC and Evalue; the input arguments are the results of an optimization procedure carried out on two subset"""
    evalues1 = data1['E-values']
    mcc1 = data1['mcc']

    evalues2 = data2['E-values']
    mcc2 = data2['mcc']

    combined_data = pd.concat([data1, data2])
    custom_palette = ['magenta', 'purple']
    sns.lineplot(x='E-values', y='mcc', hue = 'Subset', data=combined_data, style = 'Subset', markers = True, palette = custom_palette)
    plt.xlabel('E-values')
    plt.ylabel('MCC')
    plt.xscale('log')
    plt.title('MCC vs E-value')
    return(plt.savefig('MCCvsEvalue.png'))

def confusion_matrix(data3):
    with open(data3) as f:
        for line in f:
            line = line.split('\t')
            array = eval(line[3])
            plt.figure(figsize=(8,6), dpi=100)
            sns.set(font_scale = 1.1)
            df = pd.DataFrame(array)
            ax = sns.heatmap(df, annot=True, fmt='d',norm=LogNorm())
            ax.set_xlabel("Predicted class", fontsize=14, labelpad=10)
            ax.xaxis.set_ticklabels(['Positive', 'Negative'])
            ax.set_ylabel("Actual class", fontsize=14, labelpad=10)
            ax.yaxis.set_ticklabels(['1', '0'])
            ax.set_title("Confusion Matrix", fontsize=14, pad=20)
            return(plt.savefig('ConfusionMatrix.png'))
        
    
if __name__ == '__main__':
    #import the data
    data1 = pd.read_csv(argv[1], delimiter='\t', names = ['E-values', 'accuracy', 'mcc', 'cm', 'fn', 'fp'])
    data2 = pd.read_csv(argv[2], delimiter='\t', names = ['E-values', 'accuracy', 'mcc', 'cm', 'fn', 'fp'])
    data3 = argv[3]
    #add the a new column for labeling the subset
    data1['Subset'] = pd.Series([1 for x in range(len(data1.index))])
    data2['Subset'] = pd.Series([2 for x in range(len(data2.index))])

    MCCvsEvalue(data1,data2)
    confusion_matrix(data3)
    

