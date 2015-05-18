__author__ = 'Tones'

import Pyro4
from optparse import OptionParser
import time

class Server(object):

    def __init__(self):
        pass

    def test(text):
        time.sleep(6)
        return text + text

def main(daemon_name):
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(Server)
    ns.register(daemon_name, uri)
    daemon.requestLoop()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-n", "--name", dest="daemon_name")
    options, args = parser.parse_args()
    main(options.__dict__.get("daemon_name"))