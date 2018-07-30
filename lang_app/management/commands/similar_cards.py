from django.core.management.base import BaseCommand, CommandError
from lang_app.models import Card, Sentence
from utils.comparer.comparer import TreeComparer
from tqdm import tqdm
import json
from random import randint


class Command(BaseCommand):

    help = "Works out the similar cards for each card"
    comp = TreeComparer()

    def handle(self, *args, **options):

        all_cards = Card.objects.all()
        for card in tqdm(all_cards):
            # Get all cards - excluding this one
            other_cards = Card.objects.exclude(pk=card.pk)
            results = []
            # iterate over all other cards getting their comparison score
            for other_card in other_cards:
                results.append((other_card, self.comp.compare(card, other_card)))

            # Get the ten most similar cards
            sorted_by_comp = sorted(results, key=lambda item: item[1])[:10]

            # Get list of the pks as json
            pks_as_json = json.dumps([c[0].pk for c in sorted_by_comp])

            # Put the json into the sentence object in the db
            card.similar_cards = pks_as_json
            card.save()






