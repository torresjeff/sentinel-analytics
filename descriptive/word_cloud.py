#!/usr/bin/python3
import sys, os
home = os.environ.get('HOME')
lib_dir = home + '/workspace/analytics/util'
sys.path.append(lib_dir)
from os import path
from model import Facebook
from knowledge_base import KnowledgeBase
import datetime
import pymongo
import json
from dateutil.relativedelta import relativedelta
import re
import numpy as np
# Requiere instalar python3-tk sudo apt-get install python3-tk
from wordcloud import WordCloud

def generate_word_cloud(fb, page_id):
    now = datetime.datetime.now()

    print("generating word_cloud for", page_id)
    query = {"$and": [{"_id": {"$regex": page_id + "_[0-9]+"}}, {"whole_sentence": {"$exists": True}}]}
    results = fb.query("posts", query)
    whole_text = ""
    for r in results:
        whole_text += r['whole_sentence']
    wc = WordCloud(background_color=None, mode="RGBA", collocations=False, width=1920, height=800)
    wc.generate(whole_text)
    img_path = path.join(home + "/workspace/sentinel/public/img/wordclouds/" + str(now.year) + "-" + str(now.month) + "-" + page_id + ".png")
    print(img_path)
    wc.to_file(img_path)
    #print("whole_text", whole_text)
    #print("results for", page_id, "=>", results)


if __name__ == '__main__':
    fb = Facebook()
    kb = KnowledgeBase()
    
    lideres_opinion = kb.read_knowledge_base('../base-conocimiento/lideres-opinion.all.txt')
    config_file = "config.lideres.json"
    
    with open(home + '/workspace/facebook-scraper-py/' + config_file) as data_file:
        jsonConfig = json.load(data_file)
    
    if jsonConfig is not None:
        for p in jsonConfig['pages']:
            generate_word_cloud(fb, str(p['id']))

