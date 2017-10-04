home <- Sys.getenv("HOME")
#wd <- paste(home, "/workspace/analytics/word-association", sep="")
wd <- paste(home, "/workspace/analytics/base-conocimiento", sep="")

setwd(wd)
getwd()
#base_conocimiento_dir <- paste(home, "/workspace/analytics/base-conocimiento")
# DEV TOOLS PACKAGE
# Si sale error, hacer: sudo apt-get update y sudo apt-get -y upgrade
#install.packages("devtools", dependencies = TRUE)
library(devtools)

# TEXT MINING PACKAGE
#Si sale error, se debe instalar slam: sudo apt-get install r-cran-slam
# y tambien NLP 
#install.packages("NLP")
#install.packages("slam")
#install.packages("tm", dependencies = TRUE, repos="http://R-Forge.R-project.org")
library(tm)

# MONGO PACKAGE
#install_github(repo = "mongosoup/rmongodb")
library(rmongodb)
mongo = mongo.create(host="localhost")
mongo.is.connected(mongo)
mongo.get.databases(mongo)
posts = "facebook.posts"

# STOP WORDS
stopwords <- readLines("stopwords.txt", encoding = "UTF-8")
# BASE DE CONOCIMIENTO CORRUPCION
palabras_corrupcion <- read.csv(file="palabras-corrupcion.txt", header=FALSE, sep=",", encoding="UTF-8")
palabras_corrupcion[,1]

#reg <- regex_palabras(palabras_corrupcion)
generate_regex <- function (attr, x) {
  reg <- paste('{"',attr,'": {"$regex": ".*', x, '.*"}}', sep="")
  #reg <- paste('{"message": {"$regex": "', x, '"}}', sep="")
  return(reg)
}

palabras_message <- generate_regex("message", palabras_corrupcion[,1])
palabras_name <- generate_regex("name", palabras_corrupcion[,1])
palabras_description <- generate_regex("description", palabras_corrupcion[,1])

palabras <- c()
palabras <- c(rbind(palabras_message, palabras_name, palabras_description))
palabras <- paste(unlist(palabras), collapse=',')
jsonStr <- paste('{"$or": [', palabras, ']}')
bson <- mongo.bson.from.JSON(jsonStr)
Sys.time()
all_posts <- mongo.find(mongo, "facebook.posts", bson)
Sys.time()

# TODO: ver si hay alguna manera con la que no toque iterate sobre todos los posts, esto implica crear otro arreglo y mas RAM
posts <- vector()
while (mongo.cursor.next(all_posts)) {
  tmp = mongo.bson.to.list(mongo.cursor.value(all_posts))
  # TODO: toca clean up: quitar signos de puntuacion, stemming?, 
  tmp["message"] <- gsub("[!\"“”‘’·&/()–=?¿¡\'\\@|ºª#~¬{}^*-.,;:/►→]", " ", tmp["message"])
  tmp["name"] <- gsub("[!\"“”‘’·&/()–=?¿¡\'\\@|ºª#~¬{}^*-.,;:/►→]", " ", tmp["name"])
  tmp["description"] <- gsub("[!\"“”‘’·&/()–=?¿¡\'\\@|ºª#~¬{}^*-.,;:/►→]", " ", tmp["description"])
  tmp["message"] <- paste(tmp["message"], tmp["name"], tmp["description"])
  posts <- c(posts, tmp["message"]) # TODO: falta tmp["name"], en la ultima version del scraper
}
#posts
corpus <- VCorpus(VectorSource(posts))
tdm <- DocumentTermMatrix(corpus, control = list(stopwords = stopwords))
                          #control = list(removePunctuation = TRUE)
inspect(tdm)

# ES CASE SENSITIVE, todo está en minusculas
Sys.time()
associations <- findAssocs(tdm, c("soborno"), c(0.0))
Sys.time()
print(associations)

#associations.df = as.data.frame(do.call(rbind, associations))
#write.csv(associations, file="associations-corrupto.csv")

