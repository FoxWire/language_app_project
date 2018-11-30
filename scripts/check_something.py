# Django stuff
import os
import sys
import django
sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

from lang_app.models import Question, Block, Session, UserState, Sentence
from utils.policies.policies import PolicyOne, PolicyTwo, PolicyThree
import re
from random import randint
from utils.matrix_wrapper import MatrixWrapper
from tqdm import tqdm


for question in Question.objects.all():
    if '106' in question.chunk:
        print(question.sentence, question.pk)



