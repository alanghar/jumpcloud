from unittest import TestCase
import pprint
import logging
import os
import subprocess
import requests
import grequests
import socket
import json
from baseservertest import BaseServerTest
from test_passwordhash_password import HASH_WAIT_TIME_SEC
from helpers import restart_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class TestPasswordHash_Stats(BaseServerTest):
    def test_initial_stats(self):
        restart_server()
        stats = self.get_stats()
        self.assertEqual(stats['AverageTime'], 0)
        self.assertEqual(stats['TotalRequests'], 0)

    def test_simple_request_increment(self):
        self.seed_random(0)
        initial_stats = self.get_stats()
        pw = self.generate_random_password(20)
        self.try_pw(pw)
        new_stats = self.get_stats()
        self.assertEqual(new_stats['TotalRequests'], initial_stats['TotalRequests'] + 1)
        assert new_stats['AverageTime'] >= HASH_WAIT_TIME_SEC

    def test_concurrent_increment(self):        
        self.seed_random(0)
        initial_stats = self.get_stats()
        rand_pws = self.generate_n_random_passwords(50, 20)
        url = self.get_pw_url()
        async_requests = (grequests.post(url, data=json.dumps({"password": str(pw)})) for pw in rand_pws)
        async_results = [int(x.content) for x in grequests.map(async_requests)]
        new_stats = self.get_stats()
        self.assertEqual(new_stats['TotalRequests'], initial_stats['TotalRequests'] + 50)
        assert new_stats['AverageTime'] >= HASH_WAIT_TIME_SEC
        
