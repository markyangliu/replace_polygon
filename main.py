import importlib
from replacepolygon import *
from intersectarea import *

def main(path):
    endpt = replacePoly(path)
    calcIntersectArea(endpt)


main('C:\input.txt')