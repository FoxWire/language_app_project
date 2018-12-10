import os
# import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'language_app_project.settings')
# django.setup()

from django.core.management.base import BaseCommand, CommandError

from utils.sentence_reader.sentence_reader import SentenceReader
from utils.parser.parser import Parser
# from utils.google_translate.google_translate import Translator
from lang_app.models import Sentence, Card
from tqdm import tqdm
from language_app_project.settings import BASE_DIR
import re


class Command(BaseCommand):

    help = """
        Adds an uncommon word score to each card in the database. 
        The score is the number of words in the sentence that don't occur in the 
        3000 most common English words.
        """

    def handle(self, *args, **options):

        print(len(Sentence.objects.all()))

        # Read in both lists of common words into a set
        common_words = set()
        path = "/home/stuart/PycharmProjects/workspaces/language_app_project/data/"

        with open(path + "common_words_3000.txt", 'r') as file:
            for word in file:
                common_words.add(word.lower().strip())

        with open(path + "common_words_10000.txt", 'r') as file:
            for word in file:
                common_words.add(word.lower().strip())

        # iterate over all sentences and apply the score to them
        for sent_obj in Sentence.objects.all():
            sentence = sent_obj.sentence

            # strip the punctuation (keep the hyphens though for join words )
            words = re.sub(r'[^\w\s\'-]', '', sentence).lower()

            # strip out the digits, numbers
            words = re.sub(r'[0-9]+', '', words)

            # split on spaces and hyphens
            words = re.split(r'[ -]', words)

            # remove any words that are just empty strings
            words = [word for word in words if word]

            # Don't count any duplicate words
            words = list(set(words))

            score, scored_words = 0, []
            for word in words:
                if word not in common_words:
                    score += 1
                    scored_words.append(word)

            sent_obj.uncommon_words_score = score
            sent_obj.save()










