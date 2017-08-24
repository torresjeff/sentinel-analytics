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

	Note the scale must be from -1 to 1.

	By default the script uses the `CSL_politico.csv` lexicon. An option to specify the lexicon through command line will be available in a future update. In the mean time, specify the lexicon in the script as an argument to the function `load_list`. Eg: `obj_pol_user.load_list("lexicons/mylexicon.csv", type_file_enum.polarity)`.
* After setting your lexicon (or using the default one), calculate the polarity for a document using the `process_text` function, like so:
	```
	obj_pol_user = process_list()
	obj_pol_user.load_list("lexicons/CSL_politico.csv",type_file_enum.polarity)
	print(obj_pol_user.process_text("Me gusta la nueva ley de ciencia innovación y tecnologia, Pero algo anda mal  ? "))
	```

	The function returns a dictionary and should look like the following:
	```
	{
		'Label': 'Neutro',
		'Average': 0.25,
		'Words': [
			('polarity', [['gusta', 'gusta', '1']]),
			('polarity', [['nueva', 'nueva', '0']]),
			('polarity', [['ley', 'ley', '0']]),
			('polarity', [['ciencia', 'ciencia', '0']]),
			('polarity', [['innovación', 'innovacion', '1']]),
			('polarity', [['tecnologia', 'tecnologia', '0']]),
			('polarity', [['anda', 'anda', '0']]),
			('polarity', [['mal', 'mal', '-1']])
		],
		'Polarity': 0
	}

	```
	* `Label`: can be one of `Positivo` (positive), `Negativo` (negative) or `Neutro` (neutral). This is a string representation of the calculated polarity.
	* `Average`: calculated polarity in the range [-1, 1].
		* if `0.5 < Average <= 1`  then `Label = Positivo`
		* else if `-1 <= Average < -0.5`  then `Label = Negativo`
		* else `Label = Neutro`
	* `Words`: an array of tuples (one tuple for every word of the sentence, excluding stopwords) with the following structure: `[('polarity', [ORIGINAL WORD, PRE-PROCESSED WORD, SCORE]), ...]`
		* `ORIGINAL WORD`: the original word (including accents if any or special characters) fed into the `process_text` function
		* `PRE-PROCESSED WORD`: same word with no accents or special characters
		* `SCORE`: the score associated with the word as defined in the lexicon
	* `Polarity`: number representation of label (1 = Positivo, -1 = Negativo, 0 = Neutro)



## References
```
Moreno-Sandoval L., Beltrán-Herrera P., Vargas-Cruz J., Sánchez-Barriga C., Pomares-Quimbaya A., Alvarado-Valencia J. and García-Díaz J. (2017). CSL: A Combined Spanish Lexicon - Resource for Polarity Classification and Sentiment Analysis.In Proceedings of the 19th International Conference on Enterprise Information Systems - Volume 1: ICEIS, ISBN 978-989-758-247-9, pages 288-295. DOI: 10.5220/0006336402880295
```

```
Ortiz, C., Eduardo, L., Chappe, C., Catalina, A., Arévalo, F., David, J., 2016. Análisis del sentimiento político mediante la aplicación de herramientas de minería de datos a través del uso de redes sociales.
```