'''
This object will take a card and return the list of the lemmatized words
in it's chunk in a random order
'''

# Django stuff
import os
import sys
import django
sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

import re
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from lang_app.models import Question
from random import shuffle
from language_app_project.settings import BASE_DIR
import os
import json


class Lemmatizer:

    def __init__(self):
        with open(os.path.join(BASE_DIR, 'utils', 'parser', 'verb_forms.json'), 'r') as file:
            self.verb_forms = json.loads(file.read())

    @staticmethod
    def convert_tag(tag):
        if tag.startswith('J'):
            return wordnet.ADJ
        elif tag.startswith('R'):
            return wordnet.ADV
        elif tag.startswith('N'):
            return wordnet.NOUN
        elif tag.startswith('V'):
            return wordnet.VERB
        else:
            return None

    def lemmatize(self, question):

        tree_string = question.chunk_tree_string

        # Get the tags and the words from the tree string of the chunk
        results = re.findall(r'\([A-Z$]+ [A-Za-z0-9\'-]+\)', tree_string)

        # Convert the strings to tuples
        tuples = [tuple(result[1:-1].split()) for result in results]

        # Lemmatize and put into list
        lemmatized = []
        for i, tup in enumerate(tuples):
            # For each tuple, convert the tag for the lemmatizer and lemmatize
            tag, word = self.convert_tag(tup[0]), tup[1]

            lem = WordNetLemmatizer().lemmatize(word, pos=tag) if tag else word

            # Get the other possible verbs if available otherwise just include the word itself
            possible_verbs = self.verb_forms.get(lem, None)
            possible_words = possible_verbs if possible_verbs else []

            if word not in possible_words:
                possible_words.append(word)

            if lem not in possible_words:
                possible_words.append(lem)

            possible_words = [word.lower() for word in possible_words]

            lemmatized.append({'id': str(i), 'lem': lem, 'possible_words': possible_words})

        shuffle(lemmatized)
        return lemmatized

    @staticmethod
    def get_lemmatized_verb(verb):
        return WordNetLemmatizer().lemmatize(verb, pos=wordnet.VERB)
