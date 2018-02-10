from unittest import TestCase
import logging
import os
import subprocess
import requests
import socket
import json
from helpers import start_server, stop_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

PORT = '8088'

class BaseServerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        logger.info("setUpClass() called")
        start_server(cls)

    @classmethod
    def tearDownClass(cls):
        logger.info("tearDownClass() called")
        stop_server(cls)
        
    def try_pw(self, pw):
        url = '/'.join([BASEURL, 'hash'])
        payload = r'{"password": "%s"}' % pw
        r = requests.post(url, data=payload)
        self.assertEqual(r.status_code, 200)
        try:
            int(r.content)
        except:
            self.fail("Response is not numeric") 