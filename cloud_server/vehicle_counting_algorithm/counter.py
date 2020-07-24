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

def format_coordinates(lines, resolutionRatio):
	'''
	Scales the line(s) coordinates according to the size of the input video resolution
	'''
	resolutionRatio = [float(val) for val in resolutionRatio.strip().split('x')]

	line_coord = []
	for val in lines.split(";"):
		line_coord.append([])
		points = val.strip().split(',')
		for i in range(2):
			p = (int(points[i*2].strip()), int(points[(i*2)+1].strip()))
			p = (int(p[0]*resolutionRatio[0]), int(p[1]*resolutionRatio[1]))
			line_coord[-1].append(p)
	return line_coord

class Counter():
	def __init__(self, lines, resolutionRatio):
		lines = format_coordinates(lines, resolutionRatio)
		self.trackedID = set()
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