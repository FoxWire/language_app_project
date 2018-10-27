# Generate some random numbers

from random import shuffle
# Django stuff
import os
import sys
import django
sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

from lang_app.models import Card, Sentence
from utils.comparer.comparer import TreeComparer

path = "/home/stuart/PycharmProjects/workspaces/language_app_project/data/new_random_nums.csv"
with open(path, 'a') as file:
	# get the first 200 numbers, shuffle then and write to file

	# numbers = [x for x in range(1, 201)]
	# shuffle(numbers)
	# for n in numbers:
	# 	file.write(str(n))
	# 	file.write('\n')

	# Get the pks of the first 200 cards where the sentences have less than one uncommon word
	all_cards = [c for c in Card.objects.filter(sentence__uncommon_words_score__lt=2)[:200]]
	shuffle(all_cards)
	for c in all_cards:
		file.write(str(c.pk))
		file.write('\n')
