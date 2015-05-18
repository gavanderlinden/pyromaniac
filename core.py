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
        self.worker_pool = {}
        self.ns_void = open(os.devnull, "w")
        self.ns = Popen("python -m Pyro4.naming", stdout=self.ns_void, stderr=self.ns_void)

    def add_worker(self, func_name):
        id = uuid4().hex
        if not func_name in self.worker_pool:
            self.worker_pool[func_name] = []
        self.worker_pool[func_name].append(id)
        Popen('python worker.py --name %s' % id)

    def get_worker(self, func):
        worker_name = yield from self.workers[func].get()
        return Pyro4.Proxy("PYRONAME:%s" % worker_name), worker_name

    @asyncio.coroutine
    def get_job(self):
        while True:
            job = yield from self.jobs.get()
            job_name = job["func"]
            job_text = job["text"]
            print("JOB", job)
            worker = yield from self.workers[job_name].get()
            print("WORKER", worker)
            _proxy = Pyro4.Proxy("PYRONAME:%s" % worker)
            deferred_proxy = proxy.PyroDeferredService(_proxy)
            result = deferred_proxy.test(job_text)
            print("RESULT", result)
            yield from self.workers[job_name].put(worker)

    @asyncio.coroutine
    def add_job(self):
        while True:
            print("NUMBER OF JOBS", self.jobs.qsize())
            text = str(random.randint(1,1000))
            yield from self.jobs.put({"func": "test", "text": text})
            print("Added job: %s to queue" % text)
            yield from asyncio.sleep(0.5)

    @asyncio.coroutine
    def load_pool(self):
        for func_name in self.worker_pool:
            if not func_name in self.workers:
                self.workers[func_name] = asyncio.Queue()
            for worker_name in self.worker_pool[func_name]:
                yield from self.workers[func_name].put(worker_name)

    def start(self):
        asyncio.Task(self.load_pool())
        asyncio.Task(self.get_job())
        asyncio.Task(self.add_job())
        loop = asyncio.get_event_loop()
        loop.run_forever()

