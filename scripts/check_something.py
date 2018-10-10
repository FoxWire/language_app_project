# Django stuff
import os
import sys
import django
sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

from lang_app.models import Card, Sentence
from utils.comparer.comparer import TreeComparer

'''
This is just to check if there are any cards with the chunk I am looking for
'''

for card in Card.objects.all():
	if "bone cancer" in card.sentence.sentence:
		print(card)