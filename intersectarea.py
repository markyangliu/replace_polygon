import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from descartes import PolygonPatch
import math
from replacepolygon import Arc

def calcIntersectArea(poly1, poly2):
    '''
       :param poly1: list -> [x,y], poly2 contains arc objects
       :return: float -> proportion of intersecting area compared to poly1
                        interecting/poly1
    '''
    discPoly2 = []
    isClock = isClockwise(poly1)
    for coords in poly2:
        if isinstance(coords, Arc):
            updatedCoords = discretizeArc(coords, 1000)
            if isClock:
                list.reverse(updatedCoords)
            discPoly2 += updatedCoords
        else:
            discPoly2.append(coords)
    p1 = Polygon(poly1)
    p2 = Polygon(discPoly2)
    if p1.intersects(p2):
        inter_p = p1.intersection(p2)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.add_patch(PolygonPatch(inter_p, facecolor='g', edgecolor='g'))
        ax.add_patch(PolygonPatch(p1, facecolor='m', edgecolor='m', alpha = 0.25))
        ax.add_patch(PolygonPatch(p2, facecolor='r', edgecolor='r', alpha = 0.25))
        plt.axis([0,10,0,10])
        plt.show()
        return(inter_p.area / p1.area)

def discretizeArc(arc, numPoints):
    '''
    takes an Arc object and discretizes it into multiple coordinates
    :param endpt_val1, endpt_val2: [x, y] endpoints of arc
    :param center: [x,y] center of the arc
    :param radius: float -> radius of the arc
    :param numPoints: int -> num of points
    :return: [x,y] of points
    '''
    theta_inc = arc.theta / (numPoints-1)
    arc_points = []
    for i in range(numPoints):
        theta = arc.position[1] + (i * theta_inc)
        x_val = arc.position[0][0] + (math.cos(math.radians(theta)) * arc.roc)
        y_val = arc.position[0][1] + (math.sin(math.radians(theta)) * arc.roc)
        arc_points.append([x_val,y_val])
    return arc_points

def isClockwise(coordinates):
    '''
    :param poly: polygon defined by a list of coordinates [x,y]
    :return: True if polygon is defined by clockwise coordinates
             False if polygon is defined by counterclockwise coordinates
    '''
    sum = 0
    x_vals = [coordinates[i][0] for i in range(len(coordinates))]
    y_vals = [coordinates[i][1] for i in range(len(coordinates))]
    for i in range(len(x_vals) - 1):
        sum += x_vals[i] * y_vals[i + 1]
    sum += x_vals[-1] * y_vals[0]
    for i in range(len(y_vals) - 1):
        sum -= y_vals[i] * x_vals[i + 1]
    sum -= y_vals[-1] * x_vals[0]
    if sum < 0:
        return True
    else:
        return False
