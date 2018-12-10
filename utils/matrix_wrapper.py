import os
import sys
import django
sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

import csv
import numpy as np
from language_app_project.settings import BASE_DIR

'''
The initialiser takes a path, it reads in from the path to create a numpy array.
This allows you to interact with the underlying matrix.
Only requires the upper triangle of the matrix. 
'''


class MatrixWrapper:

    matrix = None

    def __init__(self):

        # Read in the comparison array from the file
        path = os.path.join(BASE_DIR, 'data', 'matrix_1265_master.csv')
        temp_array = []
        with open(path, 'r') as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                float_row = [float(r) for r in row]
                temp_array.append(float_row)

        np_array = np.array(temp_array)

        '''
        For some of the larger arrays, I am only computing half of the values because of the
        time needed for the tree comparison to run on all questions. The next block just checks
        if only half of the array is present and mirrors it.
        '''
        if not (np_array[0] == np_array[:, 0, None].T[0]).all():

            # Use mask to combine the array and the transposed array.
            mask = np_array != 0
            np_array.T[mask] = np_array[mask]

        self.matrix = np_array

    def get_value(self, x, y, pk=False):
        # Returns the values if within the size of the array else none

        if pk:
            x -= 1
            y -= 1

        a, b = self.matrix.shape
        return self.matrix[x][y] if x < a and x < b and y < a and y < b else None

    def get_row(self, pk):
        return self.matrix[pk - 1]

    def get_similar_question_pks(self, pk):

        """
        For the pk passed in get a list of all other question pk, sorted in the order of
        similarity to pk passed in.
        :param pk:
        :return:
        """
        size = self.matrix.shape[0]

        # Get list of tuples with matrix indexes and comparison values for all other questions
        # NOTE: why i + 1 here? You need to return a list of pks not of indices in for the matrix

        pks = [(i + 1, self.get_value(pk - 1, i)) for i in range(size)]

        # sort on comparison value
        sorted_values = sorted(pks, key=lambda y: y[1])

        # remove the values and remove the first value, ie the comparison to its self
        return [tup[0] for tup in sorted_values][1:]

    def get_matrix(self):
        return self.matrix

