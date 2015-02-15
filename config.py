#read in data to build word scorer
import csv
from math import log
import numpy as np
import os

one_gram = dict()
two_gram = dict()
with open(os.path.join(os.getcwd(), 'gibberish/data/prob_ngrams1.csv'), 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        one_gram[row[0]] = float(row[1])

with open(os.path.join(os.getcwd(), 'gibberish/data/prob_ngrams2.csv'), 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        two_gram[row[0]] = float(row[1])

class WordRater:
    def __init__(self, data):
        self.one_gram, self.two_gram = data

    def rate(self, words):
        """Calculate log prob summary stats for part1 and part2 plus word count"""
        part1List = []
        part2List = []
        for x in words.split(' '):
            part1 = [log(self.one_gram[y]) for y in x]
            part2 = []
            for idx, y in enumerate(x):
                if idx + 1 == len(x):
                    break
                else:
                    part2.append(log(self.two_gram[y+x[idx+1]]))
            part1List.append(sum(part1))
            part2List.append(sum(part2))

        results = [min(part1List), max(part1List), sum(part1List)/len(part1List), np.std(part1List), min(part2List), max(part2List), sum(part2List)/len(part2List), np.std(part2List), len(words.split(' '))]

        return(results)

word_rating = WordRater([one_gram, two_gram])

if __name__=="__main__":
    print("1.", word_rating.rate("words here even more"))
    print("2.", word_rating.rate("asdfasdwer"))
    print("3.", word_rating.rate("zzzzzzzzzzz"))
