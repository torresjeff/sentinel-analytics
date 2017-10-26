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
import numpy as np


class Sesgo:
    def sesgo_publicaciones(self, posts, page_id):
        res = {
            'posts': 0
        }
        pattern = re.compile(page_id + '_[0-9]+')
        for p in posts:
            if pattern.match(p['_id']):
                res['posts'] += 1

        return res

    def detect_outliers(self, medios):
        res = {}

        for k, keys in medios.items():
            for k2, v in keys.items():
                res[k2] = []

        for k, keys in medios.items():
            for k2, v in keys.items():
                # TODO: parametrizar posts
                res[k2].append({"page_id": k, "posts": v['posts']})
        1
        #print(res)
        # Sort list
        for k, v in res.items():
            v.sort(key=lambda x: x['posts'])
            outliers = self.detect_outliers_helper([i['posts'] for i in v])
            for i, val in enumerate(v):
                res[k][i]['outlier'] = outliers[i]
        
        #print(res)
        
        #for k, v in res.items():

        return res
    
    # arr = [{"page_id": "123", "posts": 5}, {"page_id": "456", "posts": 8}]
    # arr must be sorted
    def detect_outliers_helper(self, arr, outlier_constant=1.5):
        a = np.array(arr)
        upper_quartile = np.percentile(a, 75)
        lower_quartile = np.percentile(a, 25)

        IQR = (upper_quartile - lower_quartile) * outlier_constant
        quartile_set = (lower_quartile - IQR, upper_quartile + IQR)
        #print("upper_quartile", quartile_set[1])
        #print("lower_quartile", quartile_set[0])
        res = []
        for x in arr:
            if x < quartile_set[0]:
                #print(x, "is an outlier (small)")
                res.append("small")
            elif x > quartile_set[1]:
                #print(x, "is an outlier (large)")
                res.append("large")
            else:
                #print(x, "is normal")
                res.append("normal")
        return res

def calcular_sesgo(fb, sesgo, knowledge_base, entity, config_file):
    now = datetime.datetime.now()
    jsonConfig = None
    # TODO: cambiar a config.medios.json
    with open(home + '/workspace/facebook-scraper-py/' + config_file) as data_file:
        jsonConfig = json.load(data_file)
    
    if jsonConfig is not None:
        pages = jsonConfig['pages']
        #print(pages)
        

        # TODO: hacer un summary global (desde enero de 2016, para comparar que tanto hablan los medios de corrupcion/partidos/lideres durante ese periodo de tiempo)
        #while now.year >= 2017 and now.month >= 10:
        #print(now.year, now.month)
        res = fb.query('sesgo', {"entity": entity, "year": now.year, "month": now.month})
        if res is None:
            print("res is None")
        elif len(res) == 0: # No reaction count for that month/year, so create a new summary for that month/year
            obj_insert = {}
            obj_insert['medios'] = {}
            for p in pages:
                page_id = str(p['id'])
                obj_insert['medios'][page_id] = {}
            for k, v in knowledge_base.items():
                query_knowledge_base = fb.generate_regex_query(['message', 'name', 'description'], v,
                    whole_sentence=False, wrapped=True)
                posts = fb.query('posts', query_knowledge_base)
                # TODO: parametrizar 'casos'
                for p in pages:
                    page_id = str(p['id'])
                    obj_insert['medios'][page_id][k] = sesgo.sesgo_publicaciones(posts, page_id)

            obj_insert['month'] = now.month
            obj_insert['year'] = now.year
            obj_insert['entity'] = entity
            #print("obj_insert['medios']", obj_insert['medios'])
            outliers = sesgo.detect_outliers(obj_insert['medios'])
            # k = case name
            # v = array of summaries (# of posts, outlier or not, page)
            for k, v in outliers.items():
                # v is an array of summaries per page
                for summary in v:
                    #print(summary)
                    #print(summary['page_id'], "=>", k, "=>", obj_insert['medios'][summary['page_id']])
                    obj_insert['medios'][summary['page_id']][k]['outlier'] = summary['outlier']

            fb.insert('sesgo', obj_insert)
        elif len(res) > 0:
            print(now.year, now.month, "already has sesgo summary")
        now -= relativedelta(months=1)
    
