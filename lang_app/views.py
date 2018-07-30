from django.shortcuts import render
from lang_app.models import Card
from random import randint


# Create your views here.
def index(request):

    context = None
    if request.method == 'GET':

        # Get a random card
        all_cards = Card.objects.all()

        card = all_cards[randint(0, len(all_cards))]
        data = card.ask_question()

        context = {
            'question_number': card.pk,
            'question_data': data,
        }

    if request.method == 'POST':
        user_answer = request.POST.get('user_answer')

        card = Card.objects.get(pk=request.POST.get('question_number'))
        correct_bool = card.give_answer(user_answer)[0]

        context = {
            'show_answer': True,
            'question_data': card.ask_question(),
            'correct_bool': correct_bool,
            'user_answer': user_answer,
            'chunk': card.chunk,
            'chunk_translation': card.chunk_translation
        }

    return render(request, 'lang_app/template.html', context)

