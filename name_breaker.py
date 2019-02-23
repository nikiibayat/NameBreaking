from __future__ import division
import operator
import string,csv
from math import log10
from collections import defaultdict

unigram_smooth = 2  # (0 = Additive, 1 = Norvig)
bigram_smooth = 0  # (0 = backoff, 1 = interpolation)

with open("unigram.txt") as infile:
	unigram = {}
	unigram = defaultdict(lambda: 0, unigram)
	unique_unigram_tokens = 0  # num of unique tokens
	N = 0  # num of tokens
	for line in infile:
		token_freq = line.split()
		unigram[token_freq[0]] = token_freq[1]
		unique_unigram_tokens += 1
		N += int(token_freq[1])
def unigram_probability(word):
	if unigram_smooth == 0:  # Additive Smoothing
		delta = 0.0001  # Parameter for Additive Smoothing
		prob = (int(unigram[word]) + delta) / (N + delta *
		                                       unique_unigram_tokens)
	elif unigram_smooth == 1:  # Norvig Smoothing (avoid long words)
		if word in unigram:
			prob = int(unigram[word]) / N
		else:
			prob = 10 * ((N * (10 ** len(word))) ** (-1))
	else:  # No Smoothing
		if word in unigram:
			prob = int(unigram[word]) / N
		else:
			prob = 0
	return prob


def candidates(name):
	splits = []
	for i in range(len(name)):
		splits.append([])
		splits[i].append(name[:i])
		splits[i].append(name[i:])
	return splits


def unigram_breaker(name):
	if not name:
		return ""
	splits = candidates(name)
	score = []
	for first, remaining in splits:
		score.append(unigram_probability(first) *
		             unigram_probability(remaining))
	index, value = max(enumerate(score), key=operator.itemgetter(1))
	return splits[index]


def splits(text, L=40):
	return [(text[:i + 1], text[i + 1:]) for i in range(min(len(text), L))]


#Peter Norvig Bigram
class Pdist(dict):
	"A probability distribution estimated from counts in datafile."

	def __init__(self, data=[], N=None, missingfn=None):

		for key, value in data:
			self[key] = self.get(key, 0) + int(value)
		self.N = float(N or sum(self.itervalues()))
		self.missingfn = missingfn or (lambda k, N: 1. / N)
		print "initializing finished"

	def __call__(self, key):
		if key in self:
			return self[key] / self.N
		else:
			return self.missingfn(key, self.N)


def datafile(name, sep='\t'):
	"Read key,value pairs from file."
	for line in file(name):
		yield line.split(sep)

# bigram = {}
# bigram = Pdist(datafile('nicky_bigram.txt'), N)


def bigram_probability(word, prev):
	# Back off
	if bigram_smooth == 0:
		try:
			prob = bigram[prev + ' ' + word] / float(unigram_probability(prev))
			return prob
		except KeyError:
			return unigram_probability(word)

	# Interpolation
	elif bigram_smooth == 1:
		landa2 = 0.9
		try:
			prob = ((landa2 * bigram[prev + " " + word]) / float(
				unigram_probability(prev))) + (
					       1 - landa2) * float(unigram_probability(word))
			return prob
		except KeyError:
			return (1 - landa2) * float(unigram_probability(word))


def bigram_breaker(name, prev='<S>'):
	if not name: return 0.0, []
	candidates = [combine(log10(bigram_probability(prev, first)), first,
	                      bigram_breaker(rem,
	                                     first))
	              for first, rem in splits(name)]
	return max(candidates)


def combine(Pfirst, first, (Prem, rem)):
	return Pfirst + Prem, [first] + rem


# def test():
# 	with open('newtest.txt') as f:
# 		out = open('mistakes2.txt', 'w')
# 		csv_reader = csv.reader(f, delimiter=',')
# 		true_compute = 0
# 		num_of_rows = 0
# 		exclude = set(string.punctuation)
# 		for row in csv_reader:
# 			num_of_rows += 1
# 			true_name = []
#
# 			s = ""
# 			for i in range(len(row)):
# 				if i == 0:
# 					continue
# 				else:
# 					s = ''.join(' ' not ch in exclude else ch for ch in row[i])
# 					if not hasNumbers(s) and s:
# 						parts = s.split()
# 						for part in parts:
# 							true_name.append(part.lower())
#
# 			s = ''.join(ch for ch in row[0] if ch not in exclude)
#
# 			if not hasNumbers(s) and s:
# 				print "here breaking"
# 				name = bigram_breaker(s.lower())
# 				if name[1] == true_name:
# 					true_compute += 1
# 				else:
# 					out.write(str(true_name) + "\t" + str(name) + "\n")
#
# 		print true_compute
# 		print num_of_rows
# 		print true_compute / num_of_rows
# 		out.close()


def hasNumbers(inputString):
	return any(char.isdigit() for char in inputString)


def main():
	# test()
	while(True):
		print "please enter a name"
		name = raw_input()
		print unigram_breaker(name)
# 	unigram_breaker("nickybayat")

if __name__ == '__main__':
	main()
