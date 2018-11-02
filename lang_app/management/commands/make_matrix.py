from django.core.management.base import BaseCommand, CommandError
from lang_app.models import Card, Sentence
from utils.comparer.comparer import TreeComparer
import csv
from tqdm import tqdm


class Command(BaseCommand):

    help = '''
        Creates a matrix (csv) of comparisons between card objects using the tree comparer. The command can
        be run multiple times and it will continue where it left off. This only actually calculates half 
        (the upper triangle) of the matrix to save time. This means that the resulting matrix should be used
        with the matrix wrapper class. An integer as a command line argument, determines the size of the 
        matrix to be created.
        '''
    matrix_size = len(Card.objects.all())
    comp = TreeComparer()
    path = None

    def add_arguments(self, parser):
        parser.add_argument('matrix_size', nargs='*', type=int)

    def handle(self, *args, **options):

        # Get the size of the matrix from the command line options (default is full matrix)
        opts_list = options['matrix_size']
        if opts_list:
            arg = opts_list[0]
            if arg < self.matrix_size:
                self.matrix_size = arg

        # Set the name of the path
        self.path = '/home/stuart/Desktop/matrix_{}.csv'.format(str(self.matrix_size))

        with open(self.path, 'a') as file:
            writer = csv.writer(file, delimiter=',')

            index = self.get_start_point()
            cards_this_run = Card.objects.all()[index:self.matrix_size]
            all_cards = Card.objects.all()[:self.matrix_size]
            iterator = index + 1

            for card_i in cards_this_run:
                print("Working on card: {}/{}".format(iterator, len(all_cards)))
                m = [0.0 for x in range(iterator)]
                m += [self.comp.compare(card_i, card_j) for card_j in tqdm(all_cards[iterator:])]
                iterator += 1
                writer.writerow(m)

    def get_start_point(self):

        with open(self.path, 'r') as file:
            reader = csv.reader(file, delimiter=',')
            counter = 0
            for row in reader:
                # check that the size of the rows in the file match the matrix size
                if len(row) != self.matrix_size:
                    raise Exception("Matrix dimension mismatch")
                counter += 1
        return counter














