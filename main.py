import requests
import json
# from auth import OAuth
from spotify import Spotify
import sys


srcSpotify = Spotify('SRC')
dstSpotify = Spotify('DST')

srcPlaylists = srcSpotify.get_user_playlists()
totalSrcPlaylists = srcPlaylists['total']
totalPlaylistsWithMoreThan100Songs = 1


dstPlaylists = dstSpotify.get_user_playlists()

print('There are ' + str(totalSrcPlaylists) + ' playlists')

for playlist in srcPlaylists['items']:
    
    playlistName = ''
    playlistID = ''

    for key, value in playlist.items():

        if(key == 'name'):
            playlistName = value
        if(key == 'id'):
            playlistID = value
            
    print('Playlist Name: ' + playlistName)
    print('Playlist ID: ' + playlistID + '\r\n')

    # check if list already exists on DST
    playlistExists = False
    for dstPlaylist in dstPlaylists['items']:
        if(dstPlaylist['name'] == playlistName):
            playlistExists = True
            break

    if playlistExists:
        print(f'Playlist "{playlistName}" already exists on DST.')
        dstPlaylists = dstSpotify.get_currentuser_playlists()
        for key, value in dstPlaylists.items():   
            if(key == 'owner'):
                for key1, value1 in dstPlaylists['owner'].items():
                    if(key == 'id'):
                        playlistOwnerID = value['id']
                        print(f'Playlist Owner ID: {playlistOwnerID}')
    else:
        print(f'Playlist "{playlistName}" does not exist on DST.')
        # print(f'Creating playlist "{playlistName}" on DST...')
        # response = dstSpotify.create_playlist(playlistName, 'Playlist created by Spotify Playlist Migrator', False)
        # if response.status_code == 200:
        #     print(f'Playlist "{playlistName}" successfully created on DST.')
        # else:
        #     print(f'Failed to create playlist "{playlistName}" on DST. Status code: {response.status_code}')
        #     print("Exiting program due to failure in creating playlist.")
        #     sys.exit(1)


    print('\tTracks on this playlist')
    tracks = srcSpotify.get_playlist_items(playlistID)
    songNumber = 1
    for track in tracks:
        print(f'\t - item #: {songNumber}')
        print('\t - track name: ' + track['name'])
        print('\t - track id: ' + track['id'] + '\n')
        songNumber += 1
        if songNumber == 100:
            totalPlaylistsWithMoreThan100Songs += 1


  
print(f'Total playlists: {totalSrcPlaylists}')
print(f'Total playlist with more than 100 songs: {totalPlaylistsWithMoreThan100Songs}')
