"""
Yggdrasil: The World Tree of Music
----------------------------------
A dynamic container for Spotify data:
Genre → Artist → Album → Song

Features:
- Supports manual navigation, random selection, or dynamic song search
- Fetches metadata from Spotify API on-demand
- Saves and reloads data to avoid unnecessary API calls
"""

import os # operating system
import random
import json
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()  # Load keys from .env file

sp = Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

Yggdrasil = {}  #global music tree, initialized as empty dict


# =======================================s==
# DATA STRUCTURE FUNCTIONS
# =========================================

def add_song(genre, artist, album, song_name, metadata=None): #checks each layer of Yggdrasil to see if the request exist in the physical world tree or not
    """Safely add a song to the nested Yggdrasil dictionary."""
    if genre not in Yggdrasil:
        Yggdrasil[genre] = {}
    if artist not in Yggdrasil[genre]:
        Yggdrasil[genre][artist] = {}
    if album not in Yggdrasil[genre][artist]:
        Yggdrasil[genre][artist][album] = {}
    Yggdrasil[genre][artist][album][song_name] = metadata or {}


# =========================================
# SPOTIFY API FUNCTIONS
# =========================================

def search_song_on_spotify(song_name, limit=7): #Limit to number of songs returned is defaulted to 7
    """Search Spotify for a song and return the top results."""
    results = sp.search(q=f"track:{song_name}", type="track", limit=limit)
    tracks = results.get("tracks", {}).get("items", [])
    if not tracks:
        print(f"No results found for '{song_name}'")
        return []

    metadata_list = []
    for track in tracks:
        metadata_list.append({
            "song_name": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "artist_id": track["artists"][0]["id"],
            "spotify_url": track["external_urls"]["spotify"],
            "duration_ms": track["duration_ms"],
            "track_number": track["track_number"],
        }) #compiles each specific layer of metadata in a list and maps them
    return metadata_list


def get_artist_genre(artist_id):
    """Fetch genres for a given artist ID."""
    artist = sp.artist(artist_id)
    genres = artist.get("genres", []) #default return value
    return genres[0] if genres else "Unknown"


def add_song_dynamic(song_name):
    """Search for a song, fetch metadata, and add it to Yggdrasil."""
    results = search_song_on_spotify(song_name)
    if not results:
        return None

    # If multiple results, let the user choose
    if len(results) > 1:
        print(f"\nFound multiple results for '{song_name}':")
        for i, track in enumerate(results, start=1): #enumerate adds a counter to the i variable which is then passed into the f string in line 88
            print(f"{i}. {track['song_name']} by {track['artist']} (Album: {track['album']})")
        choice = input("Select a number (or 0 to cancel): ")
        try:
            choice = int(choice)
            if choice == 0:
                return None
            metadata = results[choice - 1]
        except (ValueError, IndexError): #addresses the specific possible error cases in the try block
            print("Invalid choice. Cancelled.")
            return None
    else:
        metadata = results[0]

    genre = get_artist_genre(metadata["artist_id"])
    add_song(genre, metadata["artist"], metadata["album"], metadata["song_name"], metadata)
    save_yggdrasil()
    print(f"\nAdded '{metadata['song_name']}' under genre '{genre}' to Yggdrasil.")
    return metadata


# =========================================
# RANDOM SELECTION FUNCTIONS
# =========================================

def random_genre():
    return random.choice(list(Yggdrasil.keys()))

def random_artist(genre):
    return random.choice(list(Yggdrasil[genre].keys()))

def random_album(genre, artist):
    return random.choice(list(Yggdrasil[genre][artist].keys()))

def random_song(genre, artist, album):
    return random.choice(list(Yggdrasil[genre][artist][album].keys()))


# =========================================
# SAVE / LOAD FUNCTIONS
# =========================================

def save_yggdrasil(filename="yggdrasil.json"):
    """Save the full Yggdrasil dictionary to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(Yggdrasil, f, indent=4)
    print(f"Yggdrasil saved to {filename}.")


def load_yggdrasil(filename="yggdrasil.json"):
    """Load Yggdrasil data from a JSON file if it exists."""
    global Yggdrasil
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            Yggdrasil = json.load(f)
        print(f"Loaded Yggdrasil from {filename}.")
    else:
        print("No saved Yggdrasil found — starting fresh.")
        Yggdrasil = {}


# =========================================
# USER NAVIGATION
# =========================================

def enter_bragi():
    """Allow the user to manually explore, get a random song, or search dynamically. Named after the Norse god of Music and Poetry: Bragi"""
    print("\nWelcome to Yggdrasil — The Tree of Music")
    print("Options:\n1. Manual navigation\n2. Random song\n3. Search Spotify for a song")
    choice = input("Select an option (1/2/3): ")

    if choice == "1":
        if not Yggdrasil:
            print("Yggdrasil is empty. Try option 3 to add songs.")
            return
        genre = input(f"\nEnter a genre ({', '.join(Yggdrasil.keys())}): ")
        artist = input(f"Enter an artist ({', '.join(Yggdrasil[genre].keys())}): ")
        album = input(f"Enter an album ({', '.join(Yggdrasil[genre][artist].keys())}): ")
        song = input(f"Enter a song ({', '.join(Yggdrasil[genre][artist][album].keys())}): ")
        metadata = Yggdrasil[genre][artist][album][song]

    elif choice == "2":
        if not Yggdrasil:
            print("Yggdrasil is empty. Try option 3 to add songs.")
            return
        genre = random_genre()
        artist = random_artist(genre)
        album = random_album(genre, artist)
        song = random_song(genre, artist, album)
        metadata = Yggdrasil[genre][artist][album][song]

    elif choice == "3":
        song_name = input("Enter the name of the song you want: ")
        metadata = add_song_dynamic(song_name)
        if not metadata:
            return
        genre = get_artist_genre(metadata["artist_id"])
        artist = metadata["artist"]
        album = metadata["album"]
        song = metadata["song_name"]

    else:
        print("Invalid input. Try again.")
        return

    # Display sorted metadata
    print("\n--- Song Info ---")
    print(f"Song: {song}")
    print(f"Artist: {artist}")
    print(f"Album: {album}")
    print(f"Genre: {genre}")
    print(f"Spotify URL: {metadata.get('spotify_url')}")
    print(f"Duration (ms): {metadata.get('duration_ms')}")
    print(f"Track number: {metadata.get('track_number')}")


# =========================================
# MAIN PROGRAM
# =========================================

if __name__ == "__main__":
    load_yggdrasil()
    while True:
        enter_bragi()
        cont = input("\nDo you want to continue? (y/n): ").lower()
        if cont != "y":
            break
    save_yggdrasil()
    print("Thank you for visiting The World Tree of Music!", end="")
    print("\n")
    print("This has been Yggdrasil.")
    print("\n\tBrought to you by アトラス.")
