import matplotlib.pyplot as plt
from matplotlib.patches import Arc as plotArc
import numpy as np
from graphutil import *
import math
from replacepolygon import Arc

def calcIntersectArea(poly1, poly2):
    '''
    :param poly1: list -> [x,y], poly2 can also contain arc objects
    :return: float -> percentage of intersecting area compared to poly1
    '''
    discPoly2 = []
    for coords in poly2:
        if isinstance(coords, Arc):
            updatedCoords = discretizeArc(coords)
            discPoly2 += updatedCoords
        else:
            discPoly2.append(coords)
    x1 = []
    y1 = []
    for coord in poly1:
        x1.append(coord[0])
        y1.append(coord[1])
    x2 = []
    y2 = []
    for coord in discPoly2:
        x2.append(coord[0])
        y2.append(coord[1])
    inter_p = calcIntersectingPoints(x1,y1,x2,y2)
    print(inter_p)
    plt.plot([p1[i][0] for i in range(-1, len(p1))], [p1[i][1] for i in range(-1, len(p2))])
    plt.plot([p2[i][0] for i in range(-1, len(p1))], [p2[i][1] for i in range(-1, len(p2))])
    plt.plot([inter_p[i][0] for i in range(-1, len(inter_p))], [inter_p[i][1] for i in range(-1, len(inter_p))])
    plt.show()
    if len(inter_p) == 0: #if no intersections
        return 0
    else:
        inter_area = shoelaceArea(inter_p)
    #area of first polygon
    poly_area = shoelaceArea(poly1)
    return inter_area / poly_area

def calcIntersectingPoints(x1,y1,x2,y2):
    '''
    Calculates the intersecting points between the two polygons
    :param x1,x2,y1,y2: list -> contains x and y values for polygons 1 and 2
    :return: inter_p: list -> contains all intersecting points [x,y]
    '''
    inter_p = []
    lastSegIntersect = False
    lastPointInterior = False
    for j in range(len(x2)):
        if pointWithinPoly([[x1[k], y1[k]] for k in range(len(x1))], x2[j], y2[j]):
            inter_p.append([x2[j], y2[j]])
        for i in range(len(x1)):
            # intersection between two lines
            try:
                #print([[x1[i], y1[i]], [x1[(i + 1) % len(x1)], y1[(i + 1) % len(y1)]]],
                 #     [[x2[j], y2[j]], [x2[(j + 1) % len(x2)], y2[(j + 1) % len(y2)]]])
                temp_inter = calcIntersectSeg([[x1[i], y1[i]], [x1[(i + 1) % len(x1)], y1[(i + 1) % len(y1)]]],
                                            [[x2[j], y2[j]], [x2[(j + 1) % len(x2)], y2[(j + 1) % len(y2)]]])
                #print('success:', temp_inter)
                lastSegIntersect = True
                lastPointInterior = False
                for coord in temp_inter:
                    if coord in inter_p:
                        inter_p.remove(coord)
                    inter_p.append(coord)
            except:
                pass
                '''
                if (lastSegIntersect and pointWithinPoly([[x1[k],y1[k]] for k in range(len(x1))], x2[j],y2[j])) \
                or (lastPointInterior and not lastSegIntersect and 1==2):
                        print('inside:',x1[i], y1[i], ',', x2[j], y2[j])
                        inter_p.append([x2[j], y2[j]])
                        lastPointInterior = True
                else:
                    lastPointInterior = False
                lastSegIntersect = False
                '''

    return inter_p

