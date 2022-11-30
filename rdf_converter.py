'''ligma'''
import ast
import urllib.parse #for parsing strings to URI's
import pandas as pd #for handling csv and csv contents
from rdflib import Graph, Literal, RDF, URIRef, Namespace #basic RDF handling
from rdflib.graph import Collection
from rdflib.namespace import XSD, RDFS, OWL #most common namespaces


df = pd.read_csv("csv/tracks_genre.csv",sep=",",quotechar='"') #import csv file

g = Graph(base="http://example.org/#")
root = Namespace("http://example.org/#")
track = Namespace("http://example.org/tracks/#")
artist = Namespace("http://example.org/artists/#")

g.bind("track", track)
g.bind("artist", artist)

for i, row in df.iterrows():
    track_id = URIRef(track + urllib.parse.quote(row['id']))

    g.add((track_id, RDF.type, URIRef(root + "Track")))
    g.set((track_id, URIRef(track + "name"), Literal(row['name'])))
    g.set((track_id, URIRef(track + "popularity"), Literal(row['popularity'])))
    g.set((track_id, URIRef(track + "duration_ms"), Literal(row['duration_ms'])))
    g.set((track_id, URIRef(track + "explicit"), Literal(row['explicit'])))

    artist_ids = ast.literal_eval(row["id_artists"])
    artist_names = ast.literal_eval(row["artists"])

    for i, artist_i in enumerate(artist_ids):
        artist_id = URIRef(artist + urllib.parse.quote(artist_i))
        artist_name = artist_names[i]

        g.add((track_id, URIRef(track + "hasArtist"), artist_id))

        g.add((artist_id, RDF.type, URIRef(root + "Artist")))
        g.set((artist_id, URIRef(artist + "Name"), Literal(artist_name)))
        g.add((artist_id, URIRef(artist + "hasTrack"), track_id))

    g.add((track_id, URIRef(track + "releaseDate"), Literal(
        row['release_date'], datatype=XSD.gYear)))

    g.add((track_id, URIRef(track + "hasGenre"), Literal(row['genre'])))

g.add((URIRef(artist + "hasTrack"), RDFS.domain, URIRef(root + "Artist")))
g.add((URIRef(artist + "hasTrack"), RDFS.range, URIRef(root + "Track")))

g.add((URIRef(artist + "hasArtist"), RDFS.domain, URIRef(root + "Track")))
g.add((URIRef(artist + "hasArtist"), RDFS.range, URIRef(root + "Artist")))

g.add((URIRef(artist + "hasArtist"), OWL.inverseOf, URIRef(artist + "hasTrack")))

c = Collection(g, URIRef(root + "ligma"), [URIRef(artist + "hasTrack") , URIRef(
    track + "hasArtist")])

g.add((URIRef(artist + "hasCollaboratedWith"), OWL.propertyChainAxiom, URIRef(root + "ligma")))
g.add((URIRef(artist + "hasCollaboratedWith"), RDF.type, OWL.IrreflexiveProperty))
g.add((URIRef(artist + "hasCollaboratedWith"), RDF.type, OWL.SymmetricProperty))

print(g.serialize(format="ttl"))
g.serialize(destination="spotify.ttl")
