'''Script for converting a Spotify-generated .csv file to RDF. Receives an input file, an output
file, and an optional limit for the amount of rows to convert.'''

import ast # For parsing csv lists to python lists
import sys # For parsing command line arguments
import urllib.parse # For parsing strings to URI's
from datetime import datetime # For measuring the runtime of the script
import pandas as pd # For handling csv and csv contents
from rdflib import Graph, Literal, RDF, URIRef, Namespace # Basic RDF handling
from rdflib.graph import Collection # RDF lists for the ontology
from rdflib.namespace import XSD, RDFS, OWL # Most common namespaces

# Parsing the input arguments <input file>, <output file> and <limit>.
try:
    IMPORT_PATH = sys.argv[1] if len(sys.argv) > 1 else "csv/tracks_genre.csv"

    EXPORT_PATH = sys.argv[2] if len(sys.argv) > 2 else "spotify.ttl"

    # Special case for <limit>, since it needs to be an integer.
    try:
        LIMIT = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    except ValueError as exc:
        raise SystemExit((f"'{sys.argv[3]}' is not a valid integer. "
            "Please provide a valid integer to limit the RDF output.")) from exc

    if len(sys.argv) > 4:
        raise SystemExit(f"Usage: {sys.argv[0]} <input file> <output file> <limit>")

except IndexError as exc:
    raise SystemExit(f"Usage: {sys.argv[0]} <input file> <output file> <limit>") from exc

# Start the timer to measure how long the script takes.
t0 = datetime.now()
print("Importing file '" + IMPORT_PATH +"'...")

# Attempt to open the input file with pandas. If it's invalid, let the user know.
try:
    df = pd.read_csv(IMPORT_PATH, sep=",", quotechar='"', encoding='utf8')
except FileNotFoundError as exc:
    raise SystemExit(
        f"File '{IMPORT_PATH}' not found. Please provide a valid path to a .csv file.")from exc

# Dictionaries for converting the musical values of the Spotify API to actual musical terms.
keys = {0: "C", 1: "C#", 2:"D", 3:"D#", 4: "E", 5:"F",
    6:"F#", 7:"G", 8:"G#", 9:"A", 10:"A#",11:"B"}
modes = {0: "Minor", 1: "Major"}

# Create the graph and its namespaces.
print("Creating graph...")
g = Graph(base="http://example.org/spotify#")
root = Namespace("http://example.org/spotify#")
track = Namespace("http://example.org/spotify/tracks#")
artist = Namespace("http://example.org/spotify/artists#")
genre = Namespace("http://example.org/spotify/genre#")

g.bind("", root)
g.bind("track", track)
g.bind("artist", artist)
g.bind("genre", genre)

print("Creating triples...")

# If a limit was specified, we can trim the dataframe accordingly.
if LIMIT != 0:
    df = df.head(LIMIT)

# Start iterating over the .csv file to create the Track triples.
for i, row in df.iterrows():

    # Parsing the URIs for Track and Genre.
    track_id = URIRef(track + urllib.parse.quote(row['id']))
    genre_id = URIRef(genre + urllib.parse.quote(row['genre']))

    # Parsing the artist name and id arrays, since they're shaped like a python array in the csv.
    artist_ids = ast.literal_eval(row["id_artists"])
    artist_names = ast.literal_eval(row["artists"])

    # Assigning the type to the track.
    g.set((track_id, RDF.type, URIRef(root + "Track")))

    # Creating the properties in order of appearance in the csv.
    g.set((track_id, RDFS.label, Literal(row['name'])))
    g.set((track_id, URIRef(track + "popularity"), Literal(row['popularity'])))
    g.set((track_id, URIRef(track + "duration_ms"), Literal(row['duration_ms'])))
    g.set((track_id, URIRef(track + "explicit"), Literal(row['explicit'])))

    # We take special precautions to also add the artists to the graph as a separate class.
    # Iterating over the artists in the Track.
    for i, artist_i in enumerate(artist_ids):

        # Parsing the URI for the Artist.
        artist_id = URIRef(artist + urllib.parse.quote(artist_i))

        # Reading the name of the Artist.
        artist_name = artist_names[i]

        # Assigning the type to the artist.
        g.set((artist_id, RDF.type, URIRef(root + "Artist")))

        # Setting the name of the artist.
        g.set((artist_id, RDFS.label, Literal(artist_name)))

        # Adding tuples to relate the artist to the track and vice-versa.
        g.add((artist_id, URIRef(artist + "hasTrack"), track_id))
        g.add((track_id, URIRef(track + "hasArtist"), artist_id))

    # Continue creating the properties in order of appearance in the csv.
    g.add((track_id, URIRef(track + "releaseDate"), Literal(
        row['release_date'], datatype=XSD.gYear)))
    g.set((track_id, URIRef(track + "danceability"), Literal(row['danceability'])))
    g.set((track_id, URIRef(track + "energy"), Literal(row['energy'])))

    # We convert the key with the dictionary we defined earlier.
    g.set((track_id, URIRef(track + "key"), Literal(keys[row['key']])))
    g.set((track_id, URIRef(track + "loudness"), Literal(row['loudness'])))

    # We convert the mode with the dictionary we defined earlier.
    g.set((track_id, URIRef(track + "mode"), Literal(modes[row['mode']])))

    g.set((track_id, URIRef(track + "speechiness"), Literal(row['speechiness'])))
    g.set((track_id, URIRef(track + "acousticness"), Literal(row['acousticness'])))
    g.set((track_id, URIRef(track + "instrumentalness"), Literal(row['instrumentalness'])))
    g.set((track_id, URIRef(track + "liveness"), Literal(row['liveness'])))
    g.set((track_id, URIRef(track + "valence"), Literal(row['valence'])))
    g.set((track_id, URIRef(track + "tempo"), Literal(row['tempo'])))

    # Spotify's API Reference mentions the time signature is in /4, so we add that as well.
    g.set((track_id, URIRef(track + "time_signature"), Literal(f"{row['time_signature']}/4")))

    # Create an instance for the Genre of the song.
    g.add((genre_id, RDF.type, URIRef(root + "Genre")))

    # Setting the name of the genre.
    g.set((genre_id, RDFS.label, Literal(row['genre'])))

    # Adding tuples to relate the genre to the track and vice-versa.
    g.add((track_id, URIRef(track + "hasGenre"), genre_id))
    g.add((genre_id, URIRef(genre + "hasTrack"), track_id))

