import requests
import json
from spotify import Spotify
import sys


srcSpotify = Spotify('SRC')
dstSpotify = Spotify('DST')

srcPlaylists = srcSpotify.get_user_playlists()
totalSrcPlaylists = srcPlaylists['total']
totalPlaylistsWithMoreThan100Songs = 1


dstPlaylists = dstSpotify.get_user_playlists()

print('There are ' + str(totalSrcPlaylists) + ' playlists')
# print(srcPlaylists['items'])
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
    dstPlaylistID = ''
    for dstPlaylist in dstPlaylists['items']:
        if(dstPlaylist['name'] == playlistName):
            playlistExists = True
            dstPlaylistID = dstPlaylist['id']
            break

    if playlistExists:
        print(f'Playlist "{playlistName}" already exists on DST.')
    else:
        print(f'Playlist "{playlistName}" does not exist on DST.')
        print(f'Creating playlist "{playlistName}" on DST...')
        response = dstSpotify.create_playlist(playlistName, 'Playlist created by Spotify Playlist Migrator')
        dstPlaylistID = response['id']
        if response.status_code == 200:
            print(f'Playlist "{playlistName}" successfully created on DST.')
        else:
            print(f'Failed to create playlist "{playlistName}" on DST. Status code: {response.status_code}')
            print("Exiting program due to failure in creating playlist.")
            sys.exit(1)


    print('\tTracks on this playlist')
    tracks = srcSpotify.get_playlist_items(playlistID)
    songNumber = 1

    
    dstTracks = dstSpotify.get_playlist_items(dstPlaylistID)
    uris = []
    for track in tracks:
        print(f'\t - item #: {songNumber}')
        print('\t - track name: ' + track['name'])
        print('\t - track id: ' + track['id'] + '\n')
        print('\t - track uri: ' + track['uri'])

        # Check if the track exists on DST
        trackExistsOnDst = False
        for dstTrack in dstTracks:
            if dstTrack['uri'] == track['uri']:
                trackExistsOnDst = True
                break

        if trackExistsOnDst:
            print(f'\t - Track "{track["name"]}" already exists on DST playlist. Skipping...')
        else:
            print(f'\t - Track "{track["name"]}" does not exist on DST playlist. Adding...')
            # Add the track to the list of tracks to add
            uris.append(track['uri'])       
    
        songNumber += 1
        if songNumber == 100:
            totalPlaylistsWithMoreThan100Songs += 1


    # Ensure uris is not empty before adding tracks
    
    if not uris:
        print(f'No tracks to add to playlist "{playlistName}". Skipping...')
    else:
        # Add the current track to the destination playlist
        print(f'Adding tracks to playlist "{playlistName}" on DST...')
        print(f'dstPlaylistID: {dstPlaylistID}')
      
        dstSpotify.add_track_to_playlist(dstPlaylistID, uris)


  
print(f'Total playlists: {totalSrcPlaylists}')
print(f'Total playlist with more than 100 songs: {totalPlaylistsWithMoreThan100Songs}')
