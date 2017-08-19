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

def enable_colours(value):
    global SHOW_COLOURS
    SHOW_COLOURS = value


def colourise(colour, string):
    global SHOW_COLOURS
    if SHOW_COLOURS:
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
    else:
        colour = ''

    output = ""
    newline = '\033[0m\n' if SHOW_COLOURS else '\n'
    for line in string.split('\n'):
        output += colour + line + newline
    return output[:-1]

def checked_input(message, check, convert=None):
    if convert is None:
        convert = lambda x: x
    while True:
        output = input(message)
        try:
            if check(convert(output)):
                return convert(output)
        except ValueError:
            pass
        print("{} is invalid".format(output))
