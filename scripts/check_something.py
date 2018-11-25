# Django stuff
import os
import sys
import django
sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

from lang_app.models import Question, Block, Session
from utils.policies.polices import PolicyOne, PolicyTwo, PolicyThree

a = PolicyOne.get_question.__code__.co_code
b = PolicyTwo.get_question.__code__.co_code
c = PolicyThree.get_question.__code__.co_code


print(a == b)
print(b == c)
print(a == c)