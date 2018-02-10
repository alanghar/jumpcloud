from unittest import TestCase
import logging
import os
import time
import subprocess
import requests
import socket
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

PORT = '8088'

server_process = None

###################################################
#
#
#                Helper Functions
#       
#
###################################################

def start_server():  
    global server_process      
    if(is_listening('localhost', PORT)):
        raise Exception("Port %s is occupied" % PORT)

    env = os.environ.copy()
    env['PORT'] = PORT
    server_exe = {'posix': 'broken-hashserve_linux',
                  'nt': 'broken-hashserve_win.exe'}[os.name]
    server_process = subprocess.Popen(['../server/%s' % server_exe], env=env)
    logger.info("Spawned server process %s" % server_process.pid)

def stop_server():    
    global server_process      
    if(server_process):
        logger.info("Killing server process %s" % server_process.pid)
        server_process.kill()
        server_process = None

def restart_server():
    stop_server()
    time.sleep(1)  # I had some issues with the port not being release soon enough
    start_server()

def is_listening(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((str(host), int(port)))
        s.shutdown(2)
        return True
    except:
        return False