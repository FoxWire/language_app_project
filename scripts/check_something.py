# Django stuff
import os
import sys
import django
sys.path.append('/home/sdmiller/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

from lang_app.models import Question, Block, Session, UserState, Sentence, QandA
from utils.policies.policies import PolicyOne, PolicyTwo, PolicyThree
import re
from random import randint, shuffle
from utils.matrix_wrapper import MatrixWrapper
from tqdm import tqdm

from django.contrib.auth.models import User

# this_session = Session.objects.get(pk=17)





user = User.objects.get(username='Susanna')

# qanda = QandA.objects.filter(question__pk=312, block=this_block)


# get the user state
user_state = UserState.objects.get(user=user)
block = user_state.current_session.current_block

qanda = QandA.objects.get(question__pk=312, block=block)
print(qanda)
