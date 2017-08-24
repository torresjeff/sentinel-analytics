home <- Sys.getenv("HOME")
wd <- paste(home, "/r-projects", sep="")
setwd(wd)
getwd()

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


#TODO: poner palabras de corrupción en un archivo aparte
jsonStr <- '{"message": {"$regex": "corrup"}}'
bson <- mongo.bson.from.JSON(jsonStr)
all_posts = mongo.find(mongo, "facebook.posts", bson)

# TODO: ver si hay alguna manera con la que no toque iterate sobre todos los posts, esto implica crear otro arreglo y mas RAM
posts <- vector()
while (mongo.cursor.next(all_posts)) {
  tmp = mongo.bson.to.list(mongo.cursor.value(all_posts))
  # TODO: toca clean up: quitar signos de puntuacion, stemming?, 
  tmp["message"] <- gsub("[!\"“”‘’·&/()–=?¿¡\'\\@|ºª#~¬{}^*-.,;:/►→]", " ", tmp["message"])
  posts <- c(posts, tmp["message"]) # TODO: falta tmp["name"], en la ultima version del scraper
}

corpus <- VCorpus(VectorSource(posts))
tdm <- DocumentTermMatrix(corpus, control = list(stopwords = stopwords))
                          #control = list(removePunctuation = TRUE)
inspect(tdm)

# ES CASE SENSITIVE, todo está en minusculas
associations <- findAssocs(tdm, c("corrupto"), c(0.0))
print(associations)

associations.df = as.data.frame(do.call(rbind, associations))
write.csv(associations, file="associations-corrupto.csv")

