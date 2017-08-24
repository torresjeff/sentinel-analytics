library(tm)
library(quanteda)

posts <- c()
posts <- c(posts, c("El corrupto del presidente", "Este es el corrupto presidente más corrupto de la historia", "Álvaro Uribe es un corrupto", "No más corrupción"))
corp <- corpus(posts)
  #c("El corrupto de Álvaro Uribe", "Este es Álvaro Uribe, el presidente más corrupto de la historia", "El presidente es un corrupto", "No más corrupción")))
dtm <- dfm(corp, remove = stopwords("spanish"), VERBOSE = FALSE)
as.matrix(dtm)

tok <- tokens(corp, remove_punct = TRUE, remove_symbols = TRUE, remove_url = TRUE)
tok <- removeFeatures(tok, stopwords("spanish")) # TODO: completar stopwords
myfcm <- fcm(tok, context = "window", window = 10)
as.matrix(myfcm)
write.csv(myfcm, "fcm.csv")
associations <- textstat_simil(dtm, c("text1", "text2", "text3", "text4"), margin = "document")

print(associations)

rm(posts)
rm(corp)
rm(dtm)
