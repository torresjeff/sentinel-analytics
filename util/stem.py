#!/usr/bin/python3
import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tag import StanfordNERTagger
import unicodedata, re, string
import pymongo
from model import Facebook
from knowledge_base import KnowledgeBase

class Stemmer:
    def __init__(self):
        self.stopwords = nltk.corpus.stopwords.words('spanish')
        #print(stopwords)
        #self.stopwords_no_accents = []
        #for w in self.stopwords: self.stopwords_no_accents.append(self.delete_special_characters(self.delete_accents(w)))
        self.stemmer = SnowballStemmer('spanish')

    #def delete_special_characters(self, lin):
        #lin = re.sub('\/|\\|\\.|\,|\;|\:|\n|\?|\'|\t',' ',lin) # quita los puntos
        #lin = re.sub("\s+\w\s+"," ",lin ) # quita los caractores solos
        #lin = re.sub("\.","",lin)
        #lin = re.sub(" ", "", lin)
        #return lin.lower()
    def delete_special_characters(self, text):
        text = re.sub(r"http\S+", "", text) # Remove links
        pattern = re.compile('[\W_]+', re.UNICODE) # Only keep alphanumeric characters
        text = pattern.sub(' ', text)
        #re.sub('[\W_]+', '', text)
        #print(re.sub(r'\W+', '', text))
        #print(text.lower())
        return text.lower()


    def delete_accents(self, word):
        return ''.join((c for c in unicodedata.normalize('NFD', word) if unicodedata.category(c) != 'Mn'))

    #Elimina los StopWords
    def delete_stopword(self, text):
        return_data=[]
        for word in text:
            if (word.lower() not in self.stopwords_no_accents) and (word != "") and (len(word) >2) :
                return_data.append(word.lower())
        return return_data
    
    def stem(self, text):
        words_text = nltk.word_tokenize(text)
        words_text = self.delete_stopword(words_text)
        for w in words_text:
            print(w, "=>", self.stemmer.stem(self.delete_special_characters(self.delete_accents(w))))
            w = self.stemmer.stem(self.delete_special_characters(self.delete_accents(w)))

        return words_text

if __name__ == '__main__':
    fb = Facebook()
    kb = KnowledgeBase()
    stemmer = Stemmer()

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

    #print(palabras_corrupcion)

    results = fb.query('posts', query_posts_palabras)
    if results is not None:
        for r in results:
            temp = ''
            #print(r['_id'])
            if 'message' in r:
                temp += r['message']
                #print("message =>", r['message'])
            if 'name' in r:
                temp += " " + r['name']
                #print("name =>", r['name'])
            if 'description' in r:
                temp += " " + r['description']
                #print("description =>", r['description'])
            
            if temp is not '':
                r['whole_sentence'] = temp
            
        for r in results:
            if 'whole_sentence' in r:
                #print(r['whole_sentence'])
                r['stemmed'] = stemmer.delete_special_characters(r['whole_sentence'])
                #print(r['stemmed'])
                #print("===================")

            

    
    # Stemmer
    
    text = "Jajajajaja valiente justicia alcahueta, a todos los políticos corruptos les están dando casa por cárcel, que vergüenza. Con razón tantos corruptos, saben que la justicia es laxa entonces llegan a un acuerdo se declaran culpables y les dan una mínima pena en su casa.👎👎👎👎👎 https://stackoverflow.com/questions/1276764/stripping-everything-but-alphanumeric-chars-from-a-string-in-python"
    stemmer.delete_special_characters(text)


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
    

