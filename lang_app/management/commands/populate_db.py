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

        comp = TreeComparer()
        parser = Parser()
        trans = Translator()

        '''
         --- New for One Word German Version  ---
         Loop over all the sentences
         for each verb in the sentence, you need to make a card
         you need to get the English translation of the word if it is not in the chunk
         and you will need to build up the question tree and the sentence tree
         
        '''

        # Read in all the sentences
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
                # chunk_translation = re.findall(r'\([\w\s\'.:;,\-&!?\"/]+\)', line)[0][1:-1]

                chunk = re.findall(r'{{c1::[\w\s\'`:;,.\-&!?\"\(\)\"]+}}', line)[0][6:-2]

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

                # You don't use the chunk that you have taken from the text here. You need to find all the verbs in the
                # complete sentence

                # get all words with tags
                token_tups = [tuple(token[1:-1].split(' ')) for token in
                          re.findall(r'\([A-Z\[$.,:]+ [\w\'&\.\-:"`]+\)', sentence_object.sentence_tree_string)]

                # Filter on the verbs
                verb_tups = [t for t in token_tups if t[0].startswith("V")]

                # Now you need to make card for each verb
                for verb_tup in verb_tups:

                    verb = verb_tup[1]
                    verb_translation = trans.get_translation(verb)

                    # Create the card object
                    card_object = Card.objects.get_or_create(sentence=sentence_object,
                                                             chunk=verb,
                                                             chunk_translation=verb_translation,
                                                             )[0]

                    card_object.question_tree_string = comp.remove_chunk_from_parse_tree(card_object)
                    card_object.save()

