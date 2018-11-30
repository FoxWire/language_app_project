from django.core.management.base import BaseCommand, CommandError
from lang_app.models import Card, Sentence
import json
from utils.parser.parser import Parser
from utils.comparer.comparer import TreeComparer
'''
This is just a test to see if how well the system will find similar patterns 
in chunks. You can enter your own chunk and see what matches come back.
'''


class Command(BaseCommand):

    def handle(self, *args, **options):
        my_chunk = "I've been thinking about it for days."

        parser = Parser()
        comp = TreeComparer()

        # get the parse tree for this chunk
        tree_string = parser.parse(my_chunk)[2]

        big_list = []
        # compare all other chunks to this one
        for card in Card.objects.all():
            this_tree_string = card.tree_string
            score = comp.compare_tree_strings(tree_string, this_tree_string)
            big_list.append((card.pk, score))

        new = sorted(big_list, key=lambda x: x[1])[:10]

        for item in new:
            c = Card.objects.get(pk=item[0])
            print(c.chunk)