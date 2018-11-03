import os
# import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'language_app_project.settings')
# django.setup()

from django.core.management.base import BaseCommand, CommandError

from utils.sentence_reader.sentence_reader import SentenceReader
from utils.parser.parser import Parser
from utils.comparer.comparer import TreeComparer
from utils.google_translate.google_translate import Translator
from lang_app.models import Sentence, Card
from tqdm import tqdm
from language_app_project.settings import BASE_DIR
import re


class Command(BaseCommand):

    help = "Populates the database with cards and sentences from the input texts."

    def handle(self, *args, **options):

        # path_to_texts = os.path.join(BASE_DIR, 'input_texts')
        comp = TreeComparer()
        #
        # # Iterate over all the input texts, break each up into sentences and gather all into one
        # # list of sentences.
        # sr = SentenceReader()
        # sentences = []
        # for file in os.listdir(path_to_texts):
        #     path = os.path.join(path_to_texts, file)
        #     sentences.extend([sentence for sentence in sr.get_sentences(path)])
        #
        # # For each of the sentences, create a list of parsed objects. These are just tuples with,
        # # the sentence, the list of chunks and the parse tree as a string
        # print("*** Parsing sentences: ")
        parser = Parser()
        # parsed_objects = [parser.parse(sentence) for sentence in tqdm(sentences)]
        #
        # # Iterate over the list of parsed objects. You need to create a card for each chunk, with the
        # # sentence and the parse tree for the chunk.
        #
        # # Make a list of cards
        # print("*** Creating cards: ")
        # translator = Translator()
        # for par_obj in tqdm(parsed_objects):
        #     # Here we iterate over the chunks for each sentence and create a card for each.
        #     whole_sentence = par_obj[0]
        #     sentence_tree_string = par_obj[2]
        #     sentence_object = Sentence.objects.get_or_create(sentence=whole_sentence,
        #                                                      sentence_tree_string=sentence_tree_string)[0]
        #     for chunk in par_obj[1]:
        #         # check if suitable
        #         chunk_length = len(chunk.split(' '))
        #         if 4 <= chunk_length <= 8:
        #             chunk_tree = parser.parse(chunk)[2]
        #             chunk_translation = translator.get_translation(chunk)
        #
        #             card = Card.objects.get_or_create(sentence=sentence_object,
        #                                               chunk=chunk,
        #                                               chunk_translation=chunk_translation,
        #                                               chunk_tree_string=chunk_tree
        #                                               )[0]
        #             card.question_tree_string = comp.remove_chunk_from_parse_tree(card)
        #             card.save()
        #

        # --- New for German Version ---

        # load in the stuff from the text
        path = os.path.join(BASE_DIR, 'input_texts/Deutsch.txt')
        raw_sentences = []

        with open(path, 'r') as file:
            for line in file:
                # Ignore the sentences that don't have a curly braces in them
                if '{' in line and '(' in line:  # You only want sentences at the moment that have chunks and translations
                    raw_sentences.append(line)

            unique_sentences = {}
            for line in tqdm(raw_sentences):
                # Get the different parts out of the sentence
                line = line.strip()

                chunk_translation = re.findall(r'\([\w\s\'.:;,\-&!?\"/]+\)', line)[0][1:-1]

                chunk = re.findall(r'{{c1::[\w\s\':;,.\-&!?\"\(\)\"]+}}', line)[0][6:-2]

                sen_part_a, sen_part_b = re.split(r'\([\w\s:.,;{}!?\-\'/\)\(\"]+}', line)

                # Recreate the complete sentence
                complete_sentence = " ".join([sen_part_a, chunk, sen_part_b])

                # If we've not seen the sentence before:
                no_spaces = re.sub(r'[\s]+', '', complete_sentence)

                if no_spaces not in unique_sentences:
                    unique_sentences[no_spaces] = complete_sentence
                    sentence_tree_string = parser.parse(complete_sentence)[2]
                    sentence_object = Sentence.objects.get_or_create(sentence=complete_sentence,
                                                                     sentence_tree_string=sentence_tree_string)[0]
                else:
                    no_spaces = re.sub(r'[\s]+', '', complete_sentence)
                    sentence_object = Sentence.objects.get(sentence=unique_sentences[no_spaces])

                # Create the card object
                card_object = Card.objects.get_or_create(sentence=sentence_object,
                                                         chunk=chunk,
                                                         chunk_translation=chunk_translation,
                                                         chunk_tree_string=parser.parse(chunk)[2]
                                                         )[0]

                card_object.question_tree_string = comp.remove_chunk_from_parse_tree(card_object)
                card_object.save()



