'''
A naive bayes classifier.
You need to create a dict for each setence, the keys will be the pos tags and the values will be the 
number of times they occur in the parse tree. 

'''
# Django stuff
import os
import sys
import django
sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

from lang_app.models import Card, Sentence
from utils.comparer.comparer import TreeComparer
from sklearn.naive_bayes import MultinomialNB
import csv
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, KFold
import re
from utils.parser.parser import Parser
import nltk

# Read in the 200 questions. 
def read_user_data():
    dict = {}
    path = '/home/stuart/PycharmProjects/workspaces/language_app_project/data/user_function.csv'
    with open(path, 'r') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            dict[row[0]] = row[1]
    return dict

user = read_user_data()

def ask_user(x):
    y_values = [float(user[str(val[0])]) for val in x]
    return np.atleast_2d(y_values).T

def make_binary(array):
    '''
    Converts the data to 'binary' (1 for a correct answer and -1 for incorrect)
    This can be toggled when the evaluate function is called.
    '''
    x = [1 if a <= 0 else -1 for a in array]
    # x = [[1] if a[0] >= 0 and a[0] <= 3 else [-1] for a in array]
    return x

def get_features_pos(pk):

	parser = Parser()

	# get the card and tree string
	card = Card.objects.get(pk=pk)

	s = card.sentence.sentence
	tree = parser.parse(s)[2]


	# get a list of the tags in the parse tree
	x = re.findall(r'[A-HJ-Z]+', tree)

	# create a dict for this sentence
	dict = {}
	for tag in tags:
		dict[tag] = x.count(tag)

	# return an array of values for the dict 
	return [val for val in dict.values()]


def get_features_words(pk):
	# use the pk to get the sentence
	card = Card.objects.get(pk=pk)

	# iterate over the words in the sentence tokenize
	tokens = nltk.word_tokenize(card.sentence.sentence)

	dict = {}
	for word in words:
		dict[word] = tokens.count(word)

	return [val for val in dict.values()] 

if __name__ == "__main__":


	pos = False

	if pos:
		# read in a list of all the pos tags (for pos mode)
		tags = []
		with open("all_pos.txt", 'r') as file:
			for line in file:
				tags.append(line.split('-')[0].strip())

		# create the features dict for each sentence
		features = []
		for pk in user:
			values = get_features_pos(pk)
			features.append((pk, values))

	else:

		# read in a list of the 1000 most common words
		words = []
		with open("3000_most_common.txt", 'r') as file:
			for line in file:
				words.append(line)


		# create the features dict for each sentence
		features = []
		for pk in user:
			values = get_features_words(pk)
			features.append((pk, values))



	# Iterate over the features and get the answer for each question, making a 
	# list of answers that are in the same order as the pks features.
	answers = []
	for f in features:
		answer = user[f[0]]
		answers.append(answer)

	# convert answers from string to ints
	answers = [int(a) for a in answers]

	# convert the answer to a np array and make binary
	answers = np.array(make_binary(answers))
	
	# strip out the pks in the array so that you only have the features
	features = np.array([f[1] for f in features])

	kfold = KFold(n_splits=200)
	results = []
	for train, test in kfold.split(features):

		# create the model
		model = MultinomialNB()

		# create the test and train sets
		X_train, X_test, y_train, y_test = features[train], features[test], answers[train], answers[test]

		model.fit(X_train, y_train)
		prediction = model.predict(X_test)
		results.append(prediction[0] == y_test[0])

	print(results.count(True), "/200")



	

