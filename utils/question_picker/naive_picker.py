from utils.comparer.comparer import TreeComparer
from lang_app.models import Card
from random import randint
from tqdm import tqdm
import json


class NaivePicker:
    '''
        This naive picker class takes a card and a boolean variable denoting if the
        user got the question correct or wrong. If they got the card correct, we just return
        another random card. If they get the question wrong, we find the next most similar card
        and return that.

        Note: This does not care about whether card has already been seen or not. This
        will result in a 'stateless' running of the application.
    '''

    def __init__(self):
        self.comp = TreeComparer()
        self.all_cards = [card for card in Card.objects.all()]

    def pick(self, card, answered_correctly):

        if answered_correctly == 'True':
            return self.all_cards[randint(0, len(self.all_cards))]
        else:

            if card.similar_cards != 'this':
                # If the card has pre-calculated similar cards, use that
                similar_data = json.loads(card.similar_cards)
                return Card.objects.get(pk=similar_data[0])

            else:
                # otherwise you will need to calculate it

                # Get all cards, excluding the one that the user has just seen.
                # other_cards = Card.objects.exclude(pk=card.pk)
                other_cards = [c for c in self.all_cards if c != card]

                # iterate over all other cards getting their comparison score
                results = [(other_card, self.comp.compare(card, other_card)) for other_card in tqdm(other_cards)]

                # Get the card that is most similar
                next_card = sorted(results, key=lambda item: item[1])[0]
                print("comparison: {} chunk A: '{}' similar to chunk B: '{}'".format(next_card[1], card.chunk, next_card[0].chunk))
                next_card = next_card[0]

                return next_card

