import requests
import json
from auth import OAuth
from spotify import Spotify


srcSpotify = Spotify('SRC')

playlists = srcSpotify.get_user_playlists()
totalPlaylists = playlists['total']

print('There are ' + str(totalPlaylists) + ' playlists')

for playlist in playlists['items']:
    
    playlistName = ''
    playlistID = ''

    for key, value in playlist.items():

        if(key == 'name'):
            playlistName = value
        if(key == 'id'):
            playlistID = value
            
    print('Playlist Name: ' + playlistName)
    print('Playlist ID: ' + playlistID + '\r\n')

    print('\tTracks on this playlist')
    tracks = srcSpotify.get_playlist_items(playlistID)
    for track in tracks:
        print('\t - track name: ' + track['name'])
        print('\t - track id: ' + track['id'] + '\n')

  

