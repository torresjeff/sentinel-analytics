#!/usr/bin/python3
import sys, os
home = os.environ.get('HOME')
lib_dir = home + '/workspace/analytics/util'
sys.path.append(lib_dir)
from model import Facebook
from knowledge_base import KnowledgeBase
from polarity import type_file_enum
from polarity import process_list as SentimentAnalysis
from optparse import OptionParser
from enum import Enum
import pymongo
import csv
import datetime
from dateutil.relativedelta import relativedelta

client = pymongo.MongoClient("localhost", 27017)
db = client.facebook # use the facebook database (automatically created if it doesn't exist)
posts = db.posts
reactions = db.reactions
comments = db.comments
results = db.results

class Post:
    def __init__(self, post):
        self.post = post
    
    def __eq__(self, other):
        return self.post['_id'] == other.post['_id']
    
    def __hash__(self):
        return hash(self.post['_id'])
    
    def __str__(self):
        return self.post

class Comment:
    def __init__(self, comment):
        self.comment = comment
    
    def __eq__(self, other):
        return self.comment['_id'] == other.comment['_id']
    
    def __eq__(self, other):
        return self.comment['like_count'] > other.comment['like_count']

    def __lt__(self, other):
        return self.comment['like_count'] < other.comment['like_count']
    
    def __hash__(self):
        return hash(self.comment['_id'])

class Reaction:
    def __init__(self, reaction):
        self.reaction = reaction
    
    def __eq__(self, other):
        return self.reaction['_id'] == other.reaction['_id']
    
    def __hash__(self):
        return hash(self.reaction['_id'])

class Options(Enum):
    ALL = 1
    POLARITY = 2
    NO_POLARITY = 3
    STORED = 4
    NOT_STORED = 5
    POLARITY_AND_STORED = 6
    POLARITY_AND_NOT_STORED = 7
    NO_POLARITY_AND_STORED = 8
    NO_POLARITY_AND_NOT_STORED = 8

def get_comments_for(entity, match_exact=False, opts=Options.ALL):
    global comments
    regex = {}
    if match_exact:
        regex = {'$regex': '.*\\b' + entity + '\\b.*'}
    else:
        regex = {'$regex': '.*' + entity + '.*', '$options': 'i'}
    
    comments_for_entity = {}
    if opts == Options.ALL:
        comments_for_entity = comments.find({ '$and': [
            {'message': regex}
        ]})
    elif opts == Options.POLARITY:
        comments_for_entity = comments.find({ '$and': [
            {'message': regex},
            {'polarity': {'$exists': True}}
        ]})
    elif opts == Options.NO_POLARITY:
        comments_for_entity = comments.find({ '$and': [
            {'message': regex},
            {'polarity': {'$exists': False}}
        ]})
    elif opts == Options.STORED:
        comments_for_entity = comments.find({ '$and': [
            {'message': regex},
            {'stored': {'$exists': True}}
        ]})
    elif opts == Options.NOT_STORED:
        comments_for_entity = comments.find({ '$and': [
            {'message': regex},
            {'stored': {'$exists': False}}
        ]})
    elif opts == Options.POLARITY_AND_STORED:
        comments_for_entity = comments.find({ '$and': [
            {'message': regex},
            {'polarity': {'$exists': True}},
            {'stored': {'$exists': True}}
        ]})
    elif opts == Options.POLARITY_AND_NOT_STORED:
        comments_for_entity = comments.find({ '$and': [
            {'message': regex},
            {'polarity': {'$exists': True}},
            {'stored': {'$exists': False}}
        ]})
    elif opts == Options.NO_POLARITY_AND_STORED:
        comments_for_entity = comments.find({ '$and': [
            {'message': regex},
            {'polarity': {'$exists': False}},
            {'stored': {'$exists': True}}
        ]})
    elif opts == Options.NO_POLARITY_AND_NOT_STORED:
        comments_for_entity = comments.find({ '$and': [
            {'message': regex},
            {'polarity': {'$exists': False}},
            {'stored': {'$exists': False}}
        ]})
    
    comments_for_entity = list(comments_for_entity)
    #print("comments_for_entity =>", comments_for_entity)
    comments_for_entity = [Comment(c) for c in comments_for_entity]
    comments_set = set()

    if comments_for_entity:
        comments_set.update(comments_for_entity)

    return comments_set

