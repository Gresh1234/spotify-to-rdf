from rdflib import Graph, Literal, RDF, URIRef, BNode, Namespace #basic RDF handling
import ast
import pandas as pd #for handling csv and csv contents
from rdflib.namespace import XSD, RDFS, OWL #most common namespaces
import urllib.parse #for parsing strings to URI's


df = pd.read_csv("csv/tracks_genre.csv",sep=",",quotechar='"') #import csv file

g = Graph(base="http://example.org/")
root = Namespace("http://example.org/")
track = Namespace("http://example.org/tracks/")
artist = Namespace("http://example.org/artists/")

g.bind("track", track)
g.bind("artist", artist)

for i, row in df.head(100).iterrows():
    track_id = URIRef(track + urllib.parse.quote(row['id']))

    g.add((track_id, RDF.type, URIRef(root + "Track")))
    g.set((track_id, URIRef(track + "name"), Literal(row['name'])))
    g.set((track_id, URIRef(track + "popularity"), Literal(row['popularity'])))
    g.set((track_id, URIRef(track + "duration_ms"), Literal(row['duration_ms'])))
    g.set((track_id, URIRef(track + "explicit"), Literal(row['explicit'])))
    
    artist_ids = ast.literal_eval(row["id_artists"])
    artist_names = ast.literal_eval(row["artists"])

    for i in range(len(artist_ids)):
        artist_id = URIRef(artist + urllib.parse.quote(artist_ids[i]))
        artist_name = artist_names[i]

        g.add((track_id, URIRef(track + "hasArtist"), artist_id))

        g.add((artist_id, RDF.type, URIRef(root + "Artist")))
        g.set((artist_id, URIRef(artist + "Name"), Literal(artist_name)))
        g.add((artist_id, URIRef(artist + "hasTrack"), track_id))
    
    g.add((track_id, URIRef(track + "releaseDate"), Literal(row['release_date'], datatype=XSD.gYear)))

    g.add((track_id, URIRef(track + "hasGenre"), Literal(row['genre'])))

    g.add((URIRef(artist + "hasTrack"), ))



print(g.serialize())