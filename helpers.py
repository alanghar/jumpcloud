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