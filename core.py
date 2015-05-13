__author__ = 'Tones'

import Pyro4
import asyncio
import os
import random

from uuid import uuid4
from subprocess import Popen


class Core(object):

    def __init__(self):
        self.jobs = asyncio.Queue()
        self.workers = {}
        self.ns_void = open(os.devnull, "w")
        self.ns = Popen("python -m Pyro4.naming", stdout=self.ns_void, stderr=self.ns_void)

    def add_worker(self, func_name):
        id = uuid4().hex
        if not func_name in self.workers:
            self.workers[func_name] = asyncio.Queue()
        self.workers[func_name].put(id)
        Popen('python worker.py --name %s' % id)

    def get_worker(self, func):
        worker_name = yield from self.workers[func].get()
        return Pyro4.Proxy("PYRONAME:%s" % worker_name), worker_name

    @asyncio.coroutine
    def get_job(self):
        while True:
            job = yield from self.jobs.get()
            func = job["func"]
            text = job["text"]
            print("TEST", func, text)
            worker_name = yield from self.workers[func].get()
            print("WORKERNAME", worker_name)
            result = yield from Pyro4.Proxy("PYRONAME:%s" % worker_name).test(text)
            print("RESULT", worker_name, result)

    @asyncio.coroutine
    def add_job(self):
        while True:
            text = str(random.randint(1,1000))
            yield from self.jobs.put({"func": "test", "text": text})
            print("Added job: %s to queue" % text)
            yield from asyncio.sleep(random.randint(1,5))

    def start(self):
        asyncio.Task(self.add_job())
        asyncio.Task(self.get_job())
        loop = asyncio.get_event_loop()
        loop.run_forever()

