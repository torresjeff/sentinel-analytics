home <- Sys.getenv("HOME")
wd <- paste(home, "/r-projects", sep="")
setwd(wd)
getwd()

# DEV TOOLS PACKAGE
# Si sale error, hacer: sudo apt-get update y sudo apt-get -y upgrade
#install.packages("devtools", dependencies = TRUE)
library(devtools)

# QUANTEDA PACKAGE
#library(tm)
# Si no funciona entonces: sudo apt-get install r-cran-xml
#install.packages("XML", dependencies = TRUE)
#install.packages("quanteda")
library(quanteda)

# MONGO PACKAGE
#install_github(repo = "mongosoup/rmongodb")
library(rmongodb)
mongo = mongo.create(host="localhost")
mongo.is.connected(mongo)
mongo.get.databases(mongo)
posts = "facebook.posts"

# STOP WORDS
stop <- readLines("stopwords.txt", encoding = "UTF-8")


#TODO: poner palabras de corrupción en un archivo aparte
jsonStr <- '{"message": {"$regex": "corrup"}}'
bson <- mongo.bson.from.JSON(jsonStr)
all_posts = mongo.find(mongo, "facebook.posts", bson)

# TODO: ver si hay alguna manera con la que no toque iterate sobre todos los posts, esto implica crear otro arreglo y mas RAM
posts <- c()
while (mongo.cursor.next(all_posts)) {
  tmp = mongo.bson.to.list(mongo.cursor.value(all_posts))
  # TODO: toca clean up: quitar signos de puntuacion, stemming?, 
  #tmp$message = gsub("[!\"“”‘’·&/()=?¿¡\'\\@|ºª#~¬{}^*-.,;:/►→]", " ", tmp$message)
  posts <- c(posts, tmp$message) # TODO: falta tmp["name"], en la ultima version del scraper
}
#print(posts)
corp <- corpus(posts)
#dtm <- dfm(corp, remove = stopwords("spanish"), VERBOSE = FALSE)
#dtm
#topfeatures(dtm, 20)
# Keyword in corpus
# Tokens in corpus
tok <- tokens(corp, remove_punct = TRUE, remove_symbols = TRUE, remove_url = TRUE, remove_twitter = TRUE, remove_numbers = TRUE)
#tok <- tokens(corp, remove_punct = TRUE, remove_symbols = TRUE, remove_url = TRUE, ngrams = 2) # N-grams = 2
tok <- removeFeatures(tok, c(stopwords("spanish"), stop)) # TODO: completar stopwords
# TODO: top words de noticias (mensual?) a través del tiempo => tocaría agregar metadatos al corpus de las fechas de las publicaciones
#kwic(tok, "corrup*", windows = 5)

# FEATURE CO-OCURRENCE MATRIX: http://quanteda.io/reference/fcm.html
# myfcm <- fcm(tok, context = "window", window = 10)
# write.csv(myfcm, "fcm.csv")
# as.matrix(myfcm)

mydfm <- dfm(tok)
keywords <- c("corrupción")
associations <- textstat_simil(dfm_weight(mydfm, "relFreq"), keywords, margin = "feature") # Usa correlation method. TODO: revisar el "document" level
associations_cos <- textstat_simil(mydfm, keywords, margin = "feature", method="cosine")
# TODO: promediar cosine y correlation?
# TODO: Se guardaría en la base de datos para que la aplicacion se actualice sola
#as.list(associations, sorted = TRUE, n = 10)
write.csv(associations, file="associations-corrupcion-quanteda.csv")
write.csv(associations_cos, file="associations-corrupcion-cosine-quanteda.csv")

