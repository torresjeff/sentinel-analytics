#!/usr/bin/python3
import sys
import nltk, nltk.metrics
import numpy,math,unicodedata, re
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import csv
from enum import Enum



class type_file_enum(Enum):
    polarity = 1
    other = 2

class process_list:
    def __init__(self, debug = False):
        # LIST person_type
        self._polarity = []
        self._other = []
        # StopWord
        self._stopwords = nltk.corpus.stopwords.words('spanish')
        self._stopwords_no_accents = []
        for w in self._stopwords: self._stopwords_no_accents.append(self.delete_special_characters(self.delete_accents(w)))
        # Stemmer
        self._spanis_stemmer = SnowballStemmer('spanish')
        #Debug Print Message
        self.debug = debug

    def load_list(self, _file_type, type_file_parm):

        if (type_file_parm is type_file_enum.polarity):
            with open(_file_type, newline='') as csvFileBow:
                reader = csv.reader(csvFileBow, delimiter=';')
                for row in reader:
                    new_row = [row[0], self.delete_accents(row[0]), self.delete_special_characters(self.delete_accents(row[0])),
                         self._spanis_stemmer.stem(self.delete_accents(self.delete_accents(row[0]))), row[1]]
                    self._polarity.append(new_row)
                    #print(new_row)
                print("Summary Lexicon: ",_file_type," #Words: ", len(self._polarity))


        if (type_file_parm is type_file_enum.other):
            with open(_file_type, newline='') as csvFileBow:
                reader = csv.reader(csvFileBow, delimiter=';')
                for row in reader:
                    new_row = [row[0], self.delete_accents(row[0]),
                               self.delete_special_characters(self.delete_accents(row[0])),
                               self._spanis_stemmer.stem(self.delete_accents(self.delete_accents(row[0]))),
                               row[1]+"-"+row[2]+"-"+row[3]]
                    self._other.append(new_row)
                    #print(new_row)

    def filter_word(self, word, type_file_parm):
        debug = True
        if (type_file_parm is type_file_enum.polarity):
            original = word
            matching = [[original, s[0]] for s in self._polarity if word == s[0]]
            if debug: print("1.Characters ", original, "-", word, " - ", matching)
            if (len(matching) == 0):
                word = self.delete_accents(word)
                matching = [[original, s[1]] for s in self._polarity if word == s[1]]
                if debug: print("2.Characters ", original, "-", word, " - ", matching)
                if (len(matching) == 0):
                    word = self.delete_special_characters(self.delete_accents(word))
                    matching = [[original, s[2]] for s in self._polarity if word == s[2]]
                    if debug: print("3.Characters ", original, "-", word, " - ", matching)
                    if (len(matching) == 0):
                        word = self._spanis_stemmer.stem(self.delete_special_characters(self.delete_accents(word)))
                        matching = [[original, s[3]] for s in self._polarity if word == s[3]]
                        if debug: print("4.Characters ", original, "-", word, " - ", matching)
                        if (len(matching) == 0):
                            return "No identificado",0
                        else:
                            return "No personal",matching
                    else:
                        return "No personal",matching
                else:
                    return "No personal",matching
            else:
                return "No personal",matching
        return "No identificado",0


    def process_text(self, text):

        result_words = []
        result_polarity = None
        polarity_word = None
        polarity_value = 0
        polarity_average = 0
        polarity_label = ""
        counter = 0
        neg = 0
        pos = 0
        value = 0

        try:
            words_text = nltk.word_tokenize(text)
            words_text = self.delete_stopword(words_text)

            for word in words_text:
                polarity_word = self.filter_word_generic(word, type_file_enum.polarity)
                #print(polarity_word)
                if polarity_word[1] != 0:
                    counter = counter + 1
                    if int(polarity_word[1][0][2]) < 0:
                        neg = neg - 1
                    elif int(polarity_word[1][0][2]) > 0:
                        pos = pos + 1
                    result_words.append(polarity_word)
                    if self.debug: print(polarity_word)

            if abs(neg) > pos:
                value = neg
            else:
                value = pos

            if counter != 0:
                polarity_average = value / counter
            else:
                polarity_average = 0

            polarity_value = round(polarity_average)

            if polarity_value == 1:
                polarity_label = "Positivo"
            elif polarity_value == -1:
                polarity_label = "Negativo"
            else:
                polarity_label = "Neutro"
        except:
            print("Error - polarity : ", polarity_word)

        result_polarity = {'Polarity': polarity_value, 'Average': polarity_average,'Label': polarity_label,'Words':result_words}
        return result_polarity

    def filter_word_generic(self, word, type_file_parm):

        if (type_file_parm is type_file_enum.polarity):
           return self.internal_count_list(word,self._polarity, {"error":"No identificado", "successful":"polarity"} )
        if (type_file_parm is type_file_enum.occupation):
            return self.internal_count_list(word, self._other,{"error": "No identificado", "successful": "other"})
        return "ERROR 0001 - LIST - NOT FOUND",0

    def internal_count_list(self, word, list_porcess, response_text):
        original = word
        matching = [[original, s[0], s[4]] for s in list_porcess if word == s[0]]
        if self.debug: print("-----------------------------------")
        if self.debug: print("1.Characters ", original, "-", word, " - ", matching)
        if (len(matching) == 0):
            word = self.delete_accents(word)
            matching = [[original, s[1], s[4]] for s in list_porcess if word == s[1]]
            if self.debug: print("2.Characters ", original, "-", word, " - ", matching)
            if (len(matching) == 0):
                word = self.delete_special_characters(self.delete_accents(word))
                matching = [[original, s[2], s[4]] for s in list_porcess if word == s[2]]
                if self.debug: print("3.Characters ", original, "-", word, " - ", matching)
                if (len(matching) == 0):
                    word = self._spanis_stemmer.stem(self.delete_special_characters(self.delete_accents(word)))
                    matching = [[original, s[3], s[4]] for s in list_porcess if word == s[3]]
                    if self.debug: print("4.Characters ", original, "-", word, " - ", matching)
                    if (len(matching) == 0):
                        return response_text["error"], 0
                    else:
                        return response_text["successful"], matching
                else:
                    return response_text["successful"], matching
            else:
                return response_text["successful"], matching
        else:
            return response_text["successful"], matching

    #Eliminar las Tildes
    def delete_accents(self,_word):
        return ''.join((c for c in unicodedata.normalize('NFD', _word) if unicodedata.category(c) != 'Mn'))

    #Elimina Caracteres Especiales
    def delete_special_characters(self, lin):
        lin = re.sub('\/|\\|\\.|\,|\;|\:|\n|\?|\'|\t',' ',lin) # quita los puntos
        lin = re.sub("\s+\w\s+"," ",lin ) # quita los caractores solos
        lin = re.sub("\.","",lin)
        lin = re.sub(" ", "", lin)
        return lin.lower()

    #Elimina los StopWords
    def delete_stopword(self, text):
        return_data=[]
        for word in text:
            if (word.lower() not in self._stopwords_no_accents) and (word != "") and (len(word) >2) :
                return_data.append(word.lower())
        return return_data



