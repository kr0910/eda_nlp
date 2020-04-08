# -*- coding: utf-8 -*-
#
# add words from POMS using wordlist_JP.
#
# ref:
#   WordList_JP: http://compling.hss.ntu.edu.sg/wnja/
#   python3: http://sucrose.hatenablog.com/entry/20120305/p1
import os, sys, sqlite3
from collections import namedtuple
from pprint import pprint
import urllib.request
import gzip
import shutil


class WordNet():
    def __init__(self, path="wnjpn.db"):

        if os.path.exists(path):
            print('WordNet JP File already exists.')
        else:
            print('Downloading WordNet JP File... (slow...)')
            # Download the file from `url` and save it locally under `file_name`:
            url = 'http://compling.hss.ntu.edu.sg/wnja/data/1.1/wnjpn.db.gz'
            urllib.request.urlretrieve(url, path+".gz")
            with gzip.open(path+".gz", 'rb') as f_in:
                with open(path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(path+".gz")

        self.conn = sqlite3.connect(path)
        self.Word = namedtuple('Word', 'wordid lang lemma pron pos')
        self.Sense = namedtuple('Sense', 'synset wordid lang rank lexid freq src')
        self.Synset = namedtuple('Synset', 'synset pos name src')

    def getWords(self, lemma):
        cur = self.conn.execute("select * from word where lemma=?", (lemma,))
        return [self.Word(*row) for row in cur]

    def getSenses(self, word):
        cur = self.conn.execute("select * from sense where wordid=?", (word.wordid,))
        return [self.Sense(*row) for row in cur]

    def getSynset(self, synset):
        cur = self.conn.execute("select * from synset where synset=?", (synset,))
        return self.Synset(*cur.fetchone())

    def getWordsFromSynset(self, synset, lang):
        cur = self.conn.execute("select word.* from sense, word where synset=? and word.lang=? and sense.wordid = word.wordid;", (synset,lang))
        return [self.Word(*row) for row in cur]

    def getWordsFromSenses(self, sense, lang="jpn"):
        synonym = {}
        for s in sense:
            lemmas = []
            syns = self.getWordsFromSynset(s.synset, lang)
            for sy in syns:
                lemmas.append(sy.lemma)
                synonym[self.getSynset(s.synset).name] = lemmas
        return synonym

    def getSynonym (self, word):
        synonym = {}
        words = self.getWords(word)
        if words:
            for w in words:
                sense = self.getSenses(w)
                s = self.getWordsFromSenses(sense)
                synonym = dict(list(synonym.items()) + list(s.items()))
        ## english - japanese
        #return synonym

        ## only japanese
        flatten = lambda x: [z for y in x for z in (flatten(y) if hasattr(y, '__iter__') and not isinstance(y, str) else (y,))]
        synonym_unique = list(set(flatten(list(synonym.values()))))
        print("{} -> {}".format(word, synonym_unique))
        return synonym_unique



if __name__ == '__main__':

    wordnet = WordNet()

    if len(sys.argv) >= 2:
        synonym = wordnet.getSynonym(sys.argv[1])
        pprint(synonym)
    else:
        synonym = wordnet.getSynonym("楽しい")
        pprint(synonym)