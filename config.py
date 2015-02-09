#read in data to build word scorer
import csv
from math import log

one_gram = dict()
two_gram = dict()
with open('data/prob_ngrams1.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        one_gram[row[0]] = float(row[1])

with open('data/prob_ngrams2.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        two_gram[row[0]] = float(row[1])

class WordRater:
    def __init__(self, data):
        self.one_gram, self.two_gram = data

    def rate(self, words):
        #calc log prob 
        for x in [list(word) for word in words.split(' ')]:
            part1 = sum([log(self.one_gram[y]) for y in x])
            part2 = []
            for idx, y in enumerate(x):
                if idx + 1 == len(x):
                    break
                else:
                    part2.append(log(self.two_gram[y+x[idx+1]]))
            log_prob = part1 + sum(part2)
            return(log_prob)

if __name__=="__main__":
    word_rating = WordRater([one_gram, two_gram])
    print(word_rating.rate("words here"))
    print(word_rating.rate("asdfasdwer"))
    print(word_rating.rate("zzzzzzzzzzz"))
