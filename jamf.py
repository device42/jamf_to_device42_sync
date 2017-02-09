import requests


class JamfApi:

    def __init__(self, config, options):
        self.auth = (config['username'], config['password'])
        self.domain = config['domain']
        self.debug = options['debug']
        self.headers = {
            'Content-Type': 'text/xml',
            'Accept': 'application/json'
        }

    def get_list(self, name):
        return requests.get('https://%s/JSSResource/%s' % (self.domain, name),
                            auth=self.auth, headers=self.headers).json()

    def get_item(self, name, pk):
        return requests.get('https://%s/JSSResource/%s/id/%s' % (self.domain, name, pk),
                            auth=self.auth, headers=self.headers).json()