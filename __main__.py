import requests
import pickle
from datetime import datetime, timedelta
import logging
import random, string

authFile = '/Users/adrea/.auth.pickle'
bibFile = '/Users/adrea/library.bib'

class TokenClass:
    def __init__(self):
        logging.info('Token: token doesn\'t exist, new token being generated')
        self.client_id = '12055'
        self.client_secret = '1ng4LkgZhc8pR2Id'
        self.redirect_uri = "http://localhost:5000/oauth"
        self.scope = 'all'
        self.authorize_url = "https://api.mendeley.com/oauth/authorize"
        self.token_url = "https://api.mendeley.com/oauth/token"
        self.token = ''
        self.state = ''
        if self.token == '':
            self.getNewOAuthToken()

    def pickleSelf(self):
        logging.info('Token: saving token to file')
        with open(authFile, 'wb') as f:
            pickle.dump(self, f)

    def generateState(self):
        self.state = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    def getNewOAuthToken(self):
        logging.info('Token: grabbing new token')
        self.generateState()
        authorization_url = f'{self.authorize_url}?response_type=code&client_id={self.client_id}&redirect_uri={requests.utils.quote(self.redirect_uri)}&scope={self.scope}&state={self.state}'
        print( f'Please go to {authorization_url} to authorize access, and copy the final localhost URL')
        authorization_response = input("Response: ").split('http://localhost:5000/oauth?code=')
        if authorization_response[1].split('&state=')[1] != self.state:
            logging.arror('Token: CSRF detected, aborting')
            exit()
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        data = f'grant_type=authorization_code&code={authorization_response[1]}&redirect_uri={self.redirect_uri}'
        token = requests.post(self.token_url, data=data, auth=(self.client_id, self.client_secret), headers=headers)
        self.token = token.json()['access_token']
        self.refresh = token.json()['refresh_token']
        self.expire = datetime.now() + timedelta(seconds=token.json()['expires_in']) 
        self.pickleSelf()

    def refreshOAuthToken(self):
        logging.info('Token: refreshing token')
        self.generateState()
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        data = f'grant_type=refresh_token&refresh_token={self.refresh}&redirect_uri={self.redirect_uri}'
        token = requests.post(self.token_url, data=data, auth=(self.client_id, self.client_secret), headers=headers)
        self.token = token.json()['access_token']
        self.refresh = token.json()['refresh_token']
        self.expire = datetime.now() + timedelta(seconds=token.json()['expires_in'])
        self.pickleSelf()
        
    def checkToken(self):
        if self.expire < datetime.now():
            logging.info('Token: token is out of date and being refreshed')
            self.refreshOAuthToken()
        else:
            logging.info('Token: token is up to date')

def tokenHandler():
    try:
        with open(authFile, 'rb') as f:
            Token = pickle.load(f)
            logging.info('Token: token is being read from file')
            Token.checkToken()
    except:
        Token = TokenClass()
    return(Token)

logging.basicConfig(format='%(levelname)s:%(message)s', level='INFO')

Token = tokenHandler()

headers = {'Authorization': f'Bearer {Token.token}', 'Content-type': 'application/vnd.mendeley-document-summary+json'}
response = requests.get('https://api.mendeley.com/documents?limit=500', timeout=30, headers=headers)
entries = len(response.json())
if entries < 500:
    logging.info(f'Parser: fewer than 500 refs means I can one-shot this list')
    headers = {'Authorization': f'Bearer {Token.token}', 'accept': 'application/x-bibtex'}
    response = requests.get(f'https://api.mendeley.com/documents?limit=500', timeout=30, headers=headers)
    bibtexString = response.text
else:
    logging.info(f'Parser: 500 or more refs means that I have to go folder-by-folder')
    citationList = []
    bibtexString = ''
    headers = {'Authorization': f'Bearer {Token.token}', 'Content-type': 'application/vnd.mendeley-document-summary+json'}
    response = requests.get('https://api.mendeley.com/folders', timeout=30, headers=headers)
    for folder in response.json():
        folderID = folder['id']
        logging.info(f'Parser: Processing folder {folderID}')
        headers = {'Authorization': f'Bearer {Token.token}', 'accept': 'application/x-bibtex'}
        response = requests.get(f'https://api.mendeley.com/documents?folder_id={folderID}&limit=500', timeout=30, headers=headers)
        if response.text != '':
            splittext = response.text.split('\n\n')
            for entry in splittext:
                entryID = entry.split('{')[1].split(',')[0]
                logging.info(f'Parser: Processing entry {entryID}')
                if entryID not in citationList:
                    citationList += [entryID]
                    bibtexString += f'{entry}\n\n'

with open(bibFile, 'w') as f:
    f.write(bibtexString)
