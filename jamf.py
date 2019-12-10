import requests
import json

class JamfApi:

    def __init__(self, config, options):
        self.auth = (config['username'], config['password'])
        self.host = config['host']
        self.debug = options['debug']
        self.headers = {
            'Content-Type': 'text/xml',
            'accept': 'application/json'
        }

    def get_list(self, name):
        return requests.get('https://%s/JSSResource/%s' % (self.host, name), 
                            auth = self.auth, 
                            headers=self.headers 
                            #verify = False
                            ).json()

    def get_item(self, name, pk):
        return requests.get('https://%s/JSSResource/%s/id/%s' % (self.host, name, pk), 
                            auth = self.auth, 
                            headers=self.headers 
                            #verify = False
                            ).json()
