from requests_oauthlib import OAuth2Session
import requests
import json
from auth import OAuth
from spotify import Spotify


client = OAuth()

# check that we have valid tokens
# This will also output the URL to allow the app permission the first time
client.checkStatus()

accessToken = client.showAccessToken()
spotify = Spotify(accessToken)

playlists = spotify.get_currentuser_playlists()
totalPlaylists = playlists['total']

print('There are ' + str(totalPlaylists) + ' playlists')

for playlist in playlists['items']:
    for key, value in playlist.items():
        if(key == 'name'):
            print('Playlist Name: ' + value)
        if(key == 'id'):
            print('id: ' + value)
        if(value == '0PW2K9yIi47IxAlQ6Mmrrb'):
            print('\tTracks on this playlist')
            tracks = spotify.get_playlist_items(value)
            for track in tracks:
                print('\t - track name: ' + track['name'])
                print('\t - track id: ' + track['id'] + '\n')
        

