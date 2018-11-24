from utils.comparer.comparer import TreeComparer
from lang_app.models import Question, Sentence, UserState
from random import randint
from tqdm import tqdm
import json
from django.contrib.auth.models import User


class Picker:

    pass
    '''
    #     This new picker will ask the user ten initial questions.
    #     - Generate 10 random questions and ask them
    # 
    #     - look in the initial questions, if there are none, then they haven't started yet, or they are
    #     in the train stage.
    # 
    # '''
    #
    # def __init__(self):
    #     pass
    #
    # def get_question(self, user_pk, card):
    #
    #     num_cards = len(Card.objects.all())
    #     user = User.objects.get(pk=user_pk)
    #     user_profile = UserProfile.objects.get(pk=user_pk)
    #
    #     # check the user profile for the initial cards
    #     if user_profile.mode == 'initial':
    #         # Find the first card in the initial cards that has no results and return the pk
    #         questions = json.loads(user_profile.initial_questions)
    #         for q in questions:
    #             if not q['result']:
    #                 return q['pk']
    #
    #     elif user_profile.mode == 'train':
    #         # If there are training cards give them one
    #         cards = json.loads(user_profile.training_cards)
    #         user_profile.initial_cards = cards[1:]
    #         user_profile.save()
    #         return cards[0]
    #
    #     elif user_profile.mode == 'test':
    #         cards = json.loads(user_profile.training_cards)
    #         user_profile.initial_cards = cards[1:]
    #         user_profile.save()
    #         return cards[0]
    #
    #     else:
    #         # If you get to this point, there are no cards anywhere, create the initial cards and return one
    #         initial = []
    #         for x in range(11):
    #             d = {
    #                 'pk': randint(1, num_cards),
    #                 'result': None,
    #                 'train_questions': None,
    #                 'test_questions': None
    #             }
    #             initial.append(d)
    #
    # def give_answer(self, user_pk, card, correct_answer):
    #     '''
    #     You will have a set of 10 initial questions.
    #     For each question that you get wrong, we will make a training and a test session
    #
    #
    #     generate the initial questions, when they have all been answered, iterate over the
    #     ones with wrong answers and train test
    #     '''
    #     user_profile = UserProfile.objects.get(pk=user_pk)
    #     initial = json.loads(user_profile.initial_questions)
    #
    #     # If you are in initial mode, you put the answer in the right place
    #     if user_profile.mode == 'initial':   # maybe call this explore mode?
    #         for q in initial:
    #             if q['pk'] == card.pk:
    #                 q['result'] = correct_answer
    #                 user_profile.initial_cards = json.dumps(initial)
    #
    #         # If all of the initial questions have been answered, make the train and test cards
    #         all_answered = [q['result'] for q in initial].any(None)
    #         if all_answered:
    #             for q in initial:
    #                 if not q['result']:
    #                     card = Card.object.get(pk=q['pk'])
    #                     q['train_questions'] = card.similar_cards[5:10]
    #                     q['test_questions'] = card.simlar_cards[:5]
    #
    #             user_profile.initial_cards = initial
    #
    #             # change the mode
    #             user_profile.mode = 'train'
    #             user_profile.save()
    #
    #     # If you are in train mode, you just take the first card from the train list
    #     # and move it to correct or incorrect.
    #     if user_profile.mode == 'train':
    #         questions = json.loads(user_profile.train_questions)
    #
    #         target = user_profile.all_correct if correct_answer else user_profile.all_incorrect
    #         target_json = json.loads(target)
    #
    #         # create the array if it doesn't exist
    #         if not target_json:
    #             target_json = []
    #         target_json.append(questions[0])
    #
    #         target = json.dumps(target_json)
    #         user_profile.train_questions = json.dumps(questions[1:])
    #         user_profile.save()
    #
    #     # If you are in test mode,
    #     if user_profile.mode == 'test':
    #
    #         pass
    #

    #







