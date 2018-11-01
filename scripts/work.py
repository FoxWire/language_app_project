
import csv
path = '/home/stuart/PycharmProjects/workspaces/language_app_project/data/user_function.csv'
with open(path, 'r') as into, open("other.csv", 'w') as out:
	reader = csv.reader(into, delimiter=',')
	writer = csv.writer(out, delimiter=',')
	for row in reader:
		if int(row[1]) <= 2:
			writer.writerow([row[1]])	
