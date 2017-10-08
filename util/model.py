#!/usr/bin/python3
import pymongo
from enum import Enum
import csv
import datetime
from knowledge_base import KnowledgeBase

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

class Facebook:
    def __init__(self, host="localhost", port=27017):
        self.client = pymongo.MongoClient(host, port)
        print("Successfully connected to mongo")
        self.db = self.client.facebook # use the facebook database (automatically created if it doesn't exist)
        self.posts = self.db.posts
        self.reactions = self.db.reactions
        self.comments = self.db.comments
        self.results = self.db.results
    
    def get_comments_for(self, entity, match_exact=False, opts=Options.ALL):
        regex = {}
        if match_exact:
            regex = {'$regex': '.*\\b' + entity + '\\b.*'}
        else:
            regex = {'$regex': '.*' + entity + '.*', '$options': 'i'}
        
        comments_for_entity = {}
        if opts == Options.ALL:
            comments_for_entity = self.comments.find({ '$and': [
                {'message': regex}
            ]})
        elif opts == Options.POLARITY:
            comments_for_entity = self.comments.find({ '$and': [
                {'message': regex},
                {'polarity': {'$exists': True}}
            ]})
        elif opts == Options.NO_POLARITY:
            comments_for_entity = self.comments.find({ '$and': [
                {'message': regex},
                {'polarity': {'$exists': False}}
            ]})
        elif opts == Options.STORED:
            comments_for_entity = self.comments.find({ '$and': [
                {'message': regex},
                {'stored': {'$exists': True}}
            ]})
        elif opts == Options.NOT_STORED:
            comments_for_entity = self.comments.find({ '$and': [
                {'message': regex},
                {'stored': {'$exists': False}}
            ]})
        elif opts == Options.POLARITY_AND_STORED:
            comments_for_entity = self.comments.find({ '$and': [
                {'message': regex},
                {'polarity': {'$exists': True}},
                {'stored': {'$exists': True}}
            ]})
        elif opts == Options.POLARITY_AND_NOT_STORED:
            comments_for_entity = self.comments.find({ '$and': [
                {'message': regex},
                {'polarity': {'$exists': True}},
                {'stored': {'$exists': False}}
            ]})
        elif opts == Options.NO_POLARITY_AND_STORED:
            comments_for_entity = self.comments.find({ '$and': [
                {'message': regex},
                {'polarity': {'$exists': False}},
                {'stored': {'$exists': True}}
            ]})
        elif opts == Options.NO_POLARITY_AND_NOT_STORED:
            comments_for_entity = self.comments.find({ '$and': [
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
    
    def get_posts_for(self, entity, match_exact=False):
        regex = {}
        if match_exact:
            regex = {'$regex': '.*\\b' + entity + '\\b.*'}
        else:
            regex = {'$regex': '.*' + entity + '.*', '$options': 'i'}

        posts_for_entity = self.posts.find({'$or': [
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
    
    def generate_regex_query(self, attr=[], values=[]):
        query = {'$or': []}
        for a in attr:
            for v in values:
                query['$or'].append({a: {"$regex": ".*" + v + ".*", '$options': 'i'}})
        return query
    
    def query(self, collection, query):
        if collection == 'posts':
            return list(self.posts.find(query))
        elif collection == 'comments':
            return list(self.comments.find(query))
        elif collection == 'reactions':
            return list(self.reactions.find(query))
        elif collection == 'results':
            return list(self.results.find(query))
        else:
            return None

if __name__ == '__main__':
    fb = Facebook()
    kb = KnowledgeBase()    
    #comments = fb.get_comments_for("Álvaro Uribe")
    #posts = fb.get_posts_for("Álvaro Uribe")
    #print(posts)



    palabras_corrupcion = kb.read_knowledge_base('../base-conocimiento/palabras-corrupcion.txt')
    #print("Palabras corrupcion", palabras_corrupcion)
    casos_corrupcion = kb.read_knowledge_base('../base-conocimiento/casos-corrupcion.txt')
    #print("Casos corrupcion", casos_corrupcion)
    instituciones = kb.read_knowledge_base('../base-conocimiento/instituciones.txt')
    #print("Instituciones", instituciones)
    lideres_opinion = kb.read_knowledge_base('../base-conocimiento/lideres-opinion.txt')
    #print("Lideres", lideres_opinion)
    partidos_politicos = kb.read_knowledge_base('../base-conocimiento/partidos-politicos.txt')

    palabras_corrupcion = kb.get_words_as_list(palabras_corrupcion)
    casos_corrupcion = kb.get_words_as_list(casos_corrupcion)
    instituciones = kb.get_words_as_list(instituciones)
    lideres_opinion = kb.get_words_as_list(lideres_opinion)
    partidos_politicos = kb.get_words_as_list(partidos_politicos)
        
    # Queries para posts
    query_posts_palabras = fb.generate_regex_query(['message', 'name', 'description'], palabras_corrupcion)
    query_posts_casos = fb.generate_regex_query(['message', 'name', 'description'], casos_corrupcion)
    query_posts_instituciones = fb.generate_regex_query(['message', 'name', 'description'], instituciones)
    query_posts_lideres = fb.generate_regex_query(['message', 'name', 'description'], lideres_opinion)
    query_posts_partidos = fb.generate_regex_query(['message', 'name', 'description'], partidos_politicos)

    # Queries para comments
    query_comments_palabras = fb.generate_regex_query(['message'], palabras_corrupcion)
    query_comments_casos = fb.generate_regex_query(['message'], casos_corrupcion)
    query_comments_instituciones = fb.generate_regex_query(['message'], instituciones)
    query_comments_lideres = fb.generate_regex_query(['message'], lideres_opinion)
    query_comments_partidos = fb.generate_regex_query(['message'], partidos_politicos)


    
    res = fb.query('posts', query_posts_palabras)

    print(res)

    #fb.generate_regex()