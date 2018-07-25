import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'language_app_project.settings')
import django
django.setup()

from lang_app.models import Sentence, Card

from sentence_reader import SentenceReader
from parser import Parser
from google_translate.google_translate import Translator
from comparer import TreeComparer
from card import Card
import re
from random import shuffle
from tqdm import tqdm
from nltk.parse import stanford
import os


'''
As before, this will need to read in the texts, split them all into sentences
then iterate over the list of sentences and break them into chunks. Then create card for each chunk. 
You will need to check the translation cache.
'''

def prepare_cards():

    path_to_texts = './input_texts/'
    # Loop each of the texts and create one list of all the sentences
	sr = SentenceReader()
    sentences = []
    for path in os.listdir(path_to_texts):
        sentences.extend([sentence for sentence in sr.get_sentences(path_to_texts + path)])

    # For each of the sentences, create a list of parsed objects. These are just tuples with,
    # the sentence, the list of chunks and the parse tree as a string
	parser = Parser()
    parsed_objects = [parser.parse(sentence) for sentence in tqdm(sentences)]


    '''
	Iterate over the list of parsed objects. You need to create a card for each chunk, with the 
	sentence and the parse tree for the chunk. 
	'''

    # Make a list of cards
    translator = Translator()
    cards = []
    for par_obj in tqdm(parsed_objects):
        # Here we iterate over the chunks for each sentence and create a card for each.
        whole_sentence = par_obj[0]
        for chunk in par_obj[1]:
            # check if suitable
            chunk_length = len(chunk.split(' '))
            if 4 <= chunk_length <= 8:
                chunk_tree = parser.parse(chunk)[2]
                chunk_translation = translator.get_translation(chunk)
                cards.append(Card(	whole_sentence,
				 					chunk,
				 					chunk_translation,
				 					chunk_tree
				 					))
    # Shuffle the cards
    shuffle(cards)
    return cards


