from numpy import sign

def get_slope(line):
	'''
	Calculate slope using the formula: (y2-y1)/(x2-x1)
	'''
	try:
		return (line[1][1]-line[0][1])/(line[1][0]-line[0][0])
	except: #Crashes if denominator is zero
		return 0
def get_intercept(line, slope):
	'''
	Calculate intercept using formula: y - mx = b
	'''
	return line[0][1] - (slope*line[0][0])

def get_line_result(x, y, m, b):
	'''
	Calculating the result by using mx - y + b = 0 in the form Ax + By +c = 0
	'''
	return (m*x) - y + b 

def format_coordinates(lines, current_resolution):
	'''
	Scales the line(s) coordinates according to the size of the input video resolution
	:param lines: String containing the coordinates of the line(s)
	:param current_resolution: List which contains the width and height of the current resolution
	'''
	line_coord = []
	for val in lines.split(";"):
		line_coord.append([])
		points = val.strip().split(',')
		for i in range(2):
			p = (int(points[i*2].strip()), int(points[(i*2)+1].strip()))
			p = (round(p[0] * current_resolution[0] / 100), round(p[1] * current_resolution[1] / 100))
			line_coord[-1].append(p)
	return line_coord

class Counter():
	'''
	Counts the vehicles which have intersected with the line
	'''
	def __init__(self, lines, current_resolution):
		lines = format_coordinates(lines, current_resolution)
		self.tracked_id = set()
		self.lines = []
		self.slopes_and_intercepts = [] #Stores slopes and intercepts for all lines
		self.setup_lines(lines)

	def setup_lines(self, lines):
		for line in lines:
			m = get_slope(line)
			b = get_intercept(line, m)
			self.lines.append(line)
			self.slopes_and_intercepts.append((m, b))

	def add_to_tracked_list(self, object_id):
		self.tracked_id.add(object_id)

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
		If all points of the rectangle have the same sign after plugging them into the line equation then they all lay
		on the same side of the line and no intersection exists.
		If signs differ, an intersection exists.

		Params: bbox contains x1, y1, x2, y2 for the bounding box 

		Return: True if the box intersects with the line; else false
		'''
		tl = (bbox[0], bbox[1]) #Top left
		tr = (bbox[2], bbox[1]) #Top right
		bl = (bbox[0], bbox[3]) #Bottom left
		br = (bbox[2], bbox[3]) #Bottom right

		# For each line
		for i, (m, b) in enumerate(self.slopes_and_intercepts):
			solutions = []
			# Iterating through each corner of the bbox
			for point in [tl, tr, bl, br]:                                
				solutions.append(get_line_result(point[0], point[1], m, b))

			# All the solutions don't have the same sign then, the points intersect
			if (self.check_sign(solutions)):
				return True
			return False
