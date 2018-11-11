from django.core.management.base import BaseCommand, CommandError
from lang_app.models import Card, Sentence
from utils.comparer.comparer import TreeComparer
from utils.matrix_wrapper import MatrixWrapper
from tqdm import tqdm
import json


class Command(BaseCommand):

    help = "Works out the similar cards for each card"
    comp = TreeComparer()

    def handle(self, *args, **options):

        mw = MatrixWrapper()

        all_cards = Card.objects.all()
        for card in all_cards:

            # check if this card has already been calculated
            if not card.similar_cards:

                # Get all cards - excluding this one
                other_cards = Card.objects.exclude(pk=card.pk)
                results = []
                # iterate over all other cards getting their comparison
                print("Working on card {} of {}".format(card.pk, len(Card.objects.all())))
                for other_card in tqdm(other_cards):

                    # Try to get the value from the matrix wrapper, if null then compute it
                    value = mw.get_value(card.pk, other_card.pk)
                    if not value:
                        value = self.comp.compare(card, other_card)
                    results.append((other_card, value))

                # Get the ten most similar cards
                sorted_by_comp = sorted(results, key=lambda item: item[1])[:100]

                # Get list of the pks as json
                pks_as_json = json.dumps([c[0].pk for c in sorted_by_comp])

                # Put the json into the sentence object in the db
                card.similar_cards = pks_as_json
                card.save()







