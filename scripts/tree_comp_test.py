# Django stuff
import os
import sys
import django
sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

from lang_app.models import Card, Sentence
from utils.comparer.comparer import TreeComparer
from utils.parser.parser import Parser

'''
I am using the tree comparison algo to mark and score the user's answers. 
If you have the exact same sentence, you will get a score of 0
If you replace one word with another of the same type, (verb) then you will be only one point out.
When you go outside of that, you are changing the structure of the tree and that will mean you get more points 
in differnce. 

So what does that mean? Is it good to use the tree comparison for marking? 



'''

# Here are two example sentences
sentence = "This is just an example sentence that I am using to test some things."
answer = "This is just an example sentence that I am using to tree some things."

parser = Parser()
comp = TreeComparer()

sentence_parsed = parser.parse(sentence)[2]

answer_parsed = parser.parse(answer)[2]

x = comp.compare_tree_strings(sentence_parsed, answer_parsed)
print(x)
