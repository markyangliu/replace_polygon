import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib.patches import Arc as plotArc
from graphutil import *
import copy

def replacePoly(input):
    '''
    Replaces a polygon with defined vertices with arcs of best fit
    :return:
    '''
    x,y = coordInput(input)
    plt.plot([x[i] for i in range(-1, len(x))], [y[i] for i in range(-1, len(y))])
    plt.axis([0, 10, 0, 10])
    plt.show()

    angle_vals,endpt_vals,ext_int = calcVecAng(x,y,0.5)

    arc_dict = []

    aL_resolution = 10  # precision of arc length increments
    for _theta in range(1, 181):  # populates dictionary of arcs
        for _aL in range(1, 100):
            arc_dict.append((Arc(_aL / 10, _theta, 0)))

    arc_list = replaceArc(x,y,endpt_vals,angle_vals,arc_dict)

    arc_list = appendDirection(endpt_vals,arc_list,ext_int)

    fg, ax = plt.subplots(1, 1)

    for _arc in arc_list:
        ax.add_patch(plotArc(_arc.position[0], 2 * _arc.roc, 2 * _arc.roc, _arc.position[1], 0, _arc.theta))
        #plt.plot(_arc.position[0][0], _arc.position[0][1], '.')

    endpt_vals.append(endpt_vals[0])
    for _ep1, _ep2 in zip(endpt_vals[0:-1], endpt_vals[1:]):
        #print(_ep1, _ep2)
        ep1 = np.array(_ep1[1])
        ep2 = np.array(_ep2[0])
        epx = np.array([ep1[0], ep2[0]])
        epy = np.array([ep1[1], ep2[1]])
        ax.plot(epx, epy, ':r')

    for a in arc_list:
        print('aL: {0}, roc: {1}, angle: {2}, center: {3}, angle of rotation: {4}'.format(a.aL, a.roc, a.theta,
                                                                                          a.position[0], a.position[1]))

    fg.canvas.draw()
    ax.axis([0, 10, 0, 10])
    plt.show()

    poly_coords = []
    inc = 0
    for i in range(len(arc_list)):
        poly_coords.append(endpt_vals[i][0])
        poly_coords.append(arc_list[i])
        poly_coords.append(endpt_vals[i][1])
    print(poly_coords)

    return poly_coords,

class Arc(object):
    def __init__(self, aL, theta, arc_obj):
        self.aL = aL
        self.theta = theta
        # the arc_obj will later be the actual DNA origami representation of the arc
        # for now, it's useless
        self.arc_obj = 0
        self.roc = aL / math.radians(theta)
        self.position = 0  # center, direction of rightmost vector

def coordInput(path):
    '''
    Takes in an input file and converts each line in format num, num into a coordinate list
    :param path: string -> path of txt file
    :return: list, list -> x_vals, y_vals
    '''
    f = open(path, 'r')
    inputPoints = []
    for line in f:
        line = line.replace(" ", "")
        line = line.rstrip('\n')
        line = line.rstrip()
        inputPoints.append([float(i) for i in line.split(',') if i.isdecimal()])  # convert to int
    f.close()
    x = []
    y = []
    for coords in inputPoints:
        x.append(coords[0])
        y.append(coords[1])
    return x,y

def calcEndpoint(v1_u, v2_u, x, y, endpt_length):
    '''
    calculates the endpoints of the arc based on unit vectors from vertices
    :param v1_u: list -> [x_dis, y_dis]
    :param x: float
    :param y: float
    :param endpt_length: float
    :return: list, list -> [x,y], [x,y]
    '''
    endpt1 = [x - (endpt_length * v1_u[0]), y - (endpt_length * v1_u[1])]
    endpt2 = [x - (endpt_length * v2_u[0]), y - (endpt_length * v2_u[1])]
    return endpt1, endpt2

