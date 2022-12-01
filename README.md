# spotify-to-rdf

CC7220 - La Web de Datos, Group 11 Final Project

## What is this?

It's a python script to convert .csv data exported from [Spotify's Web API](https://developer.spotify.com/documentation/web-api/), more specifically [this dataset](https://www.kaggle.com/datasets/carlodenardin/spotifydv) by [Carlo De Nardin](https://www.kaggle.com/carlodenardin) on Kaggle.

## How am I supposed to use it?

All you need is [pandas](https://pandas.pydata.org/) and [rdflib](https://rdflib.readthedocs.io/en/stable/). You can install both with `pip install -r requirements.txt`

You can run the script on the command line, providing three arguments: `python rdf_converter.py <input file> <output file> <limit>`. The default arguments are `python rdf_converter.py csv/tracks_genre.csv spotify.ttl 0`.

Consider that the input .csv has to be in an appropriate format, the output file has to be a .ttl, and the limit can be a positive or negative integer as per https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.head.html .