# Creating additional tuples for the ontology.
print("Creating ontology...")

# artist:hasCollaboratedWith connects two Artists if they have participated on the same Track.
g.add((URIRef(artist + "hasCollaboratedWith"), RDFS.domain, URIRef(root + "Artist")))
g.add((URIRef(artist + "hasCollaboratedWith"), RDFS.range, URIRef(root + "Artist")))
g.add((URIRef(artist + "hasCollaboratedWith"), RDF.type, OWL.SymmetricProperty))

# artist:hasTrack connects an Artist to their Tracks.
g.add((URIRef(artist + "hasTrack"), RDFS.domain, URIRef(root + "Artist")))
g.add((URIRef(artist + "hasTrack"), RDFS.range, URIRef(root + "Track")))

# artist:hasGenre connects an Artist to the Genres in which they have released songs.
g.add((URIRef(artist + "hasGenre"), RDFS.domain, URIRef(root + "Artist")))
g.add((URIRef(artist + "hasGenre"), RDFS.range, URIRef(root + "Genre")))

# track:hasGenre connects a Track to its Genre.
g.add((URIRef(track + "hasGenre"), RDFS.domain, URIRef(root + "Track")))
g.add((URIRef(track + "hasGenre"), RDFS.range, URIRef(root + "Genre")))

# track:hasArtist connects a Track to its Artists.
g.add((URIRef(track + "hasArtist"), RDFS.domain, URIRef(root + "Track")))
g.add((URIRef(track + "hasArtist"), RDFS.range, URIRef(root + "Artist")))

# Some of these properties are opposites, so we define that as well.
g.add((URIRef(track + "hasArtist"), OWL.inverseOf, URIRef(artist + "hasTrack")))
g.add((URIRef(track + "hasGenre"), OWL.inverseOf, URIRef(genre + "hasTrack")))
g.add((URIRef(artist + "hasGenre"), OWL.inverseOf, URIRef(genre + "hasArtist")))

# We create a couple of turtle lists to define some owl:propertyChainAxioms
Collection(g, URIRef(root + "propChain1"), [URIRef(artist + "hasTrack") , URIRef(
    track + "hasArtist")])

Collection(g, URIRef(root + "propChain2"), [URIRef(artist + "hasTrack") , URIRef(
    track + "hasGenre")])

# If an Artist has a Track, and that Track has another Artist, both artists have collaborated.
g.add((URIRef(artist + "hasCollaboratedWith"), OWL.propertyChainAxiom, URIRef(root + "propChain1")))

# If an Artist has a Track, and that Track has a Genre, that Artist has that Genre.
g.add((URIRef(artist + "hasGenre"), OWL.propertyChainAxiom, URIRef(root + "propChain2")))

# Stop the timer once to print how long it took to read the csv and create the graph.
t1 = datetime.now()

print(f"RDF created in {(t1 - t0).total_seconds()} seconds.")
print("Exporting file '" + EXPORT_PATH + "'...")

# Export the graph as a .ttl file in the specified output path.
g.serialize(format="ttl", destination=EXPORT_PATH)

# Stop the timer again to print how long it took to create the file, and how long the entire script
# took.
t2 = datetime.now()

print(f"File created in {(t2 - t1).total_seconds()} seconds.")

print(f"Script executed in {(t2 - t0).total_seconds()} seconds.")
