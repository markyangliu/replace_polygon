class NoIntersectionException(Exception):
    '''
    Raised when there are no intersections between the lines
    '''
    pass
class AllPointsIntersectException(Exception):
    '''
    Raised when all points between the lines are the same
    '''
    pass
def calcSlope(p1, p2):
    '''
    calculates the slope given two points
    :param p1: list -> [x,y]
    :param p2: list -> [x,y]
    :return: float -> slope
    '''
    if p1[0] == p2[0]: #vertical line
        return None
    else:
        return (p1[1] - p2[1]) / (p1[0] - p2[0])

def calcLinLineIntersect(lin1, lin2):
    '''
    calculates the intersection point of two lines each defined by two points
    :param lin1: list -> [p1, p2]
    :param p1: list -> [x, y]
    :return: list -> [x, y]
    '''
    m1 = calcSlope(lin1[0], lin1[1])
    m2 = calcSlope(lin2[0], lin2[1])
    if m1 == None: #vertical line
        intercept_1 = float(lin1[0][0])
    else:
        intercept_1 = float(lin1[0][1] - (m1 * lin1[0][0]))
    if m2 == None:#vertical line
        intercept_2 = float(lin2[0][0])
    else:
        intercept_2 = float(lin2[0][1] - (m2 * lin2[0][0]))

    if m1 == m2 : #if both vertical lines
        if intercept_1 == intercept_2:
            raise AllPointsIntersectException
        else:
            raise NoIntersectionException
    elif m1 == None: #if 1 vertical line
        inter_x = intercept_1
        inter_y = (m2 * intercept_1) + intercept_2
        return [inter_x, inter_y]
    elif m2 == None:#if 1 vertical line
        inter_x = intercept_2
        inter_y = (m1 * intercept_2) + intercept_1
        return [inter_x, inter_y]
    else:
        inter_x = ((m1 * lin1[0][0]) - lin1[0][1] - (m2 * lin2[0][0]) + lin2[0][1]) / (m1 - m2)
        inter_y = (m1 * (inter_x - lin1[0][0])) + lin1[0][1]
        return [inter_x,inter_y]