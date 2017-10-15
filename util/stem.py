#!/usr/bin/python3
import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tag import StanfordNERTagger
import unicodedata, re, string
import unidecode
import pymongo
import datetime
from model import Facebook
from knowledge_base import KnowledgeBase

class Stemmer:
    def __init__(self):
        self.stopwords = nltk.corpus.stopwords.words('spanish')
        self.stopwords_no_accents = []
        for w in self.stopwords: self.stopwords_no_accents.append(self.delete_accents(w))
        self.stemmer = SnowballStemmer('spanish')

    #def delete_special_characters(self, lin):
        #lin = re.sub('\/|\\|\\.|\,|\;|\:|\n|\?|\'|\t',' ',lin) # quita los puntos
        #lin = re.sub("\s+\w\s+"," ",lin ) # quita los caractores solos
        #lin = re.sub("\.","",lin)
        #lin = re.sub(" ", "", lin)
        #return lin.lower()
    def delete_special_characters(self, text):
        text = re.sub(r"http\S+", "", text) # Remove links
        text = re.sub(r"\S+\.\S+\/\S*\s", "", text) # Remove links
        pattern = re.compile('[\W_]+', re.UNICODE) # Only keep alphanumeric characters
        text = pattern.sub(' ', text)
        #re.sub('[\W_]+', '', text)
        #print(re.sub(r'\W+', '', text))
        #print(text.lower())
        #return text.lower()
        return text


    def delete_accents(self, text):
        #return ''.join((c for c in unicodedata.normalize('NFD', word) if unicodedata.category(c) != 'Mn'))
        return unidecode.unidecode(text)

    #Elimina los StopWords
    def delete_stopword(self, text):
        return_data=""
        for word in text.split():
            if (word.lower() not in self.stopwords_no_accents) and (word != "") and (len(word) > 2):
                return_data += word.lower() + " "
        return return_data
    
    def delete_numbers(self, text):
        return re.sub('\d+', '', text)
    
    def stem(self, text):
        text = text.lower()
        #text = self.delete_stopword(text)
        #text = self.delete_accents(text)
        words_text = nltk.word_tokenize(text)
        words = []
        for w in words_text:
            words.append(self.stemmer.stem(w))
        
        return ' '.join(words)
    
    def stem_array(self, collection, query):
        results = fb.query(collection, query)
        if results is not None:
            for r in results:
                temp = ''
                #print(r['_id'])
                if 'message' in r:
                    temp += r['message']
                    #print("message =>", r['message'])
                if 'name' in r and collection == 'posts':
                    temp += " " + r['name']
                    #print("name =>", r['name'])
                if 'description' in r and collection == 'posts':
                    temp += " " + r['description']
                    #print("description =>", r['description'])
                
                if temp is not '':
                    r['whole_sentence'] = temp
                    r['whole_sentence'] = self.delete_special_characters(r['whole_sentence'])
                    r['whole_sentence'] = self.delete_accents(r['whole_sentence'])
                    r['whole_sentence'] = self.delete_numbers(r['whole_sentence'])
                    r['whole_sentence'] = self.delete_stopword(r['whole_sentence'])
                    r['stemmed'] = self.stem(r['whole_sentence'])
                    #print(r['_id'])
                    #print(r['whole_sentence'])
                    #print(r['stemmed'])
                    #print("===================")

            fb.update_all(collection, results)

