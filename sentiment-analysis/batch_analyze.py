#!/usr/bin/python3

from polarity import type_file_enum
from polarity import process_list as SentimentAnalysis
from optparse import OptionParser
import pymongo
import csv
import datetime

client = pymongo.MongoClient("localhost", 27017)
db = client.facebook # use the facebook database (automatically created if it doesn't exist)
pages = db.pages
posts = db.posts
reactions = db.reactions
comments = db.comments

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
    
    def __hash__(self):
        return hash(self.comment['_id'])

class Reaction:
    def __init__(self, reaction):
        self.reaction = reaction
    
    def __eq__(self, other):
        return self.reaction['_id'] == other.reaction['_id']
    
    def __hash__(self):
        return hash(self.reaction['_id'])
    

def read_knowledge_base(file):
    words = []
    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        words = {}
        for row in reader:
            words[row[0]] = True if row[1] == 'true' else False
            #words += row[0]
            #new_row = [row[0], self.delete_accents(row[0]), self.delete_special_characters(self.delete_accents(row[0])),
                    #self._spanis_stemmer.stem(self.delete_accents(self.delete_accents(row[0]))), row[1]]
            #self._polarity.append(new_row)
    #print(words)
    return words
    

def get_comments_for(entity, match_exact=False, with_polarity=False):
    global comments
    regex = {}
    if match_exact:
        regex = {'$regex': '.*\\b' + entity + '\\b.*'}
    else:
        regex = {'$regex': '.*' + entity + '.*', '$options': 'i'}
    
    comments_for_entity = {}

    if with_polarity:
        comments_for_entity = comments.find({ '$and': [
            {'message': regex},
            {'polarity': {'$exists': True}}
        ]})
    else:
        comments_for_entity = comments.find({ '$and': [
            {'message': regex},
            {'polarity': {'$exists': False}}
        ]})

    comments_for_entity = list(comments_for_entity)
    comments_for_entity = [Comment(c) for c in comments_for_entity]
    return comments_for_entity

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
    return posts_for_entity

def get_reactions_for(entity, match_exact=False):
    global posts
    global reactions
    posts_for_entity = get_posts_for(entity, match_exact)
    reactions_for_entity = []
    for p in posts_for_entity:
        reactions_for_entity.extend(list(reactions.find({'_id': p.post['_id']})))

    reactions_for_entity = [Reaction(r) for r in reactions_for_entity]
    return reactions_for_entity

def update_comments_with_polarity(comments_set):
    for c in comments_set:
        updated_comment = dict(c.comment)
        updated_comment['polarity'] = analyzer.process_text(c.comment['message'])['Polarity']
        del updated_comment['_id']
        
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

def write_comments_to_file(name):
    file = '../results/comments/' + name + '-' + datetime.datetime.today().strftime('%Y-%m-%d') + '.csv'
    #comments_set = get_comments_for(name, )
    with open(file, 'w+', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        for c in comments:
            csvwriter.writerow([c.comment['_id'], c.comment['message'], c.comment['like_count'], c.comment['polarity'], c.comment['created_time']])

if __name__ == '__main__':

    #print("Palabras corrupcion", palabras_corrupcion)
    #print("Casos corrupcion", casos_corrupcion)
    #print("Instituciones", instituciones)
    #print("Lideres opinion", lideres_opinion)
    #print("Partidos politicos", partidos_politicos)

    parser = OptionParser()
    parser.add_option("-f", "--file", dest="file", default="lexicons/politico.csv", help="name of the file with the lexicons")
    parser.add_option("-s", "--separator", dest="sep", default="\t", help="specify separator for the file with the lexicons")
    (options, args) = parser.parse_args()

    analyzer = SentimentAnalysis()
    analyzer.load_list(type_file_enum.polarity, options.file, options.sep)

    palabras_corrupcion = read_knowledge_base('../base-conocimiento/palabras-corrupcion.txt')
    casos_corrupcion = read_knowledge_base('../base-conocimiento/casos-corrupcion.txt')
    instituciones = read_knowledge_base('../base-conocimiento/instituciones.txt')
    lideres_opinion = read_knowledge_base('../base-conocimiento/lideres-opinion.txt')
    partidos_politicos = read_knowledge_base('../base-conocimiento/partidos-politicos.txt')

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
    
    (posts_set, comments_set, reactions_set) = get_posts_comments_reactions_set(lideres_opinion)

    update_comments_with_polarity(comments_set)
    
    write_comments_to_file("claudia-lopez")
    
        
        #for p in posts_corrupcion:
            #print(p.post)
        
        #for c in comments_corrupcion:
            #print(c.comment)
        
        #for r in reactions_corrupcion:
            #print(r.reaction)

        #print(c['message'], "=>", analyzer.process_text(c['message'])['Label'])
    

    # TODO: leer entidades de un archivo y no con un string como se esta haciendo ahora
    #comments = get_comments_for("álvaro Uribe")
    #

    #print(comments.count())
    #print(comments[0])