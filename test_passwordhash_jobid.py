from unittest import TestCase
import logging
import os
import subprocess
import requests
import socket
import json
import base64
import hashlib
from baseservertest import BaseServerTest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class TestPasswordHash_JobID(BaseServerTest):
    def test_alpha_nonexistent_jobid(self):
        url = self.get_jobid_url("nonexistent")
        r = requests.get(url)
        self.assertEqual(r.status_code, 400)

    def test_integer_nonexistent_jobid(self):
        url = self.get_jobid_url("1234567890")
        r = requests.get(url)
        self.assertEqual(r.status_code, 400)

    def test_neginteger_nonexistent_jobid(self):
        url = self.get_jobid_url("-1234567890")
        r = requests.get(url)
        self.assertEqual(r.status_code, 400)

    def test_float_nonexistent_jobid(self):
        url = self.get_jobid_url("123.456789")
        r = requests.get(url)
        self.assertEqual(r.status_code, 400)

    def test_blank_jobid(self):
        url = self.get_jobid_url("")
        r = requests.get(url)
        self.assertEqual(r.status_code, 400)

    def test_space_jobid(self):
        url = self.get_jobid_url(" ")
        r = requests.get(url)
        self.assertEqual(r.status_code, 400)
