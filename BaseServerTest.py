from unittest import TestCase
import base64
import hashlib
import json
import logging
import os
import random
import requests
import socket
import string
import subprocess
import time
import datetime
import psutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

PORT = '8088'
BASEURL = r'http://localhost:%s' % PORT


class BaseServerTest(TestCase):
    def setUp(self):
        self.server_process = None
        self.restart_server(PORT)
        self.seed_random(0)

    def tearDown(self):
        self.stop_server()

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

    def verify_server_terminated(self):
        """
        Verifies that the server process terminated.
        """
        if(self.server_process):
            start_time = datetime.datetime.now()
            while(datetime.datetime.now() - start_time < datetime.timedelta(seconds=5)):
                if(psutil.pid_exists(self.server_process.pid) is False):
                    break
                time.sleep(0.1)
            assert psutil.pid_exists(self.server_process.pid) == False, "Server process still exists 5 seconds after shutdown."

    def start_server(self, port):
        if(self.is_listening('localhost', port)):
            raise Exception("Port %s is occupied" % port)

        env = os.environ.copy()
        env['PORT'] = port
        server_exe = {'posix': 'broken-hashserve_linux',
                      'nt': 'broken-hashserve_win.exe'}[os.name]
        self.server_process = subprocess.Popen(['../server/%s' % server_exe], env=env)
        logger.info("Spawned server process %s" % self.server_process.pid)
        time.sleep(0.5)  # Sometimes the server needs some time to initialize and open the port

    def stop_server(self):
        if(self.server_process and self.server_process.poll() is None):
            logger.info("Killing server process %s" % self.server_process.pid)
            try:
                self.server_process.kill()
            except:
                pass
            self.server_process.wait()
            self.server_process = None

    def restart_server(self, port):
        self.stop_server()
        time.sleep(1)  # I had some issues with the port not being release soon enough
        self.start_server(port)

    def is_listening(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((str(host), int(port)))
            s.shutdown(2)
            return True
        except:
            return False
