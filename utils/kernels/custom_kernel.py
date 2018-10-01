import numpy as np
import csv
from sklearn.gaussian_process.kernels import Kernel, StationaryKernelMixin, NormalizedKernelMixin


class CustomKernel(StationaryKernelMixin, NormalizedKernelMixin, Kernel):

    def __init__(self, length_scale=100):

        '''
            The custom kernel basically just accesses the precomputed comparison values
            for each of the cards. So it needs to have access to these values via a file that it reads into
            memory. To make the creation of this file faster, you only created half of it so you will have to use the
            matrix wrapper object here, as it allows you to pretend that you have the full matrix.
        '''

        # Read the csv into memory, there should only be 100 items in it at the moment.
        path = '/home/stuart/PycharmProjects/workspaces/language_app_project/data/matrix_100.csv'
        array = []
        with open(path, 'r') as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                float_row = [float(r) for r in row]
                array.append(float_row)
        self.array = np.array(array)
        self.length_scale = length_scale

    def __call__(self, x, y=None, eval_gradient=False):
        '''
            Implements this:
            k(xx_i, xx_j) = exp( -1/2 (d(xx_i, xx_j )^2) / length_scale )

            Returns an np array. This is used in the fitting and predicting parts of the GP.
            When fitting, only the X argument is provided. In this case we make an array of the
            disances (in terms of the similarity function) of all the X values from all other
            X values. If the Y argument is provided, we can assume that we are predicing,
            meaning that we should work out the distances between all X and all Y values.

            In each case we use the values in X (and Y) as indices into the array of precomputed
            distances.

            you could pad out the indices so that they are the same length and then just chop the
            stuff off that you don't need
        '''

        values_x = x[:, 0]
        values_y = y[:, 0] if Y is not None else values_x

        x = self.array[[values_x], :][0]
        x = x[:, [values_y]].reshape(len(values_x), len(values_x))

        kernel = np.exp(-.5 * (x ** 2) / self.length_scale)
        return np.atleast_2d(kernel)