def calcular_sesgo_corrupcion_entidades(fb, sesgo, knowledge_base_corrupcion, knowledge_base_entidades, knowledge_base_casos, entity, config_file):
    now = datetime.datetime.now()
    jsonConfig = None
    # TODO: cambiar a config.medios.json
    with open(home + '/workspace/facebook-scraper-py/' + config_file) as data_file:
        jsonConfig = json.load(data_file)
    
    if jsonConfig is not None:
        pages = jsonConfig['pages']
        #print(pages)
        

        # TODO: hacer un summary global (desde enero de 2016, para comparar que tanto hablan los medios de corrupcion/partidos/lideres durante ese periodo de tiempo)
        #while now.year >= 2017 and now.month >= 10:
        #print(now.year, now.month)
        res = fb.query('sesgo', {"entity": entity, "year": now.year, "month": now.month})
        if res is None:
            print("res is None")
        elif len(res) == 0: # No reaction count for that month/year, so create a new summary for that month/year
            obj_insert = {}
            obj_insert['medios'] = {}
            for p in pages:
                page_id = str(p['id'])
                obj_insert['medios'][page_id] = {}
            
            queries_corrupcion = {}
            for k, v in knowledge_base_corrupcion.items():
                queries_corrupcion = fb.generate_regex_query(['message', 'name', 'description'], v,
                    whole_sentence=False, wrapped=True)
            for k, v in knowledge_base_casos.items():
                queries_corrupcion['$or'].append(fb.generate_regex_query(['message', 'name', 'description'], v,
                    whole_sentence=False, wrapped=True))

            for k, v in knowledge_base_entidades.items():
                query_entidades = fb.generate_regex_query(['message', 'name', 'description'], v,
                        whole_sentence=False, wrapped=True)
                #print("query_knowledge_base_corrupcion =>", query_knowledge_base_corrupcion)
                final_query = {'$and': [queries_corrupcion, query_entidades]}
                #print("final_query =>", final_query)
                posts = fb.query('posts', final_query)
                
                #print("results for", k2, k, "=>", posts)
                #print("--------------------------------")
                for p in pages:
                    page_id = str(p['id'])
                    obj_insert['medios'][page_id][k] = sesgo.sesgo_publicaciones(posts, page_id)

            obj_insert['month'] = now.month
            obj_insert['year'] = now.year
            obj_insert['entity'] = entity
            outliers = sesgo.detect_outliers(obj_insert['medios'])
            # k = case name
            # v = array of summaries (# of posts, outlier or not, page)
            for k, v in outliers.items():
                # v is an array of summaries per page
                for summary in v:
                    #print(summary)
                    #print(summary['page_id'], "=>", k, "=>", obj_insert['medios'][summary['page_id']])
                    obj_insert['medios'][summary['page_id']][k]['outlier'] = summary['outlier']

            #print("obj_insert['medios']", obj_insert['medios'])
            fb.insert('sesgo', obj_insert)
            print("inserted sesgo", entity)
        elif len(res) > 0:
            print(now.year, now.month, "already has sesgo summary")
        now -= relativedelta(months=1)
    
