home <- Sys.getenv("HOME")
wd <- paste(home, "/workspace/analytics/base-conocimiento", sep="")

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

# STOP WORDS
stopwords <- readLines("stopwords.txt", encoding = "UTF-8")
# BASE DE CONOCIMIENTO CORRUPCION
palabras_corrupcion_assoc <- read.csv(file="palabras-corrupcion-assoc.txt", header=TRUE, sep=",", encoding="UTF-8")
palabras_corrupcion_assoc[,1]

#TODO: buscar posts de corrupcion POR cada medio, para saber cuales son las palabras mas mencionadas en conjunto con corrupcion para cada medio
generate_regex <- function (attr, x) {
  reg <- paste('{"',attr,'": {"$regex": ".*', x, '.*"}}', sep="")
  #reg <- paste('{"message": {"$regex": "', x, '"}}', sep="")
  return(reg)
}

queries <- c()

for (i in 1:length(palabras_corrupcion_assoc[,1])) {
  # Si no tiene stopwords buscar en el atributo "whole_sentence"
  if (as.character(palabras_corrupcion_assoc[i,2]) == "true") {
    palabras_whole <- generate_regex("whole_sentence", palabras_corrupcion_assoc[i,1])
    queries <- c(queries, paste(unlist(palabras_whole), collapse=','))
  } else {
    palabras_message <- generate_regex("message", palabras_corrupcion_assoc[i,1])
    palabras_name <- generate_regex("name", palabras_corrupcion_assoc[i,1])
    palabras_description <- generate_regex("description", palabras_corrupcion_assoc[i,1])
    queries <- c( queries, paste(unlist(c(rbind(palabras_message, palabras_name, palabras_description))), collapse=',') )
  }
}

print(queries)

years <- c(2016, 2017)
months <- c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
#years <- c(2017)
#months <- c(9, 10)
today <- as.POSIXct(Sys.Date())


# jsonStr <- paste('{ "$and": [{"$or": [{"whole_sentence": {"$regex": ".*soborno.*"}}]}, {"month": ', 9, ', "year": ', 2017, '}] }', sep="")
# bson <- mongo.bson.from.JSON(jsonStr)
# psts <- mongo.find(mongo, paste("facebook.", "posts", sep=""), bson)
# month_posts <- vector()
# while (mongo.cursor.next(psts)) {
#   tmp = mongo.bson.to.list(mongo.cursor.value(psts))
#   if (!(is.null(tmp))) {
#     month_posts <- c(month_posts, tmp["whole_sentence"])
#   }
# }
# month_posts <- c(month_posts, "")
# corpus <- VCorpus(VectorSource(month_posts))
# # Create DTM
# tdm <- DocumentTermMatrix(corpus, control = list(stopwords = stopwords, weighthing=weightTfIdf))
# #inspect(tdm)
# associations <- findAssocs(tdm, as.character("soborno"), c(0.0))
# print(associations)
#   
# print(queries)
# print(month_posts)

