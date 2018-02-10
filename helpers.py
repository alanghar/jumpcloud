import logging
import os
import time
import subprocess
import socket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

server_process = None

###################################################
#
#
#                Helper Functions
#       
#
###################################################

def start_server(port):  
    global server_process      
    if(is_listening('localhost', port)):
        raise Exception("Port %s is occupied" % port)

    env = os.environ.copy()
    env['PORT'] = port
    server_exe = {'posix': 'broken-hashserve_linux',
                  'nt': 'broken-hashserve_win.exe'}[os.name]
    server_process = subprocess.Popen(['../server/%s' % server_exe], env=env)
    logger.info("Spawned server process %s" % server_process.pid)
    time.sleep(0.5)  # Sometimes the server needs some time to initialize and open the port

def stop_server():    
    global server_process      
    if(server_process and server_process.poll() is None):
        logger.info("Killing server process %s" % server_process.pid)
        try:
            server_process.kill()
        except:
            pass
        server_process.wait()
        server_process = None

def restart_server(port):
    stop_server()
    time.sleep(1)  # I had some issues with the port not being release soon enough
    start_server(port)

def is_listening(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((str(host), int(port)))
        s.shutdown(2)
        return True
    except:
        return False