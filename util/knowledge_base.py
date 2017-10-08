#!/usr/bin/python3
import csv

class KnowledgeBase:
    #def __init__(self):

    def read_knowledge_base(self, file):
        words = []
        with open(file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            words = {}
            for row in reader:
                if row[2] not in words:
                    words[row[2]] = {'synonyms': [], 'friendly_name': ''}
                words[row[2]]['synonyms'].append({'word': row[0], 'match_exact': True if row[1] == 'true' else False})
                # TODO: esto está overriding el concepto de 'corrupción' (knowledge base de corrupcion)
                # solo está quedando la ultima palabra que coja de la base de corrupcion como friendly name
                words[row[2]]['friendly_name'] = row[3]
        #print(words['corrupcion'])
        return words
    
    def get_words_as_list(self, read_knowledge_base):
        palabras = []
        for key, value in read_knowledge_base.items():
            for v in value['synonyms']:
                palabras.append(v['word'])
        
        return palabras
