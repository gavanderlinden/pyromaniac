__author__ = 'tlinden'

from core import Core

c = Core()
for x in range(4):
    c.add_worker("test")
c.start()