obj_pol_user = process_list()
obj_pol_user.load_list("lexicons/CSL_politico.csv",type_file_enum.polarity)

#FORMA 1
#print(obj_dem_user.filter_word("Bueno",type_file_enum.person_type))
#print(obj_dem_user.filter_word("Malo",type_file_enum.person_type))

#FORMA 2
#print(obj_dem_user.filter_word_generic("Bueno",type_file_enum.polarity))
#print(obj_dem_user.filter_word_generic("Malo",type_file_enum.polarity))

#Texto
print(obj_pol_user.process_text("Me gusta la nueva ley de ciencia innovación y tecnologia, Pero algo anda mal  ? "))
print(obj_pol_user.process_text("Así lo afirmó Jaime Velilla Castrillón, representante del Departamento en esta Junta ante las revelaciones de este diario sobre presunta corrupción. Conozca más detalles de su respuesta: A la Junta de Plaza Mayor no le hablaron con la verdad Gobernación de Antioquia"))
print(obj_pol_user.process_text("Jajajajaja valiente justicia alcahueta, a todos los políticos corruptos les están dando casa por cárcel, que vergüenza. Con razón tantos corruptos, saben que la justicia es laxa entonces llegan a un acuerdo se declaran culpables y les dan una mínima pena en su casa.👎👎👎👎👎"))
print(obj_pol_user.process_text("Más años de cárcel y menos casa por cárcel para políticos corruptos y ladrones de cuello blanco."))



