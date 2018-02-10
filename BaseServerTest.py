from unittest import TestCase
import logging
import os
import subprocess
import requests
import socket
import json
import base64
import random
import hashlib
import datetime
import string
from helpers import start_server, stop_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

PORT = '8088'
BASEURL = r'http://localhost:%s' % PORT

PASSWORD = r"some random password 0123456789 ~!@#$%^&*()_[]{}?/.,<>;':"
SHA512HASH = hashlib.sha512(PASSWORD).digest()
B64ENCODED = base64.b64encode(SHA512HASH)

class BaseServerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        logger.info("setUpClass() called")
        start_server(cls)

    @classmethod
    def tearDownClass(cls):
        logger.info("tearDownClass() called")
        stop_server(cls)

    def get_jobid_url(self, jobid):
        return '/'.join([BASEURL, 'hash', str(jobid)])

    def get_pw_url(self):
        return '/'.join([BASEURL, 'hash'])

    def try_pw(self, pw):
        url = self.get_pw_url()
        payload = json.dumps({"password": str(pw)})
        r = requests.post(url, data=payload)
        self.assertEqual(r.status_code, 200)
        try:
            return int(r.content)
        except:
            self.fail("Response is not numeric") 

    def try_jobid(self, jobid):
        url = self.get_jobid_url(jobid)
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertNotEqual(r.content.strip(), "")
        return r.content

    def verify_jobid(self, jobid, expected_pw):
        resp = self.try_jobid(jobid)
        sha = hashlib.sha512(str(expected_pw)).digest()
        b64 = base64.b64encode(sha)
        self.assertEquals(resp, b64)
        return resp

    def verify_pw(self, pw):
        jobid = self.try_pw(pw)    
        return verify_jobid(jobid, pw)

    def seed_random(self, seed):
        random.seed(a=seed)

    def generate_random_password(self, length):
        return ''.join(random.choice(string.ascii_letters + string.punctuation + string.digits) for _ in range(length))

    def generate_n_random_passwords(self, n, length):
        return [self.generate_random_password(length) for x in xrange(n)]
