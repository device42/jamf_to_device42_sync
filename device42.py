import requests
import base64


class Device42Api:
    def __init__(self, config, options):
        self.username = config['username']
        self.password = config['password']
        self.domain = config['domain']
        self.protocol = config['protocol']
        self.debug = options['debug']
        self.dry_run = options['dry_run']

    def _poster(self, data, url):
        payload = data
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(self.username + ':' + self.password),
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        r = requests.post(url, data=payload, headers=headers, verify=False)
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

    # POST
    def post(self, data, name):
        url = '%s://%s/api/1.0/%s/' % (self.protocol, self.domain, name)
        msg = '\tPost request to %s' % url
        if not self.dry_run:
            print msg
        r = self._poster(data, url)
        return r.json() if r is not None else None

    def post_sub(self, data, name, name2):
        url = '%s://%s/api/1.0/%s/%s' % (self.protocol, self.domain, name, name2)
        msg = '\tPost request to %s' % url
        if not self.dry_run:
            print msg
        r = self._poster(data, url)
        return r.json() if r is not None else None

    # GET
    def get_list(self, data, name):
        url = '%s://%s/api/1.0/%s/' % (self.protocol, self.domain, name)
        msg = '\tGet request to %s ' % url
        if not self.dry_run:
            print msg
        return self._getter(data, url).json()

    # DELETE
    def delete(self, identity, name):
        url = '%s://%s/api/1.0/%s/%s' % (self.protocol, self.domain, name, identity)
        msg = '\tDelete request to %s ' % url
        if not self.dry_run:
            print msg
        return self._deleter(url).json()


