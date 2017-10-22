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
        # TODO: parametrizar "entity"
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


if __name__ == '__main__':
    fb = Facebook()
    kb = KnowledgeBase()
    counter = Counter()
    
    casos_corrupcion = kb.read_knowledge_base('../base-conocimiento/casos-corrupcion.txt')
    lideres_opinion = kb.read_knowledge_base('../base-conocimiento/lideres-opinion.txt')
    
    activity_count(fb, counter, casos_corrupcion, "casos")
    activity_count(fb, counter, lideres_opinion, "lideres")

    # TODO: hacer word cloud de las palabras mas mencionadas en comentarios de noticias de un personaje especifico
    # ej: en las noticias sobre claudia lopez, las palabras que mas se encuentran en los comentarios son "liberal", "verde", etc.
    # TODO: total de likes que tiene la pagina del lider (en caso de que tenga pagina de fb)
    # TODO: total de reacciones que ha recibido en su pagina el lider (todos los posts del lider) - en caso de que tenga página
    # TODO: de cuales temas habla más el lider en su pagina (en caso de que tenga pagina)
    # TODO: grafico de cantidad de posts sobre el personaje que se esta viendo
    # TODO: actividad del lider (cuantas publicaciones ha hecho en su pagina) - en caso de que tenga pagina
    # TODO: mostrar un map(?) de cuales regiones se publican mas sobre corrupcion
