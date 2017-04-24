#!/usr/bin/env python
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
