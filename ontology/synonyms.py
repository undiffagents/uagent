import csv


def read_synonyms():
    with open('ontology/synonyms.csv', 'r') as f:
        for line in csv.reader(f):
            if line:
                yield (line[0], line[1])
