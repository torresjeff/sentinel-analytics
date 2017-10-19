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

if __name__ == '__main__':
    fb = Facebook()
    kb = KnowledgeBase()
    counter = Counter()
    now = datetime.datetime.now()
    
    casos_corrupcion = kb.read_knowledge_base('../base-conocimiento/casos-corrupcion.txt')
    
    while now.year >= 2016:
        # TODO: parametrizar "entity"
        res = fb.query('descriptive', {"month": now.month, "year": now.year, "type": "activity_count", "entity": "casos"})
        print(now.year, now.month)
        if res is None:
            print("res is None")
        elif len(res) == 0: # No reaction count for that month/year, so create a new summary for that month/year
            obj_insert = {}
            obj_insert['casos'] = []
            for k, v in casos_corrupcion.items():
                query_casos_corrupcion = fb.generate_regex_query_for_date(now.year, now.month, ['message', 'name', 'description'], v,
                    whole_sentence=False, wrapped=True)
                posts = fb.query('posts', query_casos_corrupcion)
                query_comments = fb.generate_regex_query_for_date(now.year, now.month, ['message'], v,
                    whole_sentence=False, wrapped=True)
                results = counter.get_activity_count(posts)
                results['short_name'] = k
                results['friendly_name'] = v['friendly_name']
                results['post_count'] = len(posts)
                results['comment_count'] = fb.count('comments', query_comments)
                obj_insert['casos'].append(results)

            obj_insert['month'] = now.month
            obj_insert['year'] = now.year
            obj_insert['type'] = "activity_count"
            obj_insert['entity'] = "casos"
            fb.insert('descriptive', obj_insert)
        elif len(res) > 0:
            print(now.year, now.month, "already has activity_count summary")
        now -= relativedelta(months=1)

    # TODO: hacer word cloud de las palabras mas mencionadas en comentarios de noticias de un personaje especifico
    # ej: en las noticias sobre claudia lopez, las palabras que mas se encuentran en los comentarios son "liberal", "verde", etc.
    # TODO: total de likes que tiene la pagina del lider (en caso de que tenga pagina de fb)
    # TODO: total de reacciones que ha recibido en su pagina el lider (todos los posts del lider) - en caso de que tenga página
    # TODO: de cuales temas habla más el lider en su pagina (en caso de que tenga pagina)
    # TODO: grafico de cantidad de posts sobre el personaje que se esta viendo
    # TODO: actividad del lider (cuantas publicaciones ha hecho en su pagina) - en caso de que tenga pagina
    # TODO: mostrar un map(?) de cuales regiones se publican mas sobre corrupcion
    # TODO: mostrar un map(?) de cuales regiones son mas AFECTADAS por corrupcion. Esto sería el grafo, pero buscando municipios/departamentos/pais en vez de cualquier palabra asociada
