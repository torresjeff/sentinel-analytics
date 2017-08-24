#!/usr/bin/python3
import sys
import csv
import unicodedata


dict = {}

def readFile(name, separator=';'):
	global dict
	with open(name, newline='') as csvFileBow:
		reader = csv.reader(csvFileBow, delimiter=separator)
		for row in reader:
			#print(row[0].lower())
			key = delete_accents(row[0].lower())
			value = 1 if int(row[1]) > 0 else -1 if int(row[1]) < 0 else 0
			dict[key] = value


		return reader

def delete_accents(_word):
	return ''.join((c for c in unicodedata.normalize('NFD', _word) if unicodedata.category(c) != 'Mn'))

def writeFile(name, separator=';'):
	global dict
	with open(name, 'w', newline='') as csvfile:
		writer = csv.writer(csvfile, delimiter=separator)
		for key, value in dict.items():
			writer.writerow([key, value])

if __name__ == '__main__':
	csl = readFile("lexicons/CSL.csv")
	politico = readFile("lexicons/politico.txt", '\t')
	writeFile('lexicons/CSL_politico.csv')
	#print(dict)


