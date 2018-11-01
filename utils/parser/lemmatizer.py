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
from lang_app.models import Card
from random import shuffle


class Lemmatizer:

    def __init__(self):
        pass

    def convert_tag(self, tag):
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

    def lemmatize(self, card):
        tree_string = card.chunk_tree_string
        print(tree_string)
        # Get the tags and the words from the tree string of the chunk
        results = re.findall(r'\([A-Z$]+ [A-Za-z\'-]+\)', tree_string)

        # Convert the strings to tuples
        tuples = [tuple(result[1:-1].split()) for result in results]

        # Lemmatize and put into list
        lemmatized = []
        for tup in tuples:

            tag, word = self.convert_tag(tup[0]), tup[1]
            print(tag, word)
            if tag:
                lemmatized.append(WordNetLemmatizer().lemmatize(word, pos=tag))
            else:
                lemmatized.append(word)

        shuffle(lemmatized)
        return lemmatized


if __name__ == "__main__":
    card = Card.objects.all()[1399]
    lem = Lemmatizer()
    result = lem.lemmatize(card)
    # print(card.chunk)
    # print(result)
    print(Card.objects.all()[183])
