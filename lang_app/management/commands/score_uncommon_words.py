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

        # First you will need to read in the list of common words into a set
        common_words = set()
        path = "/home/stuart/PycharmProjects/workspaces/language_app_project/data/"

        with open(path + "common_words_3000.txt", 'r') as file:
            for word in file:
                common_words.add(word.lower().strip())

        with open(path + "common_words_10000.txt", 'r') as file:
            for word in file:
                common_words.add(word.lower().strip())

        for sent_obj in Sentence.objects.all()[90:100]:
            sentence = sent_obj.sentence

            # strip the punctuation
            words = re.sub(r'[^\w\s\']', '', sentence).lower().split(' ')

            # remove any words that are just empty strings
            words = [word for word in words if word]

            score, scored_words = 0, []
            for word in words:
                if word not in common_words:
                    score += 1
                    scored_words.append(word)

            sent_obj.uncommon_words_score = score
            sent_obj.save()

            print(sent_obj)
            print(scored_words)










