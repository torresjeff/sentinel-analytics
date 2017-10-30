#!/usr/bin/python3
import pymongo
from enum import Enum
import csv
import datetime
from knowledge_base import KnowledgeBase
from model import Facebook
import re
import numpy as np

if __name__ == '__main__':
    fb = Facebook()
    kb = KnowledgeBase()    

    lideres_opinion = kb.read_knowledge_base('../base-conocimiento/lideres-opinion.all.txt')
    lideres_opinion = kb.get_words_as_list(lideres_opinion)
        

    query_posts_lideres = fb.generate_regex_query(['message'], lideres_opinion)

    res = fb.query('comments', query_posts_lideres)

    for r in res:
        if 'message' in r:
            r['message'] = re.sub(r"\s", " ", r['message'])

    random_list = np.random.choice(res, 200, replace=False)
    
    with open('comments_polarity.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(['comentario', 'polaridad'])
        for r in random_list:
            # [0] = message, [1] = polarity
            row = ['', '']
            if 'message' in r:
                row[0] = r['message']
            csvwriter.writerow(row)
    