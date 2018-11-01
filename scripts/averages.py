'''
collect the values from each of the user function files and
write the averages to the user function file
'''

import csv


path = "/home/stuart/PycharmProjects/workspaces/language_app_project/data/"
averages = []


with open(path + "user_function_a.csv", 'r') as file_1, open(path + "user_function_b.csv", 'r') as file_2, open(path + "user_function_c.csv", 'r') as file_3:
    reader_a = csv.reader(file_1, delimiter=',')
    reader_b = csv.reader(file_2, delimiter=',')
    reader_c = csv.reader(file_3, delimiter=',')

    for a, b, c in zip(reader_a, reader_b, reader_c):

        # first check that the numbers all line up
        if not a[0] == b[0] == c[0]:
            print("something doesn't match")

        # get the average
        average = round((float(a[1]) + float(b[1]) + float(c[1])) / 3)
        averages.append((a[0], average))

with open(path + "user_function.csv", 'w') as out:
    writer = csv.writer(out, delimiter=',')
    for average in averages:
        writer.writerow([average[0], average[1]])





