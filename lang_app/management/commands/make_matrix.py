from django.core.management.base import BaseCommand, CommandError
from lang_app.models import Card, Sentence
from utils.comparer.comparer import TreeComparer
import csv
from tqdm import tqdm


class Command(BaseCommand):

    help = '''
        Creates a matrix (csv) of comparisons between card objects using the tree comparer. The command can
        be run mulitple times and it will continue where it left off. This only actually calculates half 
        (the upper triangle) of the matrix to save time. This means that the resulting matrix should be used
        with the matrix wrapper class.
        '''
    comp = TreeComparer()
    path = '/home/stuart/PycharmProjects/workspaces/language_app_project/data/matrix_1989.csv'

    def handle(self, *args, **options):

        with open(self.path, 'a') as file:
            writer = csv.writer(file, delimiter=',')

            index = self.get_start_point()
            cards_this_run = Card.objects.all()[index:]
            all_cards = Card.objects.all()
            iterator = index + 1

            for card_i in cards_this_run:
                print("Working on card: {}/{}".format(card_i.pk, len(all_cards)))
                m = [0.0 for x in range(iterator)] 
                m += [self.comp.compare(card_i, card_j) for card_j in tqdm(all_cards[iterator:])]
                iterator += 1
                writer.writerow(m)

    def get_start_point(self):

        with open(self.path, 'r') as file:
            reader = csv.reader(file, delimiter=',')
            counter = 0
            for row in reader:
                counter += 1
        return counter














