# Django stuff
import os
import sys
import django
sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

from lang_app.models import Question, Block, Session, UserState
from utils.policies.policies import PolicyOne, PolicyTwo, PolicyThree

user_state = UserState.objects.all()[0]
print(user_state.current_policy_id)
user_state.switch_policy()
print(user_state.current_policy_id)