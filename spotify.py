import requests
import json
from configparser import ConfigParser

config = ConfigParser(allow_no_value=True)
config.sections()
config.read('config.ini')

import requests

class Spotify:
    def __init__(self, spotify_account_config_section) -> None:
        auth_config = config['AUTH']
        self.base_url = auth_config['apibaseurl']
        self.authUrl = auth_config['authUrl']
        self.tokenUrl = auth_config['tokenUrl']
        self.redirectUri = auth_config['redirectUri']    

        self.spotifyAccountConfigSection = spotify_account_config_section
        if spotify_account_config_section == 'SRC':
            acct_config = config['SRC']
        elif spotify_account_config_section == 'DST':
            acct_config = config['DST']
        else:
            raise ValueError("Invalid spotify_account_config_section value. Must be 'SRC' or 'DST'.")   

        self.userID = acct_config['userID']
        self.clientID = acct_config['clientID']
        self.clientSecret = acct_config['clientSecret']

        self.access_token = self.getToken()
        if self.access_token is None:
            raise Exception("Error fetching token")
        else:
            print("Token fetched successfully: " + self.access_token)
   
    def getToken(self):
        """
        Fetches an access token from Spotify API using client credentials.
        
        Args:
            client_id (str): Your Spotify API client ID
            client_secret (str): Your Spotify API client secret
            
        Returns:
            str: Access token if successful, None if failed
        # """
        
        # Prepare the data payload
        data = {
            "grant_type": "client_credentials",
            "client_id": self.clientID,
            "client_secret": self.clientSecret
        }
        
        # Set headers
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            # Make POST request
            response = requests.post(self.tokenUrl, data=data, headers=headers)
            
            # Raise an exception if the request failed
            response.raise_for_status()
            
            # Parse JSON response and return the access token
            token_data = response.json()
            return token_data.get("access_token")
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching token: {e}")
            return None
        
    def get_user_playlists(self):

        url = f"{self.base_url}/users/{self.userID}/playlists"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        response = requests.get(url, headers=headers)
        print('url is ' + url)
        print('headers is ' + str(headers))
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error fetching playlist: {response.status_code}") 
        
    def get_currentuser_playlists(self):
        url = f"{self.base_url}/users/me/playlists"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        response = requests.get(url, headers=headers)
        print('url is ' + url)
        print('headers is ' + str(headers))
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
                if item is not None and track is not None:
                    tracks.append({
                        "name": track["name"],
                        "id": track["id"],
                        "uri": track["uri"],
                        "artist": track["artists"][0]["name"],
                    })
            return tracks
        else:
            raise Exception(f"Error fetching playlist items: {response.status_code}")

    def create_playlist(self, name, description, public=False):
        url = f"{self.base_url}/users/{self.userID}/playlists"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "name": name,
            "description": description,
            "public": public
        }
        print('headers is ' + str(headers))
        print('payload is ' + str(payload))
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Error creating playlist: {response.status_code}, {response.text}")
            