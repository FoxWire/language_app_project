from django.core.management.base import BaseCommand
from lang_app.models import Question
from utils.comparer.comparer import TreeComparer
import csv
from tqdm import tqdm
from django.conf import settings
from math import floor
import multiprocessing
import os
from time import sleep
import re

class Command(BaseCommand):
    help = '''
        Creates a matrix (csv) of comparisons between card objects using the tree comparer. 
            - Can be run multiple times, will continue from where it was last stopped
            - Only calculates half (the upper triangle) of the matrix to save running time.
            - Uses multiprocessing
        '''
    matrix_size = len(Question.objects.all())
    comp = TreeComparer()
    cores = 1

    def handle(self, *args, **options):

        # Get the next row that you want to work on
        missing, start_point = self.get_continue_point()
        if start_point >= self.matrix_size and not missing:
            print("Already done")
        else:

            completed_row_count = start_point
            running_processes = []
            all_processes = []

            # Add the missing cards onto the ones that you are using for this run
            list_of_cards = [Question.objects.get(pk=pk) for pk in missing] + [c for c in Question.objects.all()[start_point:self.matrix_size]]

            # Create a list of all the processes that you will be running, but don't start them
            for card in list_of_cards:
                process = multiprocessing.Process(target=self.work, args=(card,))
                all_processes.append(process)

            # copy all processes into waiting processes
            waiting_processes = [process for process in all_processes]

            # Start the first three processes
            for i in range(self.cores):
                process = waiting_processes.pop(0)
                running_processes.append(process)
                process.start()

            # This needs to run until all the processes are complete
            while waiting_processes:
                sleep(2)
                # Remove any processes that have completed
                for i, process in enumerate(running_processes):
                    if not process.is_alive():
                        completed_row_count += 1
                        print("{}/{} completed".format(completed_row_count, self.matrix_size))
                        del running_processes[i]

                # Add another process from waiting to running and start it
                if len(running_processes) < self.cores:
                    process = waiting_processes.pop(0)
                    running_processes.append(process)
                    process.start()

            # Wait until all the processes are done
            for process in all_processes:
                process.join()

            # Then join all the other files into one matrix
            all_rows = []
            for file_name in os.listdir(os.path.join(settings.BASE_DIR, 'data', 'matrix_data')):
                path = os.path.join(settings.BASE_DIR, 'data', 'matrix_data', file_name)
                with open(path, 'r') as file:
                    reader = csv.reader(file, delimiter=',')
                    for line in reader:
                        all_rows.append((self.count_zeros(line), line))

            all_rows = sorted(all_rows, key=lambda y: y[0])

            # write it to the new file
            path = os.path.join(settings.BASE_DIR, 'data', 'matrix_{}_master.csv'.format(self.matrix_size))
            with open(path, 'w') as file:
                writer = csv.writer(file, delimiter=',')
                for row in all_rows:
                    writer.writerow(row[1])

    def count_zeros(self, line):
        total = 0
        for val in line:
            if val != '0.0':
                break
            total += 1
        return total

    def work(self, card):

        index = card.pk
        row = [0.0 for x in range(index)]
        for other_card in Question.objects.all()[index:self.matrix_size]:
            row.append(self.comp.compare(card, other_card))

        file_name = "row_{}.csv".format(card.pk)
        path = os.path.join(settings.BASE_DIR, 'data', 'matrix_data', file_name)
        with open(path, 'a') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(row)

    @staticmethod
    def get_continue_point():

        files = os.listdir(os.path.join(settings.BASE_DIR, 'data', 'matrix_data'))
        pks = [int(re.findall(r'[0-9]+', file)[0]) for file in files]

        # Find any missing ones
        maximum = 0
        missing = []
        if files:
            maximum = max(pks)
            missing = [i for i in range(1, maximum + 1) if i not in pks]
        return missing, maximum



