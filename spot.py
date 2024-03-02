import pandas as pd
from dataclasses import dataclass, field, asdict
from typing import List, Tuple
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import billboard
from collections import defaultdict, Counter, namedtuple
from models import Artist, AudioFeatures, Track

"""
NOTE: When submitting to PrairieLearn, please ensure that the function call to main() at the bottom of the file is commented out, as well as any other places you have called the getPlaylist() or getHot100() functions. A simple CTRL/CMD + F to search will 
suffice. 

PrairieLearn will fail to grade your submission if the main() function is still commented in OR if a call to getPlaylist() or getHot100() is still present in your code.  
"""

"""
SETUP: Must do first!
"""
# Task 1: Install `spotipy` using: `conda install spotipy`

# Task 2: Grab the Spotify ClientID and Secret to make API calls.
# TODO: Replace the two variables in your config.py file

# import config

#https://developer.spotify.com/dashboard/applications to get client_id and client_secret
# sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=config.CLIENT_ID, client_secret=config.CLIENT_SECRET))

"""
PART 1: Getting the Top 100 Data!
You must complete Part 1 before moving on down below
"""
def getPlaylist(id: str) -> List[Track]:
    '''
    Given a playlist ID, returns a list of Track objects corresponding to the songs on the playlist. See
    models.py for the definition of dataclasses Track, Artist, and AudioFeatures.
    We need the audio features of each track to populate the audiofeatures list.
    We need the genre(s) of each artist in order to populate the artists in the artist list.

    We've written parts of this function, but it's up to you to complete it!
    '''
    
    # fetch tracks data from spotify given a playlist id
    playlistdata = sp.playlist(id)
    tracks = playlistdata['tracks']['items']

    # fetch audio features based on the data stored in the playlist result
    track_ids = [track['track']['id'] for track in tracks] #TODO: build a list of track_ids from the tracks
    audio_features = sp.audio_features(track_ids)
    
    audio_info = {}  # Audio features list might not be in the same order as the track list
    for af in audio_features:
        audio_info[af['id']] = AudioFeatures(af['danceability'], \
                                             af['energy'], \
                                             af['key'],  \
                                             af['loudness'],  \
                                             af['mode'],  \
                                             af['speechiness'], \
                                             af['acousticness'], \
                                             af['instrumentalness'], \
                                             af['liveness'], \
                                             af['valence'], \
                                             af['tempo'], \
                                             af['duration_ms'], \
                                             af['time_signature'], \
                                             af['id'])


    # prepare artist dictionary
    artist_ids = [artist['id'] for track in tracks for artist in track['track']['artists']] # TODO: make a list of unique artist ids from tracks list
    artists = {}
    for k in range(1+len(artist_ids)//50): # can only request info on 50 artists at a time!
        artists_response = sp.artists(artist_ids[k*50:min((k+1)*50,len(artist_ids))]) #what is this doing?
        for a in artists_response['artists']:
            artists[a['id']] = Artist(id = a['id'],
                                      name = a['name'],
                                      genres = a['genres'])# TODO: create the Artist for each id (see audio_info, above)


    # populate track dataclass
    trackList = [Track(id = t['track']['id'], # TODO: your code here     , \
                       name= t['track']['name'], # TODO: your code here    , \
                       artists= [artists[artist['id']] for artist in t['track']['artists']], # TODO: your code here , \
                       audio_features= audio_info[t['track']['id']])# TODO: your code here ) \
                           for t in tracks]

    return trackList

''' this function is just a way of naming the list we're using. You can write
additional functions like "top Canadian hits!" if you want.''' 
'''
def getHot100() -> List[Track]:
    # Billboard hot 100 Playlist ID URI
    hot_100_id = "6UeSakyzhiEt4NB3UAd6NQ"
    return getPlaylist(hot_100_id)

'''

# getPlaylist('20x303ywxynPNR3dXgzjE8') # Test getPlaylist()! *** Uncomment to test


# ---------------------------------------------------------------------
# ...

"""
Part 2: The Helper Functions
Now that we have the billboard's top 100 tracks, let's design some helper functions that will make our lives easier when creating our dataframe.
"""

def getGenres(t: Track) -> List[str]:
    '''
    TODO
    Takes in a Track and produce a list of unique genres that the artists of this track belong to
    '''
    genres = set()  # Using a set to ensure uniqueness
    for artist in t.artists:
        genres.update(artist.genres)
    return list(genres)

def doesGenreContains(t: Track, genre: str) -> bool:
    '''
    TODO
    Checks if the genres of a track contains the key string specified
    For example, if a Track's unique genres are ['pop', 'country pop', 'dance pop']
    doesGenreContains(t, 'dance') == True
    doesGenreContains(t, 'pop') == True
    doesGenreContains(t, 'hip hop') == False
    '''
    genre_lower = genre.lower()
    
    for artist in t.artists:
        for artist_genre in artist.genres:
            if genre_lower in artist_genre.lower():
                return True
    return False

'''# *** Test run: Uncomment
playlist_id = "20x303ywxynPNR3dXgzjE8"
playlist_tracks = getPlaylist(playlist_id)
track_to_test = playlist_tracks[]
#  genre to check
genre_to_check = "japanese teen pop"

# Test the doesGenreContains function
result = doesGenreContains(track_to_test, genre_to_check)
print(f"Does the current Track have the genre '{genre_to_check}'? {result}") # Result: checked
'''

def getTrackDataFrame(tracks: List[Track]) -> pd.DataFrame:
    '''
    This function is given.
    Prepare dataframe for a list of tracks
    audio-features: 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
                    'duration_ms', 'time_signature', 'id', 
    track & artist: 'track_name', 'artist_ids', 'artist_names', 'genres', 
                    'is_pop', 'is_rap', 'is_dance', 'is_country'
    '''
    # populate records
    records = []
    for t in tracks:
        to_add = asdict(t.audio_features) #converts the audio_features object to a dict
        to_add["track_name"] = t.name
        to_add["artist_ids"] = list(map(lambda a: a.id, t.artists)) # we will discuss this in class
        to_add["artist_names"] = list(map(lambda a: a.name, t.artists))
        to_add["genres"] = getGenres(t)
        to_add["is_pop"] = doesGenreContains(t, "pop")
        to_add["is_rap"] = doesGenreContains(t, "rap")
        to_add["is_dance"] = doesGenreContains(t, "dance")
        to_add["is_country"] = doesGenreContains(t, "country")
        
        records.append(to_add)
        
    # create dataframe from records
    df = pd.DataFrame.from_records(records)
    return df

# ---------------------------------------------------------------------
# The most popular artist of the week
# HashableArtist = namedtuple('HashableArtist', ['id', 'name', 'genres'])

def artist_with_most_tracks(tracks: List[Track]) -> (Artist, int):
    '''
    TODO
    List of tracks -> (artist, number of tracks the artist has)
    This function finds the artist with the most number of tracks on the list
    If there is a tie, you may return any of the artists
    '''         
    tally = Counter()  # Counter to keep track of the number of tracks for each artist

    # Count the tracks for each artist
    for track in tracks:
        for artist in track.artists:
            tally[artist] += 1

    # Find the artist(s) with the maximum count
    most_common_artist, count = tally.most_common(1)[0]  # Retrieve the most common artist and their count

    return most_common_artist, count

# artist_with_most_tracks(getPlaylist('20x303ywxynPNR3dXgzjE8'))


'''# *** Test Run:
most_common_artist, track_count = artist_with_most_tracks(playlist_tracks)
# Print the result
print(f"The artist with the most tracks is {most_common_artist.name} with {track_count} tracks.")
'''

"""
Part 3: Visualizing the Data
"""

# 3.1 scatter plot of dancability-speechiness with markers colored by genre: is_rap

def danceability_plot(tracks: List[Track]):
    danceabilities = [t.audio_features.danceability for t in tracks]
    speechiness = [t.audio_features.speechiness for t in tracks]
    
    is_rap = [any('rap' in genre.lower() for genre in getGenres(t)) for t in tracks]
    
    # Plotting the scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(danceabilities, speechiness, c=is_rap, cmap='coolwarm', alpha=0.7)

    plt.title('Scatter Plot of Danceability vs Speechiness (Colored by Rap)')
    plt.colorbar(label='Is Rap')
    plt.xlabel('Danceability')
    plt.ylabel('Speechiness')
    
    plt.show()

# ...
    
# 3.2 scatter plot (ask your own question)
# scatter plot of dancability vs. energy (NOT with markers colored by genre: is_rap)
def danceability_energy_plot(tracks: List[Track]):
    danceabilities = [t.audio_features.danceability for t in tracks]
    energy = [t.audio_features.energy for t in tracks]
    
    # Plotting the scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(danceabilities, energy, alpha=0.7)

    plt.title('Scatter Plot of Danceability vs Energy')
    plt.xlabel('Danceability')
    plt.ylabel('Energy')
    
    plt.show()

# danceability_energy_plot(getPlaylist('20x303ywxynPNR3dXgzjE8'))

'''
def main():
    top100Tracks = getHot100()
    df = getTrackDataFrame(top100Tracks)
    print(df.head())
    artist, num_track = artist_with_most_tracks(top100Tracks)
    print("%s has the most number of tracks on this week's Hot 100 at a whopping %d tracks!" % (artist.name, num_track))

main()
'''

