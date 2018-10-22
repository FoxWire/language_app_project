import os
import sys
import django

sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

from lang_app.models import Card, Sentence
from utils.comparer.comparer import TreeComparer
from utils.parser.parser import Parser


sentence_a = "Have you ever eaten meat?"
sentence_b = "Have I ever seen kangaroos?"
comp = TreeComparer()
parser = Parser()

tree_a = parser.parse(sentence_a)[2]
tree_b = parser.parse(sentence_b)[2]

print(tree_a)
print(tree_b)

result = comp.compare_tree_strings(tree_a, tree_b, ignore_leaves=True)
print(result)

