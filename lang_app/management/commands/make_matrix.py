from django.core.management.base import BaseCommand, CommandError
from lang_app.models import Card, Sentence
from utils.comparer.comparer import TreeComparer
import csv
from tqdm import tqdm


class Command(BaseCommand):

    help = '''
        Create a matrix of comparisons for each of the cards. Can be run muliple times. Will
        always continue from where it left off on the last execution.
        '''
    comp = TreeComparer()

    def handle(self, *args, **options):

        ## --- USE THIS CODE TO MAKE COMPLETE MATRIX FOR ALL CARDS --- ##
        # Get the index of the last row that was written to the csv file
        index = self.get_start_point()
        cards_this_run = Card.objects.all()[index:]
        all_cards = Card.objects.all()
        total_number_of_cards = len(Card.objects.all())
    
        # Make the comparisons and write the line to the csv
        with open('/home/stuart/Desktop/matrix_2000.csv', 'a') as file:
            writer = csv.writer(file, delimiter=',')
            for i in cards_this_run:
                cols = []
                print("{}/{}".format(i.pk, total_number_of_cards))
                for j in tqdm(all_cards):
                    cols.append(self.comp.compare(i, j))
                writer.writerow(cols)


        ##--- USE THIS CODE TO MAKE CUSTOM MATRIX---##

        # cards = Card.objects.all()[:10]
        
        # total_number_of_cards = len(cards)
    
        # # Make the comparisons and write the line to the csv
        # with open('/home/stuart/Desktop/matrix_new.csv', 'a') as file:
        #     writer = csv.writer(file, delimiter=',')
        #     for i in cards:
        #         cols = []
        #         print("{}/{}".format(i.pk, total_number_of_cards))
        #         for j in tqdm(cards):
        #             cols.append(self.comp.compare(i, j))
        #         writer.writerow(cols)


    def get_start_point(self):

        with open('/home/stuart/Desktop/matrix_2000.csv', 'r') as file:
            reader = csv.reader(file, delimiter=',')
            counter = 0
            for row in reader:
                counter += 1
        return counter














