import requests
import json
import webbrowser
from configparser import ConfigParser
from urllib.parse import urlencode, urlparse, parse_qs

config = ConfigParser(allow_no_value=True)
config.sections()
config.read('config.ini')

class Spotify:
    def __init__(self, spotify_account_config_section) -> None:
        auth_config = config['AUTH']
        self.base_url = auth_config['apibaseurl']
        self.authUrl = auth_config['authUrl']
        self.tokenUrl = auth_config['tokenUrl']
        self.redirectUri = auth_config['redirectUri']    
        self.userType = ''
        self.validUserAuth = False

        self.spotifyAccountConfigSection = spotify_account_config_section
        if spotify_account_config_section == 'SRC':
            acct_config = config['SRC']
            self.userType = 'SRC'
        elif spotify_account_config_section == 'DST':
            acct_config = config['DST']
            self.userType = 'DST'
        else:
            raise ValueError("Invalid spotify_account_config_section value. Must be 'SRC' or 'DST'.")   

        self.userID = acct_config['userID']
        self.clientID = acct_config['clientID']
        self.clientSecret = acct_config['clientSecret']
        self.scopes = acct_config['scopes']

        if self.userType == 'DST':
            # self.access_token = self.get_user_authorization_token()
            self.access_token = self.getToken()
        else:
            # self.access_token = self.get_user_authorization_token()
            self.access_token = self.getToken()
        if self.access_token is None:
            raise Exception("Error fetching token")
        else:
            print("Token fetched successfully: " + self.access_token)

        self.access_token = self.getToken()
        if self.access_token is None:
            raise Exception("Error fetching token")
        else:
            print("Token fetched successfully: " + self.access_token)
   
   
    def get_user_authorization_token(self):
        """
        Implements the Authorization Code Flow to get an access token for the end user.
        """

        # Step 1: Redirect user to Spotify's authorization page
        auth_query_parameters = {
            "client_id": self.clientID,
            "response_type": "code",
            "redirect_uri": self.redirectUri,
            "scope": self.scopes,
        }
        auth_url = f"{self.authUrl}?{urlencode(auth_query_parameters)}"
        print(f"Opening browser for user authorization: {auth_url}")
        webbrowser.open(auth_url)

        # Step 2: User logs in and Spotify redirects to redirectUri with a code
        redirect_response = input("Paste the full redirect URL here: ")
        parsed_url = urlparse(redirect_response)
        code = parse_qs(parsed_url.query).get("code")

        if not code:
            raise Exception("Authorization code not found in the redirect URL.")
        code = code[0]

        # Step 3: Exchange the authorization code for an access token
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirectUri,
            "client_id": self.clientID,
            "client_secret": self.clientSecret,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            response = requests.post(self.tokenUrl, data=token_data, headers=headers)
            response.raise_for_status()
            token_response_data = response.json()
            # print('Token response data: ' + str(token_response_data))
            return token_response_data.get("access_token")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching user authorization token: {e}")
            return None
        
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
            "client_secret": self.clientSecret,
            "scope": self.scopes
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
            # print('token_data is ' + str(token_data))
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
        # print('headers is ' + str(headers))
        if response.status_code == 200:
            # print('response is ' + str(response))
            # print('response text is ' + str(response.text))
            return response.json()
        else:
            raise Exception(f"Error fetching playlist: {response.status_code}") 
        
    def get_currentuser_playlists(self):
        url = f"{self.base_url}/users/me/playlists"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        response = requests.get(url, headers=headers)
        # print('url is ' + url)
        # print('headers is ' + str(headers))
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

    def add_track_to_playlist(self, playlist_id, track_uris):
        """
        Adds one or more tracks to a Spotify playlist.

        Args:
            playlist_id (str): The ID of the playlist.
            track_uris (list): A list of track URIs to add to the playlist.

        Returns:
            dict: The response from the Spotify API if successful.

        Raises:
            Exception: If the request fails.
        """
        # Check if the user is authenticated
        # If not, get the user authorization token
        if self.validUserAuth == False:
            self.access_token = self.get_user_authorization_token()
            self.validUserAuth = True

        url = f"{self.base_url}/playlists/{playlist_id}/tracks"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "uris": track_uris
        }
        # print('payload is ' + str(payload))

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Error adding items to playlist: {response.status_code}, {response.text}")
        
    def create_playlist(self, name, description, public=True, collaborative=True):
        if self.validUserAuth == False:
            self.access_token = self.get_user_authorization_token()
            self.validUserAuth = True
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
        # print('headers is ' + str(headers))
        # print('payload is ' + str(payload))
        # print('url is ' + url)
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Error creating playlist: {response.status_code}, {response.text}")
            