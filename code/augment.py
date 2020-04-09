# Easy data augmentation techniques for text classification
# Jason Wei and Kai Zou

from eda import *

#arguments to be parsed from command line
import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--input", required=True, type=str, help="input file of unaugmented data")
ap.add_argument("--output", required=False, type=str, help="output file of unaugmented data")
ap.add_argument("--num_aug", required=False, type=int, help="number of augmented sentences per original sentence")
ap.add_argument("--alpha", required=False, type=float, help="percent of words in each sentence to be changed")
ap.add_argument("--stopword", required=False, type=str, help="japanese_stop_words.txt")
ap.add_argument("--wordnet", required=False, type=str, help="japanese_wordnet.db")
ap.add_argument("--aug_col", required=False, type=str, help="augmentation column")
ap.add_argument("--sep", required=False, type=str, help="setarator")
args = ap.parse_args()

#the output file
output = None
if args.output:
    output = args.output
else:
    from os.path import dirname, basename, join
    output = join(dirname(args.input), 'eda_' + basename(args.input))

#number of augmented sentences to generate per original sentence
num_aug = 9 #default
if args.num_aug:
    num_aug = args.num_aug

#how much to change each sentence
alpha = 0.1#default
if args.alpha:
    alpha = args.alpha
    
stopword = "stop_word.txt"
if args.stopword:
    stopword = args.stopword
    
wordnet = "wnjpn.db"
if args.wordnet:
    wordnet = args.wordnet
    
aug_col = ""
if args.aug_col:
    aug_col = args.aug_col
    
sep = "\t"
if args.sep:
    sep = args.sep

#generate more data with standard augmentation
def gen_eda(train_orig, output_file, stopword, wordnet, aug_col, sep, alpha, num_aug=9):

    writer = open(output_file, 'w')
    lines = open(train_orig, 'r').readlines()
    eda = EDA(stopword, wordnet, alpha_sr=alpha, alpha_ri=alpha, alpha_rs=alpha, p_rd=alpha, num_aug=num_aug)
        
    for i, line in enumerate(lines):

        if i == 0 and aug_col:
            col_names = line.rstrip().split(sep)
            aug_col_index = col_names.index(aug_col)
            continue
        elif i == 0:
            aug_col_index = 0
        parts = line[:-1].split(sep)
        sentence = parts[aug_col_index]
        aug_sentences = eda.sentences_augmentation(sentence)
        for aug_sentence in aug_sentences:
            parts[aug_col_index] = aug_sentence
            writer.write(sep.join(parts) + '\n')

    writer.close()
    print("generated augmented sentences with eda for " + train_orig + " to " + output_file + " with num_aug=" + str(num_aug))

#main function
if __name__ == "__main__":

    #generate augmented sentences and output into a new file
    gen_eda(args.input, output, stopword, wordnet, aug_col, sep, alpha=alpha, num_aug=num_aug)