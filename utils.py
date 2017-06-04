#!/usr/bin/env python
import heapq

# Because the normal python one is broken...
# Adapted From: https://www.safaribooksonline.com/library/view/python-cookbook-3rd/9781449357337/ch01s05.html
class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._index = 0

    def push(self, item, priority):
        heapq.heappush(self._queue, (priority, self._index, item))
        self._index += 1

    def pop(self):
        return heapq.heappop(self._queue)[-1]

    def empty(self):
        return len(self._queue) == 0


def colourise(colour, string):
    if colour is None:
        colour = ''
    elif colour.lower() == "blue":
        colour = '\033[94m'
    elif colour.lower() == "green":
        colour = '\033[92m'
    elif colour.lower() == "yellow":
        colour = '\033[93m'
    elif colour.lower() == "red":
        colour = '\033[91m'

    output = ""
    for line in string.split('\n'):
        output += colour + line + '\033[0m\n'
    return output[:-1]
