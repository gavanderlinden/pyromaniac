__author__ = 'Tones'

import Pyro4
import os

from uuid import uuid4
from subprocess import Popen


class Core(object):

    def __init__(self):
        self.workers = {}
        self.ns_void = open(os.devnull, "w")
        self.ns = Popen("python -m Pyro4.naming", stdout=self.ns_void, stderr=self.ns_void)

    def add_worker(self, func_name):
        id = uuid4()
        self.workers[func_name] = id
        Popen('python worker.py --name %s' % id)

    def invoke(self, func):
        worker_name = self.workers[func]
        return Pyro4.Proxy("PYRONAME:%s" % worker_name)
