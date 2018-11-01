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


class Command(BaseCommand):

    help = "Populates the database with cards and sentences from the input texts." \
           "In this branch we make cards that are VERBS ONLY"

    def handle(self, *args, **options):

        path_to_texts = os.path.join(BASE_DIR, 'input_texts')
        comp = TreeComparer()

        # Iterate over all the input texts, break each up into sentences and gather all into one
        # list of sentences.
        sr = SentenceReader()
        sentences = []
        for file in os.listdir(path_to_texts):
            path = os.path.join(path_to_texts, file)
            sentences.extend([sentence for sentence in sr.get_sentences(path)])

        # For each of the sentences, create a list of parsed objects. These are just tuples with,
        # the sentence, the list of chunks and the parse tree as a string
        print("*** Parsing sentences: ")
        parser = Parser()
        parsed_objects = [parser.parse(sentence) for sentence in tqdm(sentences)]

        # ---change the parse tree to return just the verbs---

        # Iterate over the list of parsed objects. You need to create a card for each chunk, with the
        # sentence and the parse tree for the chunk.

        # Make a list of cards
        print("*** Creating cards: ")
        translator = Translator()
        for par_obj in tqdm(parsed_objects):
            # Here we iterate over the chunks for each sentence and create a card for each.
            whole_sentence = par_obj[0]
            sentence_tree_string = par_obj[2]
            sentence_object = Sentence.objects.get_or_create(sentence=whole_sentence,
                                                             sentence_tree_string=sentence_tree_string)[0]
            for verb in par_obj[1]:
                chunk_tree = ""  # don't need anything here anyway
                chunk_translation = ""  # we don't really need anything here

                card = Card.objects.get_or_create(sentence=sentence_object,
                                                  chunk=verb,
                                                  chunk_translation=chunk_translation,
                                                  chunk_tree_string=chunk_tree
                                                  )[0]
                card.question_tree_string = comp.remove_chunk_from_parse_tree(card)
                card.save()




