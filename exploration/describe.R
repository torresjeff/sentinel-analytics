home <- Sys.getenv("HOME")
wd <- paste(home, "/workspace/analytics/util", sep="")
setwd(wd)
getwd()

#install.packages("e1071")
#install.packages("ggplot2")
#install.packages("dplyr")
library(dplyr)
library(e1071)
library(ggplot2)

## 1. Declaración de funciones ##
# Coeficiente de varianza. (> 0.33, la desviacion estandar es grande)
CV <- function(var){(sd(var)/mean(var))}

## 2. Leer datos de entrada ##
# Leer posts, comments, reactions, paginas
posts <- read.csv(file='posts.csv', header=TRUE, sep=",")
comments <- read.csv(file='comments.csv', header=TRUE, sep=",")
reactions <- read.csv(file='reactions.csv', header=TRUE, sep=",")
pages <- read.csv(file='pages.csv', header=TRUE, sep=",")

## 3. Preparación de datos ##
# Crear nueva columna "page_id" en el dataframe posts con el id de la pagina a la que pertenece cada post
posts$page_id <- sub("_[0-9]+", "", posts$X_id)
# Reemplazar valores faltantes por 0. Si está faltando la columna de "shares" es porque simplemente ningún usuario compartió esa publicación
posts$shares[is.na(posts$shares)] <- 0
# Merge los data frames de posts con los de paginas (para tener el nombre de la pagina a la que pertenece cada post)
posts_merged <- merge(posts, pages, by="page_id", all.x=TRUE)
# Merge los reactions con los posts, para tener la cantidad de reacciones (angry, sad, like) para cada publicacion
posts_merged <- merge(posts_merged, reactions, by="X_id")

## POSTS ##
summary(posts_merged)

# Medidas de tendencia central
mean(posts_merged$shares)
mean(posts_merged$sad)
mean(posts_merged$wow)
mean(posts_merged$love)
mean(posts_merged$like)
mean(posts_merged$angry)
mean(posts_merged$haha)

median(posts_merged$shares)
median(posts_merged$sad)
median(posts_merged$wow)
median(posts_merged$love)
median(posts_merged$like)
median(posts_merged$angry)
median(posts_merged$haha)

skewness(posts_merged$shares)
skewness(posts_merged$sad)
skewness(posts_merged$wow)
skewness(posts_merged$love)
skewness(posts_merged$like)
skewness(posts_merged$angry)
skewness(posts_merged$haha)



# Medidas de dispersión
range(posts_merged$name.y ~ posts_merged$shares)
var(posts_merged$shares) ## varianza

IQR(posts_merged$shares) ## Rango intercuartilico (diferencia entre el cuartil 3 y el 1) - robustos a los datos extremos

# desviacion estandar (lo malo es que se deja afectar por datos extremos)
sd(posts_merged$shares)
sd(posts_merged$sad)
sd(posts_merged$wow)
sd(posts_merged$love)
sd(posts_merged$like)
sd(posts_merged$angry)
sd(posts_merged$haha)


# Histograma
ggplot(posts,aes(shares)) + geom_histogram()

#set.seed(1)
#train.indeces <- sample(1:nrow(posts_merged), 5)
#temp <- posts_merged[train.indeces, ]

ggplot(posts_merged, aes(x=name.y, y=shares)) + stat_boxplot(geom ='errorbar', width = 0.4) + geom_boxplot() + labs(x="Página") + theme(axis.text.x=element_text(angle=90,hjust=1,vjust=0.5))
ggplot(posts_merged, aes(x=name.y, y=sad)) + stat_boxplot(geom ='errorbar', width = 0.4) + geom_boxplot() + labs(x="Página") + theme(axis.text.x=element_text(angle=90,hjust=1,vjust=0.5))
ggplot(posts_merged, aes(x=name.y, y=wow)) + stat_boxplot(geom ='errorbar', width = 0.4) + geom_boxplot() + labs(x="Página") + theme(axis.text.x=element_text(angle=90,hjust=1,vjust=0.5))
ggplot(posts_merged, aes(x=name.y, y=love)) + stat_boxplot(geom ='errorbar', width = 0.4) + geom_boxplot() + labs(x="Página") + theme(axis.text.x=element_text(angle=90,hjust=1,vjust=0.5))
ggplot(posts_merged, aes(x=name.y, y=like)) + stat_boxplot(geom ='errorbar', width = 0.4) + geom_boxplot() + labs(x="Página") + theme(axis.text.x=element_text(angle=90,hjust=1,vjust=0.5))
ggplot(posts_merged, aes(x=name.y, y=angry)) + stat_boxplot(geom ='errorbar', width = 0.4) + geom_boxplot() + labs(x="Página") + theme(axis.text.x=element_text(angle=90,hjust=1,vjust=0.5))
ggplot(posts_merged, aes(x=name.y, y=haha)) + stat_boxplot(geom ='errorbar', width = 0.4) + geom_boxplot() + labs(x="Página") + theme(axis.text.x=element_text(angle=90,hjust=1,vjust=0.5))

#CV(posts$shares)

## COMMENTS ##
summary(comments)
sd(comments$like_count)
ggplot(comments, aes(x="", y=like_count)) + stat_boxplot(geom ='errorbar', width = 0.4) + geom_boxplot()
sd(comments$like_count)


## ESCALAR-ESCALAR ##
ggplot(posts_merged, aes(sad + wow + love + like + angry + haha, shares))+ geom_point()  + stat_smooth(method= lm) + labs(x="Reacciones")


## TEXT ANALYSIS ##
library(quanteda)
corp <- corpus(as.character(posts_merged$message))
dtm <- dfm(corp, remove = stopwords("spanish"))
topfeatures(dtm, n = 30, decreasing = TRUE)

corp <- corpus(as.character(posts_merged$name.x))
dtm <- dfm(corp, remove = stopwords("spanish"))
topfeatures(dtm, n = 30, decreasing = TRUE)

corp <- corpus(as.character(posts_merged$description))
dtm <- dfm(corp, remove = stopwords("spanish"))
topfeatures(dtm, n = 30, decreasing = TRUE)

corp <- corpus(as.character(comments$message))
dtm <- dfm(corp, remove = stopwords("spanish"))
topfeatures(dtm, n = 30, decreasing = TRUE)
