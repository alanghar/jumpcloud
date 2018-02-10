from unittest import TestCase
import logging
import os
import subprocess
import requests
import socket
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

PORT = '8088'


###################################################
#
#
#                Helper Functions
#       
#
###################################################

def start_server(cls):        
    if(is_listening('localhost', PORT)):
        raise Exception("Port %s is occupied" % PORT)

    env = os.environ.copy()
    env['PORT'] = PORT
    server_exe = {'posix': 'broken-hashserve_linux',
                  'nt': 'broken-hashserve_win.exe'}[os.name]
    cls.server_process = subprocess.Popen(['../server/%s' % server_exe], env=env)
    logger.info("Spawned server process %s" % cls.server_process.pid)

def stop_server(cls):    
    if(cls.server_process):
        logger.info("Killing server process %s" % cls.server_process.pid)
        cls.server_process.kill()

def is_listening(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((str(host), int(port)))
        s.shutdown(2)
        return True
    except:
        return False


###################################################
#
#
#                Test Definitions
#       
#
###################################################

class BaseServerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        logger.info("setUpClass() called")
        start_server(cls)

    @classmethod
    def tearDownClass(cls):
        logger.info("tearDownClass() called")
        stop_server(cls)


class TestPasswordHash_Ports(BaseServerTest):        
    def test_ports_1(self):
        logger.info("Testing test_ports_1()")

        if(not is_listening('localhost', PORT)):
            self.fail("Server is not listening on port %s" % PORT)




class TestPasswordHash_Stats(BaseServerTest):
    pass

class TestPasswordHash_JobID(BaseServerTest):
    pass

class TestPasswordHash_Shutdown(BaseServerTest):
    pass

