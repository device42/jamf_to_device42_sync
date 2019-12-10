import requests
import base64
import json


class Device42Api:
    def __init__(self, config, options):
        self.username = config['username']
        self.password = config['password']
        self.host = config['host']
        self.debug = options['debug']
        self.dry_run = options['dry_run']

    def _poster(self, data, url):
        payload = data
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(self.username + ':' + self.password)
        }

        r = requests.post(url, payload, headers=headers, verify=False)
        if self.debug:
            msg1 = unicode(payload)
            msg2 = 'Status code: %s' % str(r.status_code)
            msg3 = str(r.text)

            print '\n\t----------- POST FUNCTION -----------'
            print '\t' + msg1
            print '\t' + msg2
            print '\t' + msg3
            print '\t------- END OF POST FUNCTION -------\n'

        return r

    def _put(self, data, url):
        payload = data
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(self.username + ':' + self.password)
        }

        r = requests.put(url=url, data=payload, headers=headers, verify=False)

        if self.debug:
            msg1 = unicode(payload)
            msg2 = 'Status code: %s' % str(r.status_code)
            msg3 = str(r.text)

            print '\n\t----------- PUT FUNCTION -----------'
            print '\t' + msg1
            print '\t' + msg2
            print '\t' + msg3
            print '\t------- END OF PUT FUNCTION -------\n'

        return r

    def _getter(self, data, url):
        params = data
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(self.username + ':' + self.password),
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        r = requests.get(url, params=params, headers=headers, verify=False)
        if self.debug:
            msg1 = unicode(params)
            msg2 = 'Status code: %s' % str(r.status_code)
            msg3 = str(r.text)

            print '\n\t----------- GET FUNCTION -----------'
            print '\t' + msg1
            print '\t' + msg2
            print '\t' + msg3
            print '\t------- END OF GET FUNCTION -------\n'

        return r

    def _deleter(self, url):
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(self.username + ':' + self.password),
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        r = requests.delete(url, headers=headers, verify=False)
        if self.debug:
            msg1 = 'Status code: %s' % str(r.status_code)
            msg2 = str(r.text)

            print '\n\t----------- DELETE FUNCTION -----------'
            print '\t' + msg1
            print '\t' + msg2
            print '\t------- END OF DELETE FUNCTION -------\n'

        return r

    # GET
    def get_list(self, data, name):
        url = 'https://%s/api/1.0/%s/' % (self.host, name)
        msg = '\tGet request to %s ' % url
        if not self.dry_run:
            print msg
        return self._getter(data, url).json()

    # DELETE
    def delete(self, identity, name):
        url = 'https://%s/api/1.0/%s/%s' % (self.host, name, identity)
        msg = '\tDelete request to %s ' % url
        if not self.dry_run:
            print msg
        return self._deleter(url).json()

    # BULK
    def bulk(self, data):
        url = 'https://%s/api/1.0/devices/bulk/' % self.host
        msg = '\tBulk request to %s ' % url
        if not self.dry_run:
            print msg
        return self._poster({'payload': json.dumps(data)}, url).json()

    # POST - END USER
    def post_enduser(self, data): 
        url ='https://%s/api/1.0/endusers/' %self.host
        return self._poster(data, url).json()

    # POST - BUILDING
    def post_building(self, data):
        url ='https://%s/api/1.0/buildings/' %self.host
        return self._poster(data, url).json()

    # PUT - END USER CUSTOM FIELDS
    def put_enduserCF(self, data):
        url ='https://%s/api/1.0/custom_fields/endusers/' %self.host
        return self._put(data, url).json()

    # PUT - DEVICE CUSTOM FIELDS
    def put_deviceCF(self, data):
        url ='https://%s/api/1.0/device/custom_field/' %self.host
        return self._put(data, url).json()


