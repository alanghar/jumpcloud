import logging
import os
import subprocess
import requests
import socket
import json
from BaseServerTest import BaseServerTest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

PORT = '8088'
BASEURL = r'http://localhost:%s' % PORT

class TestPasswordHash_Password(BaseServerTest):
    def try_pw(self, pw):
        url = '/'.join([BASEURL, 'hash'])
        payload = r'{"password": "%s"}' % pw
        r = requests.post(url, data=payload)
        self.assertEqual(r.status_code, 200)
        try:
            int(r.content)
        except:
            self.fail("Response is not numeric")        

    def test_empty_pw(self):
        self.try_pw("")

    def test_sqlinject_pw(self):
        self.try_pw("0 OR 1=1; --")
        self.try_pw("' OR 1=1; --")

    def test_regex_pw(self):
        self.try_pw(".")
        self.try_pw(".*")
        self.try_pw("*")

    def test_normal_pw(self):
        self.try_pw("afsl23!k78df6*@*34[]kxz")

    def test_reused_pw(self):
        self.try_pw("some password")
        self.try_pw("some password")

    def test_long_pw(self):
        self.try_pw("some password"*500)

    def test_unicode_pw(self):
        pass

    def test_binary_pw(self):
        pass

    def test_extended_pw(self):
        pass

    def test_sha512_pw(self):
        pass

    def test_jobid_as_pw(self):
        pass

    def test_hash_as_pw(self):
        pass

    def test_base64(self):
        pass

    def test_leading_spaces_pw(self):
        pass

    def test_trailing_spaces_pw(self):
        pass
