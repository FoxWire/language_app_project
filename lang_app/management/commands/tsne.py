from django.core.management.base import BaseCommand, CommandError
from lang_app.models import Card, Sentence
from utils.comparer.comparer import TreeComparer
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import numpy as np
import csv

class Command(BaseCommand):

    '''
    How does the tsne actaully work again? 
    It uses probabilities to reduce the dimensionality in some way. It also doesn't
    place your data points on a scale, but rather, just in relation to each other,
    based on the comparision function. 

    This implementation of the algorithm takes a list of the instances and compares each instance with 
    every other instance. Normally you would use the standard comparison, but you would have lots of
    dimensions for each datapoint, and they would have to be reduced. The default comparison would be
    euclidean distance. In our case, we don't have any features for the datapoints, but we do have a 
    comparison algorithm so we can just feed that in. I suppose it doesn't really attempt to reduce the 
    dimensionality because it only has one feature, and then it uses your comparison function. 

    Note: The results come out differnt each time. This must be becuase there is some probablility
    in the mix.

    Note: There may be some bugs in this.
    '''


    help = "Creates a plot of the questions using the tsne algorithm"
    comp = TreeComparer()
    array = None

    def handle(self, *args, **options):

        self.array, num_rows = self.create_matrix()

        # Get the pks for the first 10 questions
        pks = [c.pk for c in Card.objects.all()[:num_rows]]

        # create a ndarray
        pk_array = np.array(pks)

        # You need to reshape because you only have a single feature
        pk_array = pk_array.reshape(-1, 1)

        n_sne = 7000
        tsne = TSNE(n_components=2, verbose=1, perplexity=40, n_iter=300, metric=self.compare_precomputed)
        tsne_results = tsne.fit_transform(pk_array)
        self.plot(tsne_results)

    def plot(self, results):
        points_plotted = 0
        for r in results:
            x = r[0]
            y = r[1]
            plt.scatter(x, y, marker='.', c='red')
            points_plotted += 1

        # plt.legend(digits.target_names, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.xlabel('First Principal Component')
        plt.ylabel('Second Principal Component')
        plt.title("TSNE Scatter Plot")
        plt.show()
        print('number of points plotted: ', points_plotted)

    def compare(self, pk_a, pk_b):
        card_a = Card.objects.get(pk=pk_a)
        card_b = Card.objects.get(pk=pk_b)
        return self.comp.compare(card_a, card_b)

    def create_matrix(self):

        # This will make the matrix and also get the number of lines in the csv file
        num_rows = 0
        array = []
        path = '/home/stuart/PycharmProjects/workspaces/language_app_project/data/matrix_1989.csv'
        with open(path, 'r') as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                array.append(row)
                num_rows += 1
        return array, num_rows

    def compare_precomputed(self, pk_a, pk_b):
        # remember that lists are zero indexed and pks are not
        print(int(pk_a[0]), int(pk_b[0]))

        x = int(pk_a[0]) - 1
        y = int(pk_b[0]) - 1

        return float(self.array[x][y])














