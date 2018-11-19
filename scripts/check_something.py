# Django stuff
import os
import sys
import django
sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

from lang_app.models import Card

from nltk.parse import stanford
from utils.parser.parser import Parser

# stan = stanford.StanfordParser()
# parser = Parser()
#
# a= "I've always worked very hard  outdoors for most of my life as a railway platelayer  and I think that's made me endure as long as I have."
# b = "But the real achievement is not what I've done; it's how long I've lived."
# c = "I've been wondering about this for a while now."
# x = stan.raw_parse(c)
#
# # print(next(x))
#
#
# x = parser.parse(c)
# print(x[1])
# print(x[2])

print(Card.objects.get(pk=1212))