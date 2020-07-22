from numpy import sign

def get_slope(line):
    # (y2-y1)/(x2-x1)
    ###########Can crash if x1 == x2
    print(line)
    return (line[1][1]-line[0][1])/(line[1][0]-line[0][0])
def get_intercept(line, slope):
    # y - mx = b
    return line[0][1] - (slope*line[0][0])

def get_line_result(x, y, m, b):
    # mx - y + b = 0 in the form Ax + By +c = 0
    return (m*x) - y + b 

class Counter():
    def __init__(self, lines):
        self.trackedID = set()
        # lines = [[(201, 221), (427, 149)]] # Easy-- and easy2
        # lines = [[(0, 534), (1129,534)]] #kukuNew
        # lines = [[(140, 192), (150, 250)], [(0, 480), (420, 320)]] #Cam1
        # lines = [[(140, 192), (150, 250)], [(197, 287), (425, 287)]] #Cam2
        # lines = [[(492, 255), (1064, 470)], [(866, 598), (1548, 851)]] #Highway
        # lines = [[(169, 630), (1122, 583)], [(1213, 509), (1725, 1000)]] #4k
        # lines = [[(0, 285), (565, 68)], [(238, 77), (552, 251)]] #Cam11---
        # lines = [[(0, 285), (565, 68)], [(178, 65), (552, 251)]] #cam12
        self.lines = []
        self.slopesAndIntercepts = [] #Stores slopes and intercepts for all lines
        self.setupLines(lines)

    def setupLines(self, lines):
        for line in lines:
            m = get_slope(line)
            b = get_intercept(line, m)
            self.lines.append(line)
            self.slopesAndIntercepts.append((m, b)) 

    def addToTrackedList(self, objectID):
        self.trackedID.add(objectID)

    def get_lines(self):
        return self.lines

    def check_sign(self, solutions):
        # If all the points are on one side of the line, return false 
        return not(len(set(sign(solutions))) == 1)

    def intersects_with_bbox(self, bbox):
        '''
        Just plug each corner (x,y) of the rectangle into ax+by+c. 
        A corner point is on the line if the result is zero. 
        If it's not zero then the sign indicates which side of the line the point lies. 
        If all points of the rectangle have the same sign after plugging them into the line equation then they all lay on the same side of the line and no intersection exists. 
        If signs differ, an intersection exists.

        Params: bbox contains x1, y1, x2, y2 for the bounding box 

        Return: True if the box intersects with the line; else false
        '''
        tl = (bbox[0], bbox[1]) #Top left
        tr = (bbox[2], bbox[1]) #Top right
        bl = (bbox[0], bbox[3]) #Bottom left
        br = (bbox[2], bbox[3]) #Bottom right

        # For each line
        for i, (m, b) in enumerate(self.slopesAndIntercepts):
            # print("For line", self.lines[i])
            solutions = []
            # Iterating through each corner of the bbox
            for point in [tl, tr, bl, br]:                                
                solutions.append(get_line_result(point[0], point[1], m, b))

            # All the solutions don't have the same sign then, the points intersect
            if (self.check_sign(solutions)):
                return True
            return False

# bbox = [0, 0, 10, 10]
# line_counter = Counter()
# if (line_counter.intersects_with_bbox(bbox)):
#     line_counter.addToTrackedList(trackedID)