def calcVecAng(x,y, endpt_len):
    ang_vals = []
    end_vals = []
    ext = []

    for i in range(len(x)):  # calculates vectors between each point and angle values
        if i != len(x) - 1:
            v1 = np.array([x[i] - x[i - 1], y[i] - y[i - 1]])
            v2 = np.array([x[i] - x[i + 1], y[i] - y[i + 1]])
        else:
            v1 = np.array([x[i] - x[i - 1], y[i] - y[i - 1]])
            v2 = np.array([x[i] - x[0], y[i] - y[0]])
        # unit vector
        v1_u = v1 / np.linalg.norm(v1)
        v2_u = v2 / np.linalg.norm(v2)
        # endpoints of the arc segment
        end_vals.append(calcEndpoint(v1_u, v2_u, x[i], y[i], endpt_len))

        ext.append((v1[0] * v2[1] > v2[0] * v1[1]))

        # calculates angle of corner
        ang_vals.append(np.degrees(np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))))
    return ang_vals,end_vals,ext

def replaceArc(x,y,end_vals,angle_vals, arc_dict):
    arc_list = []
    for i in range(len(angle_vals)):  # calculates aL and replaces corner with arc in dict
        alpha = 180 - angle_vals[i]
        # p1(a1,a2), p2(b1,b2)
        v = [x[i], y[i]]  # vertex
        p1 = [end_vals[i][0][0], end_vals[i][0][1]]
        p2 = [end_vals[i][1][0], end_vals[i][1][1]]
        center = [None] * 2

        m1 = calcSlope(p1, v)
        m2 = calcSlope(p2, v)

        if m1 not in [0, None]:
            n1 = math.pow(m1, -1) * -1
        if m2 not in [0, None]:
            n2 = math.pow(m2, -1) * -1

        if (m1 == None):
            center[1] = p1[1]
            if(m2 == 0):
                center[0] = p2[0]
            else:
                center[0] = ((center[1] - p2[1]) / n2) + p2[0]
        elif (m2 == None):
            center[1] = p2[1]
            if (m1 == 0):
                center[0] = p1[0]
            else:
                center[0] = ((center[1] - p1[1]) / n1) + p1[0]
        elif (m1 == 0):
            center[0] = p1[0]
            center[1] = (n2 * (center[0] - p2[0])) + p2[1]
        elif (m2 == 0):
            center[0] = p2[0]
            center[1] = ((n1 * (center[0] - p1[0])) + p1[1])
        else:
            center[0] = ((n1 * p1[0]) - p1[1] - (n2 * p2[0]) + p2[1]) / (n1 - n2)
            center[1] = ((n1 * (center[0] - p1[0])) + p1[1])


        _aL = math.radians(alpha) * math.hypot(p1[0] - center[0], p1[1] - center[1])

        arc_list.append(copy.copy(findArc(arc_dict,alpha,_aL))) #replace with function to find best piece arc

        arc_list[i].position = [center]

    return arc_list


def appendDirection(endpt_vals,arc_list,ext):
    '''
    Appends the angle of the arc to the arc list
    :param endpt_vals: endpoints of the arc
    :param arc_list: list of arcs
    :param ext:
    :return:
    '''
    for i in range(len(arc_list)):
        #check if exterior or interior angle
        if ext[i]:
            r_l = 1
        else:
            r_l = 0
        d_x = endpt_vals[i][r_l][0] - arc_list[i].position[0][0]
        d_y = endpt_vals[i][r_l][1] - arc_list[i].position[0][1]
        if (d_x == 0):
            direction = 90
        elif (d_y == 0):
            direction = 0
        else:
            direction = np.degrees(np.arctan(abs(d_y / d_x)))
        # add/sub based on quadrant
        if (d_x < 0 and d_y > 0):
            direction = 180 - direction
        elif (d_x < 0 and d_y < 0) or (d_x < 0 and d_y == 0)  or (d_x == 0 and d_y < 0):
            direction = 180 + direction
        elif d_x > 0 and d_y < 0:
            direction = 360 - direction

        arc_list[i].position.append(direction)
    return arc_list

def findArc(arc_dict, angle_val, arc_len):
    '''
    :param arc_dict:
    :param angle_val:
    :param arc_len:
    :return:
    '''
    for arc in arc_dict:
        if round(arc_len, 1) == arc.aL and round(angle_val, 0) == arc.theta:
            return arc

