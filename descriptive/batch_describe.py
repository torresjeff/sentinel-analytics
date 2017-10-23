#!/usr/bin/python3
import sys, os
lib_dir = os.environ.get('HOME')
lib_dir += '/workspace/analytics/util'
sys.path.append(lib_dir)
from model import Facebook
from knowledge_base import KnowledgeBase
from reaction_count import Counter
import datetime
import pymongo
from dateutil.relativedelta import relativedelta

def activity_count(fb, counter, knowledge_base, entity):
    now = datetime.datetime.now()
    while now.year >= 2016:
        res = fb.query('descriptive', {"month": now.month, "year": now.year, "type": "activity_count", "entity": entity})
        print(now.year, now.month)
        if res is None:
            print("res is None")
        elif len(res) == 0: # No reaction count for that month/year, so create a new summary for that month/year
            obj_insert = {}
            obj_insert[entity] = []
            for k, v in knowledge_base.items():
                query_knowledge_base = fb.generate_regex_query_for_date(now.year, now.month, ['message', 'name', 'description'], v,
                    whole_sentence=False, wrapped=True)
                posts = fb.query('posts', query_knowledge_base)
                query_comments = fb.generate_regex_query_for_date(now.year, now.month, ['message'], v,
                    whole_sentence=False, wrapped=True)
                results = counter.get_activity_count(posts)
                results['short_name'] = k
                results['friendly_name'] = v['friendly_name']
                results['post_count'] = len(posts)
                results['comment_count'] = fb.count('comments', query_comments)
                obj_insert[entity].append(results)

            obj_insert['month'] = now.month
            obj_insert['year'] = now.year
            obj_insert['type'] = "activity_count"
            obj_insert['entity'] = entity
            fb.insert('descriptive', obj_insert)
        elif len(res) > 0:
            print(now.year, now.month, "already has activity_count summary")
        now -= relativedelta(months=1)

def post_count(fb, counter, knowledge_base, entity, page_id):
    now = datetime.datetime.now()
    while now.year >= 2016:
        res = fb.query('descriptive', {"month": now.month, "year": now.year, "type": "post_count", "entity": entity, "page": page_id})
        print(now.year, now.month)
        if res is None:
            print("res is None")
        elif len(res) == 0: # No reaction count for that month/year, so create a new summary for that month/year
            obj_insert = {}
            obj_insert[entity] = []
            for k, v in knowledge_base.items():
                query_knowledge_base = fb.generate_regex_query_for_date(now.year, now.month, ['message', 'name', 'description'], v,
                    whole_sentence=False, wrapped=True)
                query_knowledge_base['$and'].append({"_id": {"$regex": page_id + "_[0-9]+"}})
                #print("query_knowledge_base", query_knowledge_base)
                posts = fb.query('posts', query_knowledge_base)
                # Esto en caso de que se quieran contar los reactions por cada medio
                #results = counter.get_activity_count(posts)
                results = {}
                results['short_name'] = k
                results['friendly_name'] = v['friendly_name']
                results['post_count'] = len(posts)
                obj_insert[entity].append(results)

            obj_insert['month'] = now.month
            obj_insert['year'] = now.year
            obj_insert['type'] = "post_count"
            obj_insert['page'] = page_id
            obj_insert['entity'] = entity
            #print('obj_insert', obj_insert)
            print('inserted summary', now.year, now.month, "for page", page_id, entity)
            fb.insert('descriptive', obj_insert)
        elif len(res) > 0:
            print(now.year, now.month, "already has activity_count summary")
        now -= relativedelta(months=1)

if __name__ == '__main__':
    fb = Facebook()
    kb = KnowledgeBase()
    counter = Counter()
    
    casos_corrupcion = kb.read_knowledge_base('../base-conocimiento/casos-corrupcion.txt')
    lideres_opinion = kb.read_knowledge_base('../base-conocimiento/lideres-opinion.txt')
    
    # TODO: uncomment
    activity_count(fb, counter, casos_corrupcion, "casos")
    activity_count(fb, counter, lideres_opinion, "lideres")

    config = kb.read_config('config.medios.json')

    for p in config['pages']:
        post_count(fb, counter, casos_corrupcion, "casos", str(p['id']))
        #post_count(fb, counter, lideres_opinion, "lideres", str(p['id']))
        #post_count(fb, counter, instituciones, "instituciones", str(p['id']))
    
    # TODO: total de reacciones que ha recibido en su pagina el lider (todos los posts del lider) - en caso de que tenga página
    # TODO: de cuales temas habla más el lider en su pagina (en caso de que tenga pagina)
    # TODO: actividad del lider (cuantas publicaciones ha hecho en su pagina) - en caso de que tenga pagina
    # TODO: mostrar un map(?) de cuales regiones se publican mas sobre corrupcion