if __name__ == '__main__':
    fb = Facebook()
    kb = KnowledgeBase()
    stemmer = Stemmer()
    text = "Jajajajaja valiente justicia alcahueta, a todos los políticos corruptos les están dando casa por cárcel, que vergüenza. Con razón tantos corruptos, saben que la justicia es laxa entonces llegan a un acuerdo se declaran culpables y les dan una mínima pena en su casa.👎👎👎👎👎 https://stackoverflow.com/questions/1276764/stripping-everything-but-alphanumeric-chars-from-a-string-in-python"
    """
    st = StanfordNERTagger('../base-conocimiento/nlp/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz', #'../base-conocimiento/nlp/stanford-spanish-corenlp-2017-06-09-models.jar',
					   '../base-conocimiento/nlp/stanford-ner/stanford-ner.jar',
					   encoding='utf-8')
    words = nltk.word_tokenize(text)
    classified_text = st.tag(words)
    print(classified_text)
    """
    # Leer base de conocimiento
    palabras_corrupcion = kb.read_knowledge_base('../base-conocimiento/palabras-corrupcion.txt')
    casos_corrupcion = kb.read_knowledge_base('../base-conocimiento/casos-corrupcion.txt')
    instituciones = kb.read_knowledge_base('../base-conocimiento/instituciones.txt')
    lideres_opinion = kb.read_knowledge_base('../base-conocimiento/lideres-opinion.txt')
    partidos_politicos = kb.read_knowledge_base('../base-conocimiento/partidos-politicos.txt')

    # Convertir de dictionary a list con las regular expressions
    palabras_corrupcion = kb.get_words_as_list(palabras_corrupcion)
    casos_corrupcion = kb.get_words_as_list(casos_corrupcion)
    instituciones = kb.get_words_as_list(instituciones)
    lideres_opinion = kb.get_words_as_list(lideres_opinion)
    partidos_politicos = kb.get_words_as_list(partidos_politicos)
    
    # Queries para posts
    posts_queries = []
    posts_queries.append(fb.generate_regex_query(['message', 'name', 'description'], palabras_corrupcion))
    posts_queries.append(fb.generate_regex_query(['message', 'name', 'description'], casos_corrupcion))
    posts_queries.append(fb.generate_regex_query(['message', 'name', 'description'], instituciones))
    posts_queries.append(fb.generate_regex_query(['message', 'name', 'description'], lideres_opinion))
    posts_queries.append(fb.generate_regex_query(['message', 'name', 'description'], partidos_politicos))

    # Queries para comments
    comments_queries = []
    comments_queries.append(fb.generate_regex_query(['message'], palabras_corrupcion))
    comments_queries.append(fb.generate_regex_query(['message'], casos_corrupcion))
    comments_queries.append(fb.generate_regex_query(['message'], instituciones))
    comments_queries.append(fb.generate_regex_query(['message'], lideres_opinion))
    comments_queries.append(fb.generate_regex_query(['message'], partidos_politicos))

    print("Stemming posts...", datetime.datetime.now())
    for q in posts_queries:
        stemmer.stem_array('posts', q)
    print("Finished stemming posts...", datetime.datetime.now())
    
    print("Stemming comments...", datetime.datetime.now())
    for q in comments_queries:
        stemmer.stem_array('comments', q)
    print("Finished stemming comments...", datetime.datetime.now())
    """
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
    """

    #print(palabras_corrupcion)

    

    
    # Stemmer
    
    #stemmer.stem(text)


    """
    print(stemmer.stem("Me gusta la nueva ley de ciencia innovación y tecnologia, Pero algo anda mal  ? "))
    print(stemmer.stem("Así lo afirmó Jaime Velilla Castrillón, representante del Departamento en esta Junta ante las revelaciones de este diario sobre presunta corrupción. Conozca más detalles de su respuesta: A la Junta de Plaza Mayor no le hablaron con la verdad Gobernación de Antioquia"))
    print(stemmer.stem("Jajajajaja valiente justicia alcahueta, a todos los políticos corruptos les están dando casa por cárcel, que vergüenza. Con razón tantos corruptos, saben que la justicia es laxa entonces llegan a un acuerdo se declaran culpables y les dan una mínima pena en su casa.👎👎👎👎👎"))
    print(stemmer.stem("Más años de cárcel y menos casa por cárcel para políticos corruptos y ladrones de cuello blanco."))
    print(stemmer.stem("Álvaro Uribe es el mejor presidente de todos los tiempos."))
    print(stemmer.stem("Álvaro Uribe es el peor presidente de todos los tiempos."))
    print(stemmer.stem("Álvaro Uribe es el unico presidente que se atreve a decir la verdad"))
    print(stemmer.stem("Álvaro Uribe lo unico que sabe decir son mentiras"))
    """
    

