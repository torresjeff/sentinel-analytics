# sentiment-analysis
Sentiment analysis in Spanish using a bag-of-words approach.

This script was developed by CAOBA - Center of Excelence and Appropriation of Big Data and Data Analaytics as part of their paper [CSL: A Combined Spanish lexicon - Resource for Polarity Classification and Sentiment Analysis](http://www.scitepress.org/DigitalLibrary/PublicationsDetail.aspx?ID=J41cKicqYUA=&t=1).

## Dependencies
* Python 3.5.2
* pip: `$ sudo apt-get install python3-pip`
* NLTK: `$ pip3 install nltk`
* Numpy: `$ pip3 install numpy`
* NLTK stopword corpus and snowball data (download these using Python interpreter):
	```
	$ python3
	>>> import nltk
	>>> nltk.download('popular')
	```

## Usage
* Make sure you have your lexicons in the `lexicons` folder.
* The lexicons must be a csv file with the following structure:
	```
	...
	bailado;1
	condicionarla;1
	alcanzarse;1
	sesiones;0
	matar;-1
	...
	```
1 = positive, 0 = neutral, -1 = negative

By default the script uses the `CSL_politico.csv` lexicon. An option to specify the lexicon through command line will be available in a future update. In the mean time, specify the lexicon in the script as an argument to the function `load_list`. Eg: `obj_pol_user.load_list("lexicons/mylexicon.csv", type_file_enum.polarity)`.


## References
```
Moreno-Sandoval L., Beltrán-Herrera P., Vargas-Cruz J., Sánchez-Barriga C., Pomares-Quimbaya A., Alvarado-Valencia J. and García-Díaz J. (2017). CSL: A Combined Spanish Lexicon - Resource for Polarity Classification and Sentiment Analysis.In Proceedings of the 19th International Conference on Enterprise Information Systems - Volume 1: ICEIS, ISBN 978-989-758-247-9, pages 288-295. DOI: 10.5220/0006336402880295
```

```
Ortiz, C., Eduardo, L., Chappe, C., Catalina, A., Arévalo, F., David, J., 2016. Análisis del sentimiento político mediante la aplicación de herramientas de minería de datos a través del uso de redes sociales.
```