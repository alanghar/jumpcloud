import socket
from helpers import is_listening
from baseservertest import BaseServerTest, PORT


class TestPasswordHash_Ports(BaseServerTest):        
    def test_listening_port(self):
        if(not is_listening('localhost', PORT)):
            self.fail("Server is not listening on port %s" % PORT)

    def test_multiple_connections(self):
        socketlist = []
        for x in xrange(1000):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect(('localhost', int(PORT)))
                socketlist.append(s)
            except:
                self.fail("Could not open %s'th connection" % x)
        for s in socketlist:
            try:
                s.shutdown(2)
            except:
                pass