def get_posts_for(entity, match_exact=False):
    global posts
    regex = {}
    if match_exact:
        regex = {'$regex': '.*\\b' + entity + '\\b.*'}
    else:
        regex = {'$regex': '.*' + entity + '.*', '$options': 'i'}

    posts_for_entity = posts.find({'$or': [
            {'name': regex},
            {'description': regex},
            {'message': regex}
        ]}
    )

    posts_for_entity = list(posts_for_entity)
    posts_for_entity = [Post(p) for p in posts_for_entity]

    posts_set = set()

    if posts_for_entity:
        posts_set.update(posts_for_entity)
    return posts_set

def get_reactions_for(entity, match_exact=False):
    global posts
    global reactions
    posts_set = get_posts_for(entity, match_exact)
    reactions_for_entity = []
    for p in posts_set:
        reactions_for_entity.extend(list(reactions.find({'_id': p.post['_id']})))

    reactions_for_entity = [Reaction(r) for r in reactions_for_entity]

    reactions_set = set()
    # TODO: if it doesn't work then: reactions_for_entity = list(get_reactions_for(key, match_exact)) before if
    if reactions_for_entity:
        reactions_set.update(reactions_for_entity)
    return reactions_set

def update_comments_with_polarity(comments_set):
    for c in comments_set:
        updated_comment = dict(c.comment)
        updated_comment['polarity'] = analyzer.process_text(c.comment['message'])['Polarity']
        #del updated_comment['_id']
        
        print(c.comment['_id'], "=>", updated_comment)
        comments.update(c.comment, updated_comment, upsert=True)

def get_posts_comments_reactions_set(knowledge_base):
    posts_set = set()
    comments_set = set()
    reactions_set = set()
    
    for key, match_exact in knowledge_base.items():
        print("######", key, match_exact, "######")
        posts_for_entity = get_posts_for(key, match_exact)
        comments_for_entity = get_comments_for(key, match_exact)
        reactions_for_entity = list(get_reactions_for(key, match_exact))
        #print(reactions_for_entity)
        #print(posts_for_entity)
        if posts_for_entity:
            posts_set.update(posts_for_entity)
        
        if comments_for_entity:
            comments_set.update(comments_for_entity)
        
        if reactions_for_entity:
            reactions_set.update(reactions_for_entity)
        
    return (posts_set, comments_set, reactions_set)

