# Easy data augmentation techniques for text classification
# Jason Wei and Kai Zou

import random
from random import shuffle
random.seed(1)

import os, sys, re
import urllib.request
from pprint import pprint
from word_net import *
import MeCab


class EDA():
	def __init__(self, sw_path="stop_word.txt", wn_path="wnjpn.db", alpha_sr=0.1, alpha_ri=0.1, alpha_rs=0.1, p_rd=0.1, num_aug=9):

		self.alpha_sr=alpha_sr
		self.alpha_ri=alpha_ri
		self.alpha_rs=alpha_rs
		self.p_rd=p_rd
		self.num_aug=num_aug
		if os.path.exists(sw_path):
			print('File already exists.')
		else:
			print('Downloading...')
			# Download the file from `url` and save it locally under `file_name`:
			url = 'http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt'
			urllib.request.urlretrieve(url, sw_path)

		#stop words list
		self.stop_words = []
		with open(sw_path, "r", encoding="utf-8") as f:
			for line in f:
				self.stop_words.append(line[:-1])

		self.wordnet = WordNet(wn_path)
		self.mecab = MeCab.Tagger("-Owakati")

	def get_only_chars(self, line):

		clean_line = ""

		line = line.replace("’", "")
		line = line.replace("'", "")
		line = line.replace("-", " ") #replace hyphens with spaces
		line = line.replace("\t", " ")
		line = line.replace("\n", " ")
		line = line.lower()

		clean_line = line

		clean_line = re.sub(' +',' ',clean_line) #delete extra spaces
		if clean_line[0] == ' ':
			clean_line = clean_line[1:]
		return clean_line

	########################################################################
	# Synonym replacement
	# Replace n words in the sentence with synonyms from wordnet
	########################################################################



	def synonym_replacement(self, words, n):
		new_words = words.copy()
		random_word_list = list(set([word for word in words if word not in self.stop_words]))
		random.shuffle(random_word_list)
		num_replaced = 0
		for random_word in random_word_list:
			synonyms = self.wordnet.getSynonym(random_word)
			if len(synonyms) >= 1:
				synonym = random.choice(list(synonyms))
				new_words = [synonym if word == random_word else word for word in new_words]
				#print("replaced", random_word, "with", synonym)
				num_replaced += 1
			if num_replaced >= n: #only replace up to n words
				break

		#this is stupid but we need it, trust me
		sentence = ' '.join(new_words)
		new_words = sentence.split(' ')

		return new_words


	########################################################################
	# Random deletion
	# Randomly delete words from the sentence with probability p
	########################################################################

	def random_deletion(self, words, p):

		#obviously, if there's only one word, don't delete it
		if len(words) == 1:
			return words

		#randomly delete words with probability p
		new_words = []
		for word in words:
			r = random.uniform(0, 1)
			if r > p:
				new_words.append(word)

		#if you end up deleting all words, just return a random word
		if len(new_words) == 0:
			rand_int = random.randint(0, len(words)-1)
			return [words[rand_int]]

		return new_words

	########################################################################
	# Random swap
	# Randomly swap two words in the sentence n times
	########################################################################

	def random_swap(self, words, n):
		new_words = words.copy()
		for _ in range(n):
			new_words = self.swap_word(new_words)
		return new_words

	def swap_word(self, new_words):
		random_idx_1 = random.randint(0, len(new_words)-1)
		random_idx_2 = random_idx_1
		counter = 0
		while random_idx_2 == random_idx_1:
			random_idx_2 = random.randint(0, len(new_words)-1)
			counter += 1
			if counter > 3:
				return new_words
		new_words[random_idx_1], new_words[random_idx_2] = new_words[random_idx_2], new_words[random_idx_1] 
		return new_words

	########################################################################
	# Random insertion
	# Randomly insert n words into the sentence
	########################################################################

	def random_insertion(self, words, n):
		new_words = words.copy()
		for _ in range(n):
			self.add_word(new_words)
		return new_words

	def add_word(self, new_words):
		synonyms = []
		counter = 0
		while len(synonyms) < 1:
			random_word = new_words[random.randint(0, len(new_words)-1)]
			synonyms = self.wordnet.getSynonym(random_word)
			counter += 1
			if counter >= 10:
				return
		random_synonym = synonyms[0]
		random_idx = random.randint(0, len(new_words)-1)
		new_words.insert(random_idx, random_synonym)

	########################################################################
	# main data augmentation function
	########################################################################

	def sentences_augmentation(self, sentence):
		
		sentence = self.get_only_chars(sentence)
		words = self.mecab.parse(sentence).split()
		words = [word for word in words if word is not '']
		num_words = len(words)
		
		augmented_sentences = []
		num_new_per_technique = int(self.num_aug/4)+1
		n_sr = max(1, int(self.alpha_sr*num_words))
		n_ri = max(1, int(self.alpha_ri*num_words))
		n_rs = max(1, int(self.alpha_rs*num_words))

		#sr
		for _ in range(num_new_per_technique):
			a_words = self.synonym_replacement(words, n_sr)
			augmented_sentences.append(''.join(a_words))

		#ri
		for _ in range(num_new_per_technique):
			a_words = self.random_insertion(words, n_ri)
			augmented_sentences.append(''.join(a_words))

		#rs
		for _ in range(num_new_per_technique):
			a_words = self.random_swap(words, n_rs)
			augmented_sentences.append(''.join(a_words))

		#rd
		for _ in range(num_new_per_technique):
			a_words = self.random_deletion(words, self.p_rd)
			augmented_sentences.append(''.join(a_words))

		augmented_sentences = [self.get_only_chars(sentence) for sentence in augmented_sentences]
		shuffle(augmented_sentences)

		#trim so that we have the desired number of augmented sentences
		if self.num_aug >= 1:
			augmented_sentences = augmented_sentences[:self.num_aug]
		else:
			keep_prob = self.num_aug / len(augmented_sentences)
			augmented_sentences = [s for s in augmented_sentences if random.uniform(0, 1) < keep_prob]

		#append the original sentence
		augmented_sentences.append(sentence)

		return augmented_sentences

if __name__ == '__main__':

    eda = EDA()

    if len(sys.argv) >= 2:
        synonym = eda.sentences_augmentation(sys.argv[1])
        pprint(synonym)
    else:
        synonym = eda.sentences_augmentation("こたつの上で一日中パソコンをしていると背中が痛くなってくる。")
        pprint(synonym)