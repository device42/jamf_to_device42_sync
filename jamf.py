import requests
import xmltodict


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

    def insert_computer(self):
        xml = '''
                <computer>
                    <general>
                        a<name>test</name>
                    </general>
                </computer>
              '''
        return requests.post('https://%s/JSSResource/computers/id/0' % self.domain, xml,
                             auth=self.auth, headers=self.headers).text

    def insert_mobile_devices(self):
        xml = '''
                <mobile_device>
                    <general>
                        <name>test</name>
                        <udid>12345</udid>
                        <serial_number>12345</serial_number>
                    </general>
                </mobile_device>
              '''
        return requests.post('https://%s/JSSResource/mobiledevices/id/0' % self.domain, xml,
                             auth=self.auth, headers=self.headers).text

    def insert_licensed_software(self):
        xml = '''
                <licensed_software>
                    <computers>
                        <id>1</id>
                    </computers>
                    <general>
                        <name>test222</name>
                    </general>
                </licensed_software>
              '''
        return requests.post('https://%s/JSSResource/licensedsoftware/id/0' % self.domain, xml,
                             auth=self.auth, headers=self.headers).text
