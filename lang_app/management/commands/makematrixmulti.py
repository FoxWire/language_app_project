from django.core.management.base import BaseCommand
from lang_app.models import Card
from utils.comparer.comparer import TreeComparer
import csv
from tqdm import tqdm
from django.conf import settings
from math import floor
import multiprocessing
import os


class Command(BaseCommand):

    help = '''
        Creates a matrix (csv) of comparisons between card objects using the tree comparer. 
            - Can be run multiple times, will continue from where it was last stopped
            - Only calculates half (the upper triangle) of the matrix to save running time.
            - Uses multiprocessing
        '''
    matrix_size = len(Card.objects.all())
    comp = TreeComparer()
    path = None
    cores = 3

    def handle(self, *args, **options):

        # take the length of matrix and half it 4 times
        values, x = [], 1
        for i in range(self.cores - 1):
            x = x / 2
            values.append(x)

        processes = []
        range_start = 0
        for i, value in enumerate(reversed(values)):

            range_end = floor(self.matrix_size * value)
            card_range = Card.objects.all()[range_start:range_end]
            name = "process_{}".format(i)
            process = multiprocessing.Process(target=self.work, args=(name, card_range, range_start))
            processes.append(process)
            range_start = range_end
            process.start()

        # The loop doesn't take care of the last process
        card_range = Card.objects.all()[range_start:self.matrix_size]
        name = "process_{}".format(self.cores - 1)
        process = multiprocessing.Process(target=self.work, args=(name, card_range, range_start))
        processes.append(process)
        process.start()

        for process in processes:
            process.join()

        print("All tasks complete")

        # Read each row from all of the files into one big list
        all_lines = []
        for i in range(self.cores):
            file_name = "matrix_{}_process_{}.csv".format(self.matrix_size, i)
            path = os.path.join(settings.BASE_DIR, 'data', file_name)
            with open(path, 'r') as file:
                reader = csv.reader(file, delimiter=',')
                for line in reader:
                    all_lines.append(line)

        # # Make sure the data has the correct structure
        # num_zeros = 0
        # for line in all_lines:
        #     count = line.count('0.0')
        #     if count != num_zeros + 1:
        #         # raise Exception("Master list cannot be properly assembled")
        #         pass
        #     num_zeros = count
            
        # # Iterate over all lines and put it all into a new file
        # path = os.path.join(settings.BASE_DIR, 'data/matrix_{}_master.csv'.format(self.matrix_size))
        # with open(path, 'w') as file:
        #     writer = csv.writer(file, delimiter=',')
        #     for row in all_lines:
        #         writer.writerow(row)

        # Delete the temporary files
        # for i in range(self.cores):
        #     os.remove(os.path.join(settings.BASE_DIR, 'data/matrix_{}_process_{}.csv'.format(self.matrix_size, i)))

    def work(self, task_name, card_range, start_point):

        # Set the name of the path
        path = settings.BASE_DIR + '/data/matrix_{}_{}.csv'.format(str(self.matrix_size), task_name)

        with open(path, 'a') as file:
            writer = csv.writer(file, delimiter=',')

            # You need to decide if you are starting with a new file or continuing with an old file
            continue_point = self.get_continue_point(path)
            index = continue_point + start_point

            # Check if the work for this task is already complete
            if continue_point < len(card_range):

                all_cards = Card.objects.all()[:self.matrix_size]
                iterator = index + 1

                for card_i in tqdm(card_range[continue_point:]):
                    # print("Working on card: {}/{}".format(iterator, len(all_cards)))
                    m = [0.0 for x in range(iterator)]
                    m += [self.comp.compare(card_i, card_j) for card_j in all_cards[iterator:]]
                    iterator += 1
                    writer.writerow(m)

            print("{} complete".format(task_name))

    # def get_continue_point(self, path):
    #
    #     with open(path, 'r') as file:
    #         reader = csv.reader(file, delimiter=',')
    #         counter = 0
    #         for row in reader:
    #             # check that the size of the rows in the file match the matrix size
    #             if len(row) != self.matrix_size:
    #                 raise Exception("Matrix dimension mismatch")
    #             counter += 1
    #     return counter
