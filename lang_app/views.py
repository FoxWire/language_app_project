from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from lang_app.models import Question, UserState
from lang_app.forms import UserForm, UserProfileForm
from utils.question_picker.picker import Picker
from utils.parser.parser import Parser
from utils.policies.polices import PolicyOne, PolicyTwo, PolicyThree
from utils.parser.lemmatizer import Lemmatizer
from utils.comparer.comparer import TreeComparer
from random import choice
import csv
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse


# picker = Picker()
# parser = Parser()
# comp = TreeComparer()
lem = Lemmatizer()


policies = (
    PolicyOne(),
    PolicyTwo(),
    PolicyThree()
)

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


# This is the normal index
def index(request):

    context = {}

    if request.user.is_authenticated:

        # Get the user state object
        user_state = UserState.objects.get(user=request.user)

        # Get the policy for this user state
        policy = policies[user_state.policy_id]

        context = None

        '''
        The get request will only be made when the user logs onto the site.
        '''
        if request.method == 'GET':

            # Get the next question from the policy, passing in the user state
            question = policy.get_question(user_state)

            context = {
                'question_number': question.pk,
                'question_data': question.ask_question(),
                'lem_items': lem.lemmatize(question),
            }

        '''
        With the post request, the user will pass their answer for the previous question and 
        return the result
        '''
        if request.method == 'POST':

            # Get the previous question that has just been answered
            question_number = request.POST.get('question_number')
            user_answer = request.POST.get('user_answer')
            question = Question.objects.get(pk=question_number)
            correct_bool = question.give_answer(user_answer)[0]

            policy.update_state(user_state, question_number, user_answer, correct_bool)

            context = {
                'show_answer': True,
                'question_number': question.pk,
                'question_data': question.ask_question(),
                'correct_bool': correct_bool,
                'user_answer': user_answer,
                'chunk': question.chunk,
                'chunk_translation': question.chunk_translation
            }

    return render(request, 'lang_app/index.html', context)


# # Ajax listener
def get_hint(request):

    if request.method == 'GET':
        card_id = request.GET.get('card_id')
        shown_words = request.GET.get('shown_words')
        word = ""
        if card_id:
            chunk = Card.objects.get(id=int(card_id)).chunk

            if shown_words:
                # split the chunk and remove any words that have already been shown
                words = [word for word in chunk.split(' ') if word not in shown_words]
                word = choice(words) if words else ''
            else:
                word = choice([word for word in chunk.split(' ')])

        return HttpResponse(word)

