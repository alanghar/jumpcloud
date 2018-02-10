from unittest import TestCase
import requests
import json
import base64
import random
import hashlib
import string
from helpers import start_server, stop_server

PORT = '8088'
BASEURL = r'http://localhost:%s' % PORT


class BaseServerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        start_server(PORT)

    @classmethod
    def tearDownClass(cls):
        stop_server()

    def get_jobid_url(self, jobid):
        return '/'.join([BASEURL, 'hash', str(jobid)])

    def get_pw_url(self):
        return '/'.join([BASEURL, 'hash'])

    def get_stats_url(self):
        return '/'.join([BASEURL, 'stats'])

    def get_shutdown_url(self):
        return self.get_pw_url()

    def try_pw(self, pw):
        url = self.get_pw_url()
        payload = json.dumps({"password": str(pw)})
        r = requests.post(url, data=payload)
        assert r.status_code == 200, "Password submission returned a non-200 status"
        try:
            return int(r.content)
        except:
            self.fail("Response is not numeric") 

    def try_jobid(self, jobid):
        url = self.get_jobid_url(jobid)
        r = requests.get(url)
        assert r.status_code == 200, "Job ID request returned a non-200 status"
        assert r.content.strip() != "", "Job ID request returned nothing"
        return r.content

    def try_shutdown(self):
        url = self.get_shutdown_url()
        payload = "shutdown"
        r = requests.post(url, data=payload)
        assert r.status_code == 200, "Shutdown request returned a non-200 status"
        assert r.content == "", "Shutdown request returned data (should be blank)"

    def get_stats(self):
        url = self.get_stats_url()
        r = requests.get(url)
        assert r.status_code == 200, "Stats request returned a non-200 status"
        assert r.content.strip() != "", "Status request returned nothing"
        try:
            return json.loads(r.content)
        except:
            self.fail("Invalid JSON result")

    def verify_jobid(self, jobid, expected_pw):
        resp = self.try_jobid(jobid)
        sha = hashlib.sha512(str(expected_pw)).digest()
        b64 = base64.b64encode(sha)
        assert resp == b64, "The server returned an incorrect Base64 string for password '%s'" % expected_pw
        return resp

    def verify_pw(self, pw):
        jobid = self.try_pw(pw)    
        return self.verify_jobid(jobid, pw)

    def seed_random(self, seed):
        random.seed(a=seed)

    def generate_random_password(self, length):
        return ''.join(random.choice(string.ascii_letters + string.punctuation + string.digits) for _ in range(length))

    def generate_n_random_passwords(self, n, length):
        return [self.generate_random_password(length) for x in xrange(n)]
