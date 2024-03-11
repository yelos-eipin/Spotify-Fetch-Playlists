from requests_oauthlib import OAuth2Session
import requests
import json
from configparser import ConfigParser

config = ConfigParser(allow_no_value=True)
config.sections()
config.read('config.ini')

class OAuth:
    """ Class to get Auth token from API service """

    def __init__(self) -> None:
        self.clientID = config['AUTH']['clientID']
        self.clientSecret = config['AUTH']['clientSecret']
        self.accessCode = config['AUTH']['accessCode']
        self.accessToken = config['AUTH']['accessToken']
        self.refreshToken = config['AUTH']['refreshToken']
        self.authUrl = config['AUTH']['authUrl']
        self.tokenUrl = config['AUTH']['tokenUrl']
        self.redirectUri = config['AUTH']['redirectUri']
        self.scopes = config['AUTH']['scopes']

        # SCOPES_TO_REQUEST = {'offline_access', 'ag1', 'eq1', 'files'}
        self.STATE = "Some Unique Identifier"
        self.oauth2_session = OAuth2Session(self.clientID,  redirect_uri=self.redirectUri, scope=self.scopes)

    def showAccessToken(self):    
        return self.accessToken

    def checkStatus(self):
        """ 
        checkStatus function goes through the following steps

        freshToken exists
        -> yes
            - check if it is valid
            - if valid, this auth session is ready to execute comamnds against API. exit
            - if not valid, check if we have an accessToken
                - accessToken exists
                    - check if it's valid
                        - if accessToken is valid, get a refreshToken
                        - if not valid, check if we have an accessCode
                            - if we have an accessCode, get an accessToken and then a refreshToken.
                - if accessToken doesn't exist, check if we have an accessCode
                    - if we have an accessCode, get an accessToken and then a refreshToken.
        -> no


        
        """
        if( self.refreshToken ):
            # refreshToken exists. Attempt to refresh it 
            self.getRefreshToken()
        
        else:
            # if there is no refresh token, check if there is an accessToken
            print('There is no refreshToken')
            if( self.accessToken ):
                # accessToken exists. Attempt to refresh it
                print('attempt refresh accessToken')
                self.getAccessToken()
            else:
                # if there is no accessToken, check if there is an accessCode
                print('There is no accessToken')
                if( self.accessCode ):
                    # accessCode exists. Attempt to retrieve accessToken with it
                    print('attempt to retrieve accessToken')
                    self.getAccessToken()
                else:
                    # if there is no accessCode, start from scrach and get one
                    print('There is no accessCode')  
                    # get accessCode
                    self.getAccessCode()       

    def getAccessCode(self):
        """
            In theory, this should only run the first time doing OAuth against the API or if the accessCode has become invalid (eg.: not used in more than a year)
            This requires user interaction on the browser to log in and accept the prompts
        """

        authorization_request, state = self.oauth2_session.authorization_url(self.authUrl, self.STATE)
        print("Click on the following link below to log in and get an access code.")
        print("Once you retrieve it from the URL, update config.ini and run this script again.")
        print("")
        print(authorization_request)     

    def getAccessToken(self):
        """
            getAccessToken attempts to get a new accessToken by using the existing accessCode. If it fails due to accessCode being invalid or non-existant
            it updates the config file by blanking out the value of accessToken and it triggers the getAccessCode() method
        """

        try:
            token_response = self.oauth2_session.fetch_token( self.tokenUrl, code=self.accessCode, client_secret=self.clientSecret )
        except:
            self.updateConfig('AUTH','accesstoken', '') 
            self.getAccessCode()          
            exit()


        #check if accesstoken returned or some other error
        self.accessToken = token_response['access_token']
        self.updateConfig('AUTH','accessToken', self.accessToken)

        #if new refresh token returned, update config file
        if ( token_response['refresh_token'] ):
            print('we got a new refresh token')
            self.refreshToken = token_response['refresh_token']
            self.updateConfig('AUTH','refreshToken', self.refreshToken)      
        

    def updateConfig(self, configSection, configItemName, configItemValue):     
        #print('updating config -> configItemName: ' + configItemName + ' -> configItemValue: ' + configItemValue)               
        config[configSection][configItemName] = configItemValue
        with open('config.ini', 'w') as configfile:
            config.write(configfile)


    def getRefreshToken(self):
        """ 
            getRefreshToken attempts to get a new refreshToken. If it fails, due to it being invalid or non-existant, it blanks out the value on the 
            config file and it triggers the getAccessCode() method
        """
        try:
            token_response = self.oauth2_session.refresh_token(self.tokenUrl, refresh_token=self.refreshToken, auth=(self.clientID, self.clientSecret))
            self.accessToken = token_response['access_token']
            self.refreshToken = token_response['refresh_token']

            self.updateConfig('AUTH','accessToken', self.accessToken)
            self.updateConfig('AUTH','refreshToken', self.refreshToken) 
     
        except:
            self.updateConfig('AUTH','refreshToken', '') 
            self.getAccessCode()
            exit()
