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

        Improvement: The picker at the moment will try and find the next most similar card when
        the user gets a question wrong, this often results in a wrong answer resulting in a
        question with the same sentence and a different chunk. This is annoying that you are seeing the
        same question again. Change it so that you see the next most similar question with
        a different question.

        Addition: The picker should not show sentences that contain more than one
        uncommon word.


    '''

    def __init__(self):
        self.comp = TreeComparer()

        # Only use the cards that have one or less uncommon words
        # self.filtered_cards = Card.objects.filter(sentence__uncommon_words_score__lt=2)
        self.filtered_cards = Card.objects.all()

        self.cards_list = [card for card in self.filtered_cards]

    def pick(self, card, answered_correctly):

        if answered_correctly == 'True':
            return self.cards_list[randint(0, len(self.filtered_cards))]
        else:

            if card.similar_cards != 'this':
                # If the card has pre-calculated similar cards, use that
                similar_card_pks = json.loads(card.similar_cards)

            else:  # otherwise you will need to calculate it

                # Get all cards, excluding the one that the user has just seen.
                other_cards = [c for c in self.all_cards if c != card]

                # iterate over all other cards getting their comparison score
                results = [(other_card.pk, self.comp.compare(card, other_card)) for other_card in tqdm(other_cards)]

                # sort based on the comparison values
                sorted_values = sorted(results, key=lambda item: item[1])[10]

                # get just the pks
                similar_card_pks = [tup[0] for tup in sorted_values]

            # Get the most similar card that has a sentence different to the current one
            next_card = None
            for pk in similar_card_pks:
                try:
                    other_card = self.filtered_cards.get(pk=pk)
                    if other_card.sentence != card.sentence:
                        next_card = other_card
                except:
                    pass
                    # because of the filtering, it is possible that none of most similar cards
                    # are in the filtered query set and the get call can't find them. This will throw
                    # and exception


            # You are only selecting from the ten most similar cards, so you might not find one from
            # a different sentence. Just take the most similar card even if from the same sentence
            # in this case.
            next_card = self.filtered_cards.get(pk=similar_card_pks[0]) if not next_card else next_card

            print("->previous chunk: {}\n->next chunk: {}\n->comparison: {}".format(card.chunk,
                                                                                 next_card.chunk,
                                                                                 self.comp.compare(card, next_card)))
            return next_card




