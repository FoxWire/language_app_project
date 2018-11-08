from utils.comparer.comparer import TreeComparer
from lang_app.models import Card, Sentence, UserProfile
from random import randint
from tqdm import tqdm
import json
from django.contrib.auth.models import User


class Picker:
    '''
        This new picker will ask the user ten initial questions.
        If they get any of the questions wrong:
            - we have some areas that we can work on.
            - we can then look at these questions and find other questions that are similar and therefore should
            also be difficult for the learner.
            - They will get some of these similar questions to practise and them some more to test
            - they pass the test and we move on to the next part
        If they get the questions right at first or pass the test:
            - we try to find the next best set of questions to work with
            - we need to find questions that are different from the ones that they have seen
            - we want to get away from random here.
    '''

    def __init__(self):
        pass

    def get_question(self, user_pk, card):

        num_cards = len(Card.objects.all())
        user = User.objects.get(pk=user_pk)
        user_profile = UserProfile.objects.get(pk=user_pk)

        # If you get a user and no card, this is the first time the user has been here.
        # you need to do some set up
        if not card:
            initial_questions = [randint(1, num_cards)for x in range(11)]
            user_profile.initial_questions = json.dump(initial_questions)
            user_profile.save()
        else:
            # If they pass in a card, then they should have some data.
            pass













    def give_answer(self):
        pass