generate_assocs_summary <- function (type, keywords, pretty_name, queries, colors, no_accents) {
  for (y in years) {
    for (m in months) {
      print(paste(y, m))
      total_palabras_assoc <- list()
      for (i in 1:length(keywords)) {
        # TODO: adjust size de keywords de corrupcion
        total_palabras_assoc[[as.character(keywords[i])]] <- list(id=paste("n", i, sep=""), size=15, label=as.character(pretty_name[i]), color=as.character(colors[i]))
      }
      #print(total_palabras_assoc)
      current_id <- length(keywords) + 1
      
      if ( (y == as.integer(format(today, "%Y")) && m <= as.integer(format(today, "%m"))) || y < as.integer(format(today, "%Y")) ) {
        
        # Query current month an year (the ones in for loop)
        jsonStr <- paste('{"month": ', m, ', "year": ', y, ', "type": "', type, '"}', sep="")
        bson <- mongo.bson.from.JSON(jsonStr)
        tmp <- mongo.find.one(mongo, "facebook.assocs", bson)
        
        # If no results then create new association summary for that month-year
        if (is.null(tmp)) {
          all_assocs <- c()
          for (q in 1:length(queries)) {
            jsonStr <- paste('{ "$and": [{"$or": [', queries[q], ']}, {"month": ', m, ', "year": ', y, '}] }', sep="")
            #print(jsonStr)
            bson <- mongo.bson.from.JSON(jsonStr)
            psts <- mongo.find(mongo, paste("facebook.", type, sep=""), bson)
            month_posts <- vector()
            while (mongo.cursor.next(psts)) {
              tmp = mongo.bson.to.list(mongo.cursor.value(psts))
              if (!(is.null(tmp))) {
                month_posts <- c(month_posts, tmp["whole_sentence"])
              }
            }
            month_posts <- c(month_posts, "")
            #print(month_posts)
            
            # We will store all our calculated associations for the current month (m) and year (y) here
            
            # If we have posts for that month-year, then calculate the associations
            if (length(month_posts) > 0) {
              # Create corpus
              corpus <- VCorpus(VectorSource(month_posts))
              # Create DTM
              tdm <- DocumentTermMatrix(corpus, control = list(stopwords=stopwords, weighthing=weightTfIdf))
              # For each word in the knowledge base (palabras de corrupcion), find the associations of that word in particular
              
              
              #associations <- findAssocs(tdm, as.character(keywords[q]), c(0.0))
              #print(strsplit(as.character(pretty_name[q]), " "))
              words <- unique(strsplit(as.character(no_accents[q]), "\\s")[[1]])
              associations <- findAssocs(tdm, words, c(0.0))
              #print(associations)
              all_assocs <- c(all_assocs, associations)
              # If it did find any associations then store the size of the node and the id
              if (length(names(associations[[as.character(keywords[q])]])) >= 5) {# && !(names(associations[[as.character(palabras_corrupcion_assoc[i,1])]][1:5]) %in% total_palabras_assoc)) {
                # Only look for the 5 highest associations
                for (j in 1:5) {
                  #print(names(associations[[as.character(palabras_corrupcion_assoc[i,1])]])[j])
                  #print(associations[[as.character(palabras_corrupcion_assoc[i,1])]][j])
                  
                  # If one of the words found in the association was already found before, then simply update the size of the node instead of adding a new one
                  if (names(associations[[as.character(keywords[q])]])[j] %in% total_palabras_assoc && !(is.na(names(associations[[as.character(keywords[q])]])[j]))) {
                    #print("Found an already existing word")
                    temporary_obj <- total_palabras_assoc[[names(associations[[as.character(keywords[q])]])[j]]] 
                    total_palabras_assoc[[names(associations[[as.character(keywords[q])]])[j]]] <- list(id=temporary_obj$id, size=temporary_obj$size + associations[[as.character(keywords[q])]][j]*20, label=temporary_obj$label, color=temporary_obj$color)
                    
                  } else if (!is.na(names(associations[[as.character(keywords[q])]])[j])) { # Else, it's a new word (new node)
                    #print("Adding new word")
                    total_palabras_assoc[[names(associations[[as.character(keywords[q])]])[j]]] <- list(id=paste("n", current_id, sep=""), size=associations[[as.character(keywords[q])]][j]*20, label=names(associations[[as.character(keywords[q])]])[j])
                    current_id <- current_id + 1
                  }
                }
              }
            } # if length(month_posts) > 0
            
          } # For queries
              
          edges <- list()
          # Generate edges between word
          for (i in 1:length(keywords)) {
            if (length(names(all_assocs[[as.character(keywords[i])]])) >= 5) {
              for (j in 1:5) {
                #print(names(all_assocs[[as.character(palabras_corrupcion_assoc[i,1])]])[j])
                #print(all_assocs[[as.character(palabras_corrupcion_assoc[i,1])]])
                if (length(names(all_assocs[[as.character(keywords[i])]])[j]) > 0) {
                  source_obj <- total_palabras_assoc[[as.character(keywords[i])]]
                  target_obj <- total_palabras_assoc[[names(all_assocs[[as.character(keywords[i])]])[j]]] 
                  total_palabras_assoc[[names(all_assocs[[as.character(keywords[i])]])[j]]] <- list(id=target_obj$id, size=target_obj$size, label=target_obj$label)
                  id <- paste(as.character(keywords[i]), "_", names(all_assocs[[as.character(keywords[i])]])[j], sep="")
                  edges[[id]] <- list(id=id, source=source_obj$id, target=target_obj$id)
                  #edges <- c(edges, id=list(id=id, source=source_obj$id, target=target_obj$id))
                }
              }
            }
          }
          
          cont <- 1
          finalJsonStr <- '{"nodes": ['
          for (n in total_palabras_assoc) {
            #print(n)
            if (!(is.null(n[["color"]]))) {
              #finalJsonStr <- paste(finalJsonStr, '{"id": "', n$id, '","label": "', n$label, '","x": ', n$x, ', "y": ', n$y, ', "size": ', n$size, ', "color": "', n$color, '"}', sep="")
              finalJsonStr <- paste(finalJsonStr, '{"id": "', n$id, '","label": "', n$label, '", "size": ', n$size, ', "color": "', n$color, '"}', sep="")
            } else {
              #finalJsonStr <- paste(finalJsonStr, '{"id": "', n$id, '","label": "', n$label, '","x": ', n$x, ', "y": ', n$y, ', "size": ', n$size, '}', sep="")
              finalJsonStr <- paste(finalJsonStr, '{"id": "', n$id, '","label": "', n$label, '", "size": ', n$size, '}', sep="")
            }
            if (cont < length(total_palabras_assoc)) {
              finalJsonStr <- paste(finalJsonStr, ",", sep="")
            }
            cont <- cont + 1
          }
          finalJsonStr <- paste(finalJsonStr, '], "edges": [')
          cont <- 1
          for (e in edges) {
            finalJsonStr <- paste(finalJsonStr, '{"id": "', e$id, '","from": "', e$source, '","to": "', e$target, '"}', sep="")
            if (cont < length(edges)) {
              finalJsonStr <- paste(finalJsonStr, ",", sep="")
            }
            cont <- cont + 1
          }
          finalJsonStr <- paste(finalJsonStr, ']')
          finalJsonStr <- paste(finalJsonStr, ', "year": ', y)
          finalJsonStr <- paste(finalJsonStr, ', "month": ', m)
          finalJsonStr <- paste(finalJsonStr, ', "type": "', type, '"', sep="")
          finalJsonStr <- paste(finalJsonStr, '}')
          #print(finalJsonStr)
          bson <- mongo.bson.from.JSON(finalJsonStr)
          mongo.insert(mongo, "facebook.assocs", bson)
          
        } else {
          print(paste(y, m, "already has assocs summary"))
          tmp <- mongo.bson.to.list(tmp)
          print(tmp$`_id`)
        }
      } # If year
      #print(total_palabras_assoc)
    }
  }
}

#palabras_corrupcion_assoc[,4]
print(paste("Generating word associations for posts...", Sys.time()))
generate_assocs_summary("posts", palabras_corrupcion_assoc[,4], palabras_corrupcion_assoc[,3], queries, palabras_corrupcion_assoc[,6], palabras_corrupcion_assoc[,5])
print(paste("Finished generating word associations for posts...", Sys.time()))
print(paste("Generating word associations for comments...", Sys.time()))
generate_assocs_summary("comments", palabras_corrupcion_assoc[,4], palabras_corrupcion_assoc[,3], queries, palabras_corrupcion_assoc[,6], palabras_corrupcion_assoc[,5])
print(paste("Finished word associations for comments...", Sys.time()))

