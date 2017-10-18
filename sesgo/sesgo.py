#!/usr/bin/python3
import sys, os
home = os.environ.get('HOME')
lib_dir = home + '/workspace/analytics/util'
sys.path.append(lib_dir)
from model import Facebook
from knowledge_base import KnowledgeBase
import datetime
import pymongo
import json
from dateutil.relativedelta import relativedelta
import re


class Sesgo:
    def sesgo_publicaciones(self, posts, page_id):
        res = {
            'posts': 0
        }
        pattern = re.compile(page_id + '_[0-9]+')
        for p in posts:
            if pattern.match(p['_id']):
                print(page_id, "matches", p['_id'])
                res['posts'] += 1

        return res

    

if __name__ == '__main__':
    fb = Facebook()
    sesgo = Sesgo()
    kb = KnowledgeBase()
    now = datetime.datetime.now()

    jsonConfig = None
    with open(home + '/workspace/facebook-scraper-py/config.medios.json') as data_file:
        jsonConfig = json.load(data_file)
    
    if jsonConfig is not None:
        pages = jsonConfig['pages']
        #print(pages)
        palabras_corrupcion = kb.read_knowledge_base('../base-conocimiento/palabras-corrupcion.txt')
        casos_corrupcion = kb.read_knowledge_base('../base-conocimiento/casos-corrupcion.txt')
        instituciones = kb.read_knowledge_base('../base-conocimiento/instituciones.txt')
        lideres_opinion = kb.read_knowledge_base('../base-conocimiento/lideres-opinion.txt')
        partidos_politicos = kb.read_knowledge_base('../base-conocimiento/partidos-politicos.txt')

        # TODO: hacer un summary global (desde enero de 2016, para comparar que tanto hablan los medios de corrupcion/partidos/lideres durante ese periodo de tiempo)
        while now.year >= 2016:
            print(now.year, now.month)
            res = fb.query('sesgo', {"month": now.month, "year": now.year, "entity": "casos"})
            if res is None:
                print("res is None")
            elif len(res) == 0: # No reaction count for that month/year, so create a new summary for that month/year
                obj_insert = {}
                obj_insert['medios'] = {}
                for p in pages:
                    page_id = str(p['id'])
                    obj_insert['medios'][page_id] = {}
                for k, v in casos_corrupcion.items():
                    query_casos_corrupcion = fb.generate_regex_query_for_date(now.year, now.month, ['message', 'name', 'description'], v,
                        whole_sentence=False, wrapped=True)
                    posts = fb.query('posts', query_casos_corrupcion)
                    # TODO: parametrizar 'casos'
                    for p in pages:
                        page_id = str(p['id'])
                        obj_insert['medios'][page_id][k] = sesgo.sesgo_publicaciones(posts, page_id)

                    #results = {}
                    #results['short_name'] = k
                    #results['friendly_name'] = v['friendly_name']
                    #obj_insert['casos'].append(results)

                obj_insert['month'] = now.month
                obj_insert['year'] = now.year
                obj_insert['entity'] = "casos"
                fb.insert('sesgo', obj_insert)
            elif len(res) > 0:
                print(now.year, now.month, "already has activity_count summary")
            now -= relativedelta(months=1)