def write_comments_to_file(comments_set):
    file = '../results/comments/' + name + '-' + datetime.datetime.today().strftime('%Y-%m-%d') + '.csv'
    #comments_set = get_comments_for(name, )
    with open(file, 'w+', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        for c in comments:
            csvwriter.writerow([c.comment['_id'], c.comment['message'], c.comment['like_count'], c.comment['polarity'], c.comment['created_time']])
        
def batch_analyze(fb, knowledge_base, analyzer, collection, attributes=[]):
    now = datetime.datetime.now()
    while now.year >= 2016:
        print(now.year, now.month)
        for name, value in knowledge_base.items():
            res = fb.query('sentiment', {"year": now.year, "month": now.month, "lider": name})
            if res is None:
                print("res is None")
            
            elif len(res) == 0:
                query_lideres = fb.generate_regex_query_for_date(now.year, now.month, ['message'], value,
                        whole_sentence=False, wrapped=True)
                query_lideres['$and'].append({'polarity': {'$exists': False}})
                results = fb.query(collection, query_lideres)
                print("first query results for", name, "=>" , len(results))

                obj_insert = {
                    "year": now.year,
                    "month": now.month,
                    "friendly_name": value['friendly_name'],
                    "type": collection,
                    "entity": "lideres",
                    "lider": name,
                    "negative": 0,
                    "positive": 0,
                    "neutral": 0,
                    "top_comments": [],
                    "like_counts": []
                }
                for r in results:
                    polarity = analyzer.process_text(r['message'])['Polarity']
                    r['polarity'] = polarity

                fb.update_all(collection, results)
                query_lideres['$and'] = query_lideres['$and'][:-1]
                query_lideres['$and'].append({'polarity': {'$exists': True}})
                results = fb.query(collection, query_lideres)

                comments = []

                for r in results:
                    if r['polarity'] < 0: obj_insert['negative'] += 1
                    elif r['polarity'] > 0: obj_insert['positive'] += 1
                    elif r['polarity'] == 0: obj_insert['neutral'] += 1
                    comments.append(Comment(r))

                print("second query results for", name, "=>" , len(results))

                comments.sort(reverse=True)
                for i, c in enumerate(comments):
                    if i <= 4:
                        obj_insert['top_comments'].append(c.comment['message'])
                        obj_insert['like_counts'].append(c.comment['like_count'])
                    else:
                        break
                #print(results)
                obj_insert['total_comentarios'] = obj_insert['negative'] + obj_insert['positive'] + obj_insert['neutral']
                fb.insert('sentiment', obj_insert)
                #print (obj_insert)
            
            elif len(res) > 0:
                print("lider", name, "already has sentiment summary for", now.year, now.month)
        now -= relativedelta(months=1)

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-f", "--file", dest="file", default="lexicons/politico.csv", help="name of the file with the lexicons")
    parser.add_option("-s", "--separator", dest="sep", default="\t", help="specify separator for the file with the lexicons")
    (options, args) = parser.parse_args()

    fb = Facebook()
    kb = KnowledgeBase()
    analyzer = SentimentAnalysis()
    analyzer.load_list(type_file_enum.polarity, options.file, options.sep)

    palabras_corrupcion = kb.read_knowledge_base('../base-conocimiento/palabras-corrupcion.txt')
    #print("Palabras corrupcion", palabras_corrupcion)
    casos_corrupcion = kb.read_knowledge_base('../base-conocimiento/casos-corrupcion.txt')
    #print("Casos corrupcion", casos_corrupcion)
    instituciones = kb.read_knowledge_base('../base-conocimiento/instituciones.txt')
    #print("Instituciones", instituciones)
    lideres_opinion = kb.read_knowledge_base('../base-conocimiento/lideres-opinion.txt')
    #print("Lideres", lideres_opinion)
    partidos_politicos = kb.read_knowledge_base('../base-conocimiento/partidos-politicos.txt')
    #print("Partidos", partidos_politicos)

    batch_analyze(fb, lideres_opinion, analyzer, collection="comments", attributes=['message'])
    
    


    """
    print(analyzer.process_text("Me gusta la nueva ley de ciencia innovación y tecnologia, Pero algo anda mal  ? "))
    print(analyzer.process_text("Así lo afirmó Jaime Velilla Castrillón, representante del Departamento en esta Junta ante las revelaciones de este diario sobre presunta corrupción. Conozca más detalles de su respuesta: A la Junta de Plaza Mayor no le hablaron con la verdad Gobernación de Antioquia"))
    print(analyzer.process_text("Jajajajaja valiente justicia alcahueta, a todos los políticos corruptos les están dando casa por cárcel, que vergüenza. Con razón tantos corruptos, saben que la justicia es laxa entonces llegan a un acuerdo se declaran culpables y les dan una mínima pena en su casa.👎👎👎👎👎"))
    print(analyzer.process_text("Más años de cárcel y menos casa por cárcel para políticos corruptos y ladrones de cuello blanco."))
    print(analyzer.process_text("Álvaro Uribe es el mejor presidente de todos los tiempos."))
    print(analyzer.process_text("Álvaro Uribe es el peor presidente de todos los tiempos."))
    print(analyzer.process_text("Álvaro Uribe es el unico presidente que se atreve a decir la verdad"))
    print(analyzer.process_text("Álvaro Uribe lo unico que sabe decir son mentiras"))
    print(analyzer.process_text("Malditos perros pena de muerte que mas queremos ver Juan Orlando cuando la pena de muerte ya esto se salio de las manos"))
    """
    