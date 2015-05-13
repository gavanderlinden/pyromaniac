__author__ = 'tlinden'

from core import Core

c = Core()
for x in range(2):
    c.add_worker("test")
c.start()