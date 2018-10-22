# Django stuff
import os
import sys
import django
sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

import csv

from lang_app.models import Card, Sentence
from utils.comparer.comparer import TreeComparer

import nltk
from nltk.corpus import wordnet

from nltk.stem.wordnet import WordNetLemmatizer
words = ['gave','went','going','dating', 'incredibly', 'democratic']
for word in words:
    print(word + "-->" + WordNetLemmatizer().lemmatize(word, pos=wordnet.ADJ))
