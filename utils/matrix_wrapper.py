import os
import sys
import django
sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

import csv
import numpy as np
from language_app_project.settings import BASE_DIR
import re
from lang_app.models import Question
from random import randint
from utils.comparer.comparer import TreeComparer

'''
The initialiser takes a path, it reads in from the path to create a numpy array.
This allows you to interact with the underlying matrix.
Only requires the upper triangle of the matrix. 
'''


class MatrixWrapper:

    matrix = None

    def __init__(self):

        # Find the biggest matrix you can that we have created so far
        # path = os.path.join(BASE_DIR, "data")
        # matrices = [file for file in os.listdir(path) if 'matrix_' in file]
        #
        # file_name, file_size = '', 0
        # for matrix in matrices:
        #     number = int(re.findall(r'[0-9]+', matrix)[0])
        #     if number > file_size:
        #         largest = matrix

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

    def get_value(self, x, y):
        # Returns the values if within the size of the array else none
        a, b = self.matrix.shape
        return self.matrix[x][y] if x < a and x < b and y < a and y < b else None

    def get_similar_(self, row):
        return self.matrix[row]

    def get_matrix(self):
        return self.matrix


if __name__ == "__main__":
    m = MatrixWrapper()
    # print(m.matrix.shape)


    comp = TreeComparer()

    size = m.matrix.shape[0] - 1
    # Now compose a proper test for the 10 matrix
    randnums = [(randint(0, size), randint(0, size)) for x in range(1000)]

    correct = 0
    wrong = 0
    for a, b in randnums:
        result = m.get_value(a, b)
        x = comp.compare(Question.objects.get(pk=a + 1), Question.objects.get(pk=b + 1))
        # print(result, x, result == x)
        if result == x:
            correct += 1
        else:
            wrong += 1

    print("{} correct out of 1000".format(correct))
    print("{} wrong out of 1000".format(wrong))