def calcular_sesgo_corrupcion(fb, sesgo, knowledge_base_corrupcion, knowledge_base_casos, entity, config_file, casos_matter=True):
    now = datetime.datetime.now()
    jsonConfig = None
    # TODO: cambiar a config.medios.json
    with open(home + '/workspace/facebook-scraper-py/' + config_file) as data_file:
        jsonConfig = json.load(data_file)
    
    if jsonConfig is not None:
        pages = jsonConfig['pages']
        #print(pages)
        

        # TODO: hacer un summary global (desde enero de 2016, para comparar que tanto hablan los medios de corrupcion/partidos/lideres durante ese periodo de tiempo)
        #while now.year >= 2017 and now.month >= 10:
        #print(now.year, now.month)
        res = fb.query('sesgo', {"entity": entity, "year": now.year, "month": now.month})
        if res is None:
            print("res is None")
        elif len(res) == 0: # No reaction count for that month/year, so create a new summary for that month/year
            obj_insert = {}
            obj_insert['medios'] = {}
            for p in pages:
                page_id = str(p['id'])
                obj_insert['medios'][page_id] = {}
            
            queries_corrupcion = {}
            for k, v in knowledge_base_corrupcion.items():
                queries_corrupcion = fb.generate_regex_query(['message', 'name', 'description'], v,
                    whole_sentence=False, wrapped=True)
            
            if casos_matter:
                for k, v in knowledge_base_casos.items():
                    queries_corrupcion['$or'].append(fb.generate_regex_query(['message', 'name', 'description'], v,
                        whole_sentence=False, wrapped=True))

            final_query = queries_corrupcion
            #print("final_query =>", final_query)
            posts = fb.query('posts', final_query)
            
            #print("results for", k2, k, "=>", posts)
            #print("--------------------------------")
            for p in pages:
                page_id = str(p['id'])
                obj_insert['medios'][page_id]["corrupcion"] = sesgo.sesgo_publicaciones(posts, page_id)

            obj_insert['month'] = now.month
            obj_insert['year'] = now.year
            obj_insert['entity'] = entity
            outliers = sesgo.detect_outliers(obj_insert['medios'])
            # k = case name
            # v = array of summaries (# of posts, outlier or not, page)
            for k, v in outliers.items():
                # v is an array of summaries per page
                for summary in v:
                    #print(summary)
                    #print(summary['page_id'], "=>", k, "=>", obj_insert['medios'][summary['page_id']])
                    obj_insert['medios'][summary['page_id']][k]['outlier'] = summary['outlier']

            #print("obj_insert['medios']", obj_insert['medios'])
            fb.insert('sesgo', obj_insert)
            print("inserted sesgo", entity)
        elif len(res) > 0:
            print(now.year, now.month, "already has sesgo summary")
        now -= relativedelta(months=1)

if __name__ == '__main__':
    fb = Facebook()
    sesgo = Sesgo()
    kb = KnowledgeBase()

    palabras_corrupcion = kb.read_knowledge_base('../base-conocimiento/palabras-corrupcion.txt')
    casos_corrupcion = kb.read_knowledge_base('../base-conocimiento/casos-corrupcion.txt')
    instituciones = kb.read_knowledge_base('../base-conocimiento/instituciones.txt')
    lideres_opinion = kb.read_knowledge_base('../base-conocimiento/lideres-opinion.all.txt')
    partidos_politicos = kb.read_knowledge_base('../base-conocimiento/partidos-politicos.txt')

    calcular_sesgo(fb, sesgo, palabras_corrupcion, "corrupcion", "config.medios.json")
    calcular_sesgo(fb, sesgo, casos_corrupcion, "casos", "config.medios.json")
    calcular_sesgo(fb, sesgo, instituciones, "instituciones", "config.medios.json")
    calcular_sesgo(fb, sesgo, lideres_opinion, "lideres", "config.medios.json")
    calcular_sesgo(fb, sesgo, partidos_politicos, "partidos", "config.medios.json")

    calcular_sesgo_corrupcion_entidades(fb, sesgo, palabras_corrupcion, instituciones, casos_corrupcion, "corrupcion-instituciones", "config.medios.json")
    calcular_sesgo_corrupcion_entidades(fb, sesgo, palabras_corrupcion, lideres_opinion, casos_corrupcion, "corrupcion-lideres", "config.medios.json")
    calcular_sesgo_corrupcion_entidades(fb, sesgo, palabras_corrupcion, partidos_politicos, casos_corrupcion, "corrupcion-partidos", "config.medios.json")

    calcular_sesgo_corrupcion(fb, sesgo, palabras_corrupcion, casos_corrupcion, "lideres-corrupcion", "config.lideres.json")