def discretizeArc(arc, numPoints):
    '''
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
        arc_points.append(x_val,y_val)
    return arc_points


def pointWithinPoly(poly, p_x, p_y):
    '''
    Checks if the point lies in the interior of the polygon using ray casting
    :param poly: list -> [x,y] contains all the x and y coordinates of polygon
    :param p_x, p_y: coordinate of point
    :return: True
    '''
    past_inter = []
    numInter = 0
    for i in range(len(poly)):
        poly_seg = [[poly[i][0], poly[i][1]], [poly[(i+1) % len(poly)][0], poly[(i+1) % len(poly)][1]]]
        x_range, y_range = calcSegRange(poly_seg)
        try:
            inter_pt = calcLinLineIntersect([[p_x,p_y], [p_x + 1, p_y]], poly_seg)
            if (x_range[0] <= inter_pt[0] <= x_range[1]) and (y_range[0] <= inter_pt[1] <= y_range[1]) and (inter_pt[0] >= p_x):
                if inter_pt in past_inter:
                    if ((poly_seg[1][1] > inter_pt[1] and poly[i-1][1] > inter_pt[1])
                        or (poly_seg[1][1] < inter_pt[1] and poly[i-1][1] < inter_pt[1])):
                        numInter += 1
                else:
                    past_inter.append(inter_pt)
                    numInter += 1
        except:
            pass
    if (numInter % 2 == 0):
        return False
    else:
        return True


def calcIntersectSeg(seg1, seg2):
    '''
    Calculates if two line segments intersect
    :param seg1: list -> [pt1, pt2]
    :return: False if no intersection, list of intersections [x,y] if intersect
    '''
    try:
        #ranges represent segments
        x_range1, y_range1 = calcSegRange(seg1)
        x_range2, y_range2 = calcSegRange(seg2)
        #represents shared segment
        x_range = calcSharedRange(x_range1, x_range2)
        y_range = calcSharedRange(y_range1, y_range2)
        inter_pt = calcLinLineIntersect(seg1, seg2)
        if not x_range  or not y_range:
            raise NoIntersectionException
        else:
            #intersection is within range of segment
            if (x_range[0] <= inter_pt[0] <= x_range[1]) and (y_range[0] <= inter_pt[1] <= y_range[1]):
                return [inter_pt]
            else:
                raise NoIntersectionException
    except(NoIntersectionException):  # if the extended lines don't intersect
        raise NoIntersectionException
    except(AllPointsIntersectException):
        return [[x_range[1], y_range[1]], [x_range[0], y_range[0]]]

def calcSegRange(seg):
    '''
    Calculates the x and y ranges of the segment
    :param seg: list -> [pt1, pt2]
    :return: list, list -> [x_min, x_max], [y_min, y_max]
    '''
    x_range = [min(seg[0][0], seg[1][0]), max(seg[0][0], seg[1][0])]
    y_range = [min(seg[0][1], seg[1][1]), max(seg[0][1], seg[1][1])]
    return x_range, y_range

def calcSharedRange(range1, range2):
    '''
    Calculates the shared range of two ranges
    :param range1: list -> [min, max]
    :return: list -> [min, max]
    '''
    #no shared range
    if range1[0] > range2[1] or range2[0] > range1[1]:
        return False
    else:
        return [max(range1[0], range2[0]), min(range1[1],range2[1])]

def shoelaceArea(coordinates):
    '''
    calculates the area of a polygon given x and y coordinates using the Shoelace Theorem
    :param x_vals: list -> x coordinates of polygon
    :param y_vals: list -> y coordinates of polygon
    :return: area of polygon
    '''
    sum = 0
    x_vals = [coordinates[i][0] for i in range(len(coordinates))]
    y_vals = [coordinates[i][1] for i in range(len(coordinates))]
    for i in range(len(x_vals) - 1):
        sum += x_vals[i] * y_vals[i+1]
    sum += x_vals[-1] * y_vals[0]
    for i in range(len(y_vals) - 1):
        sum -= y_vals[i] * x_vals[i+1]
    sum -= y_vals[-1] * x_vals[0]
    return 0.5 * abs(sum)

p1 = [[-3,0], [0,3], [3,0], [1,1], [0,2]]
p2 = [[-2, 0], [-2,2], [0,4], [2,2], [2,0]]
print(calcIntersectArea(p2, p1))


plt.show()

