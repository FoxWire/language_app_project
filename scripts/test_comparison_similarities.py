'''
The tree comparisons are very slow, I want to know how many comparisons I 
are actually repeated. The sentences are not unique if I strip the leaves.

How should the comparison work?
- Each card has a question parse string. That is the parse tree of the sentence with the chunk replaced.
- And then you just convert it into a zss tree and put it into the tree distance algo


'''

# Django stuff
import os
import sys
import django
sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

from lang_app.models import Card
from utils.comparer.comparer import TreeComparer
from tqdm import tqdm

comp = TreeComparer()
# tups = set()
# count = 0
# for i in tqdm(Card.objects.all()):
#     for j in Card.objects.all():
#         input_a = comp.convert_parse_tree_to_zss_tree(i.question_tree_string, ignore_leaves=True)
#         input_b = comp.convert_parse_tree_to_zss_tree(j.question_tree_string, ignore_leaves=True)
#         tups.add((str(input_a), str(input_b)))
#         count += 1
#
# print("count:", count) #1610361
# print("set:", len(tups)) #1597696

i = Card.objects.all()[10]
j = Card.objects.all()[100]
input_a = comp.convert_parse_tree_to_zss_tree(i.question_tree_string, ignore_leaves=True)
input_b = comp.convert_parse_tree_to_zss_tree(j.question_tree_string, ignore_leaves=True)
a = (str(input_a), str(input_b))
b = (str(input_b), str(input_a))
print(a == b)
