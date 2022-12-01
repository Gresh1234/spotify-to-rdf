'''ligma'''
import ast #for parsing csv lists to python lists
import urllib.parse #for parsing strings to URI's
from datetime import datetime #for measuring the runtime of the script
import pandas as pd #for handling csv and csv contents
from rdflib import Graph, Literal, RDF, URIRef, Namespace #basic RDF handling
from rdflib.graph import Collection #RDF lists for the ontology
from rdflib.namespace import XSD, RDFS, OWL #most common namespaces

IMPORT_PATH = "csv/tracks_genre.csv"
EXPORT_PATH = "tbl.ttl"

t0 = datetime.now()

print("Importando archivo '" + IMPORT_PATH +"'...")
df = pd.read_csv(IMPORT_PATH, sep=",", quotechar='"') #import csv file

keys = {0: "C", 1: "C#", 2:"D", 3:"D#", 4: "E", 5:"F",
    6:"F#", 7:"G", 8:"G#", 9:"A", 10:"A#",11:"B"}
modes = {0: "Minor", 1: "Major"}

print("Creando grafo...")
g = Graph(base="http://example.org/spotify#")
root = Namespace("http://example.org/spotify#")
track = Namespace("http://example.org/spotify/tracks#")
artist = Namespace("http://example.org/spotify/artists#")

g.bind("", root)
g.bind("track", track)
g.bind("artist", artist)

print("Creando tuplas...")
for i, row in df.head(1000).iterrows():
    track_id = URIRef(track + urllib.parse.quote(row['id']))

    g.add((track_id, RDF.type, URIRef(root + "Track")))
    g.set((track_id, RDFS.label, Literal(row['name'])))
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
        g.set((artist_id, RDFS.label, Literal(artist_name)))
        g.add((artist_id, URIRef(artist + "hasTrack"), track_id))

    g.add((track_id, URIRef(track + "releaseDate"), Literal(
        row['release_date'], datatype=XSD.gYear)))
    g.set((track_id, URIRef(track + "danceability"), Literal(row['danceability'])))
    g.set((track_id, URIRef(track + "energy"), Literal(row['energy'])))
    g.set((track_id, URIRef(track + "key"), Literal(keys[row['key']])))
    g.set((track_id, URIRef(track + "loudness"), Literal(row['loudness'])))
    g.set((track_id, URIRef(track + "mode"), Literal(modes[row['mode']])))
    g.set((track_id, URIRef(track + "speechiness"), Literal(row['speechiness'])))
    g.set((track_id, URIRef(track + "acousticness"), Literal(row['acousticness'])))
    g.set((track_id, URIRef(track + "instrumentalness"), Literal(row['instrumentalness'])))
    g.set((track_id, URIRef(track + "liveness"), Literal(row['liveness'])))
    g.set((track_id, URIRef(track + "valence"), Literal(row['valence'])))
    g.set((track_id, URIRef(track + "tempo"), Literal(row['tempo'])))
    g.set((track_id, URIRef(track + "time_signature"), Literal(f"{row['time_signature']}/4")))
    g.add((track_id, URIRef(track + "hasGenre"), Literal(row['genre'])))

print("Creando ontología...")
g.add((URIRef(artist + "hasCollaboratedWith"), RDFS.domain, URIRef(root + "Artist")))
g.add((URIRef(artist + "hasCollaboratedWith"), RDFS.range, URIRef(root + "Artist")))

g.add((URIRef(artist + "hasTrack"), RDFS.domain, URIRef(root + "Artist")))
g.add((URIRef(artist + "hasTrack"), RDFS.range, URIRef(root + "Track")))

g.add((URIRef(track + "hasArtist"), RDFS.domain, URIRef(root + "Track")))
g.add((URIRef(track + "hasArtist"), RDFS.range, URIRef(root + "Artist")))

g.add((URIRef(track + "hasArtist"), OWL.inverseOf, URIRef(artist + "hasTrack")))

c = Collection(g, URIRef(root + "propChain1"), [URIRef(artist + "hasTrack") , URIRef(
    track + "hasArtist")])

g.add((URIRef(artist + "hasCollaboratedWith"), OWL.propertyChainAxiom, URIRef(root + "propChain1")))
g.add((URIRef(artist + "hasCollaboratedWith"), RDF.type, OWL.SymmetricProperty))

t1 = datetime.now()

print(f"RDF creado en {(t1 - t0).total_seconds()} segundos.")
print("Creando archivo '" + EXPORT_PATH + "'...")

g.serialize(format="ttl", destination=EXPORT_PATH)

t2 = datetime.now()

print(f"Archivo creado en {(t2 - t1).total_seconds()} segundos.")

print(f"Script ejecutado en {(t2 - t0).total_seconds()} segundos.")
