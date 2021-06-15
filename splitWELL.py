import csv

csv_file = 'output.csv'


def csv_header(x):
    with open('WELL-'+ x + '.csv', 'w') as myfile, open(csv_file, "r") as master:
        myfile.write(next(master))
        myfile.close()
        master.close()


def csv_writer(y, value):
    for row in y:
        if value == row[1]:
            with open('WELL-'+ value + '.csv', 'a') as myfile:
                spamwriter = csv.writer(myfile)
                spamwriter.writerow(row)
                myfile.close()


def csv_reader(z):
    with open(z , 'r') as spam:
        spamreader = csv.reader(spam, delimiter=',')
        csv_writer(spamreader, value)


ID = ['1','2','3','4','5','6']


for value in ID:
    try:
        csv_reader(value)
        csv_reader(csv_file)
    except:
        csv_header(value)
        csv_reader(csv_file)

