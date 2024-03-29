from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from lang_app.models import Question, UserState, Session
from utils.policies.policies import PolicyOne, PolicyTwo, PolicyThree
from utils.parser.lemmatizer import Lemmatizer
from django.contrib.auth import logout
from django.urls import reverse
from django.core.management import call_command

lem = Lemmatizer()

policies = {
    1: PolicyOne(),
    2: PolicyTwo(),
    3: PolicyThree()
}


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def index(request):

    context = {}

    if request.user.is_authenticated:

        # Get the user state object
        user_state = UserState.objects.get(user=request.user)

        # Get the policy for this user state
        policy = policies[user_state.current_policy_id]

        context = None

        if request.method == 'GET':

            if request.GET.get('next_session'):
                user_state.current_session = None

            if user_state.current_session and user_state.current_session.is_complete:
                context = {
                    'session_complete': True,

                    # Don't want to pass the actual session number here, just the count of session
                    'session_number': len(Session.objects.filter(user_state=user_state))
                }
                # The session is over so dump to json
                call_command('output_session', user_state.current_session.pk)
            else:
                # Get the next question from the policy, passing in the user state
                question = policy.get_question(user_state)

                lem_items = lem.lemmatize(question)

                # Get a list of the word stems that occur more than once in the sentence chunk
                lems = [lem_item['lem'].lower() for lem_item in lem_items]
                duplicate_stems = list(set([l for l in lems if lems.count(l) > 1]))

                # Create a list of all the possible words that could be duplicated
                all_duplicates = [d for d in duplicate_stems]
                for l in lem_items:
                    if l['lem'] in all_duplicates:
                        all_duplicates += l['possible_words']

                # For each of the possible words that corresponds to a duplicate, an extra tag must be added
                # to differentiate them on client side.
                for duplicate in duplicate_stems:
                    i = 0
                    for lem_item in lem_items:
                        if lem_item['lem'].lower() == duplicate:
                            lem_item['possible_words'] = [possible_word.lower() + '_' + str(i) for possible_word in lem_item['possible_words']]
                            i += 1

                context = {
                    'question_number': question.pk,
                    'question_data': question.ask_question(),
                    'lem_items': lem_items,
                    'session_complete': user_state.current_session.is_complete,
                    'session_number': user_state.current_policy_id,
                    'duplicate_lems': all_duplicates
                }

        # With the post request, the user will pass their answer for the previous question and
        # return the result
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
                'chunk_translation': question.chunk_translation,
            }

    return render(request, 'lang_app/index.html', context)


