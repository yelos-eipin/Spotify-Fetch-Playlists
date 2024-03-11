import requests
import json
from configparser import ConfigParser

config = ConfigParser(allow_no_value=True)
config.sections()
config.read('config.ini')

import requests

class Spotify:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = config['AUTH']['apibaseurl']

    def get_currentuser_playlists(self):
        url = f"{self.base_url}/me/playlists"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error fetching playlist: {response.status_code}")        

    def get_playlist(self, playlist_id):
        url = f"{self.base_url}/playlists/{playlist_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error fetching playlist: {response.status_code}")

    def get_playlist_items(self, playlist_id):
        url = f"{self.base_url}/playlists/{playlist_id}/tracks"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            tracks = []
            for item in data["items"]:
                track = item["track"]
                tracks.append({
                    "name": track["name"],
                    "id": track["id"],
                    "uri": track["uri"],
                    "artist": track["artists"][0]["name"],
                })
            return tracks
        else:
            raise Exception(f"Error fetching playlist items: {response.status_code}")
