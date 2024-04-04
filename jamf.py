import requests
from datetime import datetime, timedelta


class JamfApi:

    def __init__(self, config, options):
        self.auth = (config['username'], config['password'])
        self.host = config['host']
        self.debug = options['debug']
        self.headers = {
            'Content-Type': 'text/xml',
            'Accept': 'application/json'
        }
        self.token = None
        self.token_expiration = None

    def get_list(self, name):
        return requests.get('https://%s/JSSResource/%s' % (self.host, name), headers=self._get_headers()).json()

    def get_item(self, name, pk):
        return requests.get('https://%s/JSSResource/%s/id/%s' % (self.host, name, pk), headers=self._get_headers()).json()

    def _get_token(self):
        # Get a token if we don't have one yet or the token is expired.
        # We will renew the token 30 seconds before the token expires in order to avoid the token expiring
        # before we make the next Jamf API call.
        if self.token is None or (self.token_expiration - timedelta(seconds=30)) <= datetime.utcnow():
            response = requests.post('https://%s/api/v1/auth/token' % self.host, auth=self.auth, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                self.token = data['token']
                self.token_expiration = datetime.strptime(data['expires'], '%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                self.token = None
                self.token_expiration = None
                if self.debug:
                    print('Failed to get token. status code = %d, body = %s' % (response.status_code, response.text))

    def _get_headers(self):
        headers = dict(self.headers)
        self._get_token()
        headers['Authorization'] = 'Bearer %s' % self.token
        return headers
