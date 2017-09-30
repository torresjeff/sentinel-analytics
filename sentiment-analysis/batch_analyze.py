#!/usr/bin/python3

from polarity import type_file_enum
from polarity import process_list as SentimentAnalysis
from optparse import OptionParser
import pymongo
import csv

client = pymongo.MongoClient("localhost", 27017)
db = client.facebook # use the facebook database (automatically created if it doesn't exist)
pages = db.pages
posts = db.posts
reactions = db.reactions
comments = db.comments


def read_knowledge_base(file):
    words = []
    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            words += row
            #new_row = [row[0], self.delete_accents(row[0]), self.delete_special_characters(self.delete_accents(row[0])),
                    #self._spanis_stemmer.stem(self.delete_accents(self.delete_accents(row[0]))), row[1]]
            #self._polarity.append(new_row)
    return words
    

def get_comments_for(entity, cases_matter=False):
    global comments
    regex = {}
    if not cases_matter:
        regex = {'$regex': '.*' + entity + '.*', '$options': 'i'}
    else:
        regex = {'$regex': '.*' + entity + '.*'}
    comments_for_entity = comments.find({'message': regex})
    return comments_for_entity

def get_posts_for(entity, cases_matter=False):
    global posts
    regex = {}
    if not cases_matter:
        regex = {'$regex': '.*' + entity + '.*', '$options': 'i'}
    else:
        regex = {'$regex': '.*' + entity + '.*'}

    posts_for_entity = posts.find({ '$or': [
        {'name': regex},
        {'description': regex},
        {'message': regex}
    ]})
    return posts_for_entity

def get_reactions_for(entity, cases_matter=False):
    global posts
    global reactions
    post = get_posts_for(entity, cases_matter)
    reactions_for_entity = []
    for p in post:
        reactions_for_entity += reactions.find({'_id': p['_id']})
    return reactions_for_entity

if __name__ == '__main__':
    palabras_corrupcion = read_knowledge_base('../base-conocimiento/palabras-corrupcion.txt')
    casos_corrupcion = read_knowledge_base('../base-conocimiento/casos-corrupcion.txt')
    instituciones = read_knowledge_base('../base-conocimiento/instituciones.txt')
    lideres_opinion = read_knowledge_base('../base-conocimiento/lideres-opinion.txt')
    partidos_politicos = read_knowledge_base('../base-conocimiento/partidos-politicos.txt')

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

    #print(analyzer.process_text("Me gusta la nueva ley de ciencia innovación y tecnologia, Pero algo anda mal  ? "))
    #print(analyzer.process_text("Así lo afirmó Jaime Velilla Castrillón, representante del Departamento en esta Junta ante las revelaciones de este diario sobre presunta corrupción. Conozca más detalles de su respuesta: A la Junta de Plaza Mayor no le hablaron con la verdad Gobernación de Antioquia"))
    #print(analyzer.process_text("Jajajajaja valiente justicia alcahueta, a todos los políticos corruptos les están dando casa por cárcel, que vergüenza. Con razón tantos corruptos, saben que la justicia es laxa entonces llegan a un acuerdo se declaran culpables y les dan una mínima pena en su casa.👎👎👎👎👎"))
    #print(analyzer.process_text("Más años de cárcel y menos casa por cárcel para políticos corruptos y ladrones de cuello blanco."))
    #print(analyzer.process_text("Álvaro Uribe es el mejor presidente de todos los tiempos."))
    #print(analyzer.process_text("Álvaro Uribe es el peor presidente de todos los tiempos."))
    #print(analyzer.process_text("Álvaro Uribe es el unico presidente que se atreve a decir la verdad"))
    #print(analyzer.process_text("Álvaro Uribe lo unico que sabe decir son mentiras"))
    #print(analyzer.process_text("Malditos perros pena de muerte que mas queremos ver Juan Orlando cuando la pena de muerte ya esto se salio de las manos"))

    for lider in instituciones:
        print("######", lider, "######")
        posts_for_entity = get_posts_for(lider)
        reactions_for_entity = get_reactions_for(lider)

        for p in posts_for_entity[0:10]:
            print(p)
        
        for r in reactions_for_entity[0:10]:
            print(r)
    

    # TODO: leer entidades de un archivo y no con un string como se esta haciendo ahora
    #comments = get_comments_for("álvaro Uribe")
    #for c in comments:
        #print(c['message'], "=>", analyzer.process_text(c['message'])['Label'])

    #print(comments.count())
    #print(comments[0])