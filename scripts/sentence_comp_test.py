import os
import sys
import django

sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

from lang_app.models import Card, Sentence
from utils.comparer.comparer import TreeComparer
from utils.parser.parser import Parser

sentence_a = "He hasn’t seen her for a while."
sentence_b = "Why haven’t you been doing your homework?"
sentence_c = "There’s been a big accident in Market Street."
sentence_d = "Have you ever eaten snails?"
sentence_e = "Have you ever seen kangaroos?"
comp = TreeComparer()
parser = Parser()

tree_a = parser.parse(sentence_d)[2]
tree_b = parser.parse(sentence_e)[2]

result = comp.compare_tree_strings(tree_a, tree_b, ignore_leaves=True)
print(result)



'''
The program will not be able to recognise any pattern between two sentences that are for example both in the 
present perfect but where one is a question. But that doens't really matter. We want it to find similar
sentences and
'''
