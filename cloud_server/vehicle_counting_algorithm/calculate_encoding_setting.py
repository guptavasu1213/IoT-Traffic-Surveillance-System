THRESHOLD = 0.10 #Up to 10% error allowed

def get_file_name_from_path(file_path):
	'''
	Returns the file name without extension from the path
	'''
	return file_path[: file_path.rindex('.')].split("/")[-1] #without extension

def compute_vehicle_count(file_path):
	'''
	Computes the vehicle count for the given file name and returns the count
	'''
	count_file_name = 'count_logs/' + get_file_name_from_path(file_path) + ".txt"

	line_coordinates = {}
	#LINE COORDINATES SHOULD BE RELATIVE TO THE RESOLUTION #############
	cmd = "python3 main.py -i " + file_path + " -l \"" + str(line_coordinates) + "\"" + \
		" -cf " + count_file_name		
	print("Running command:\n" + cmd)
	# subprocess.run(cmd, shell=True)

	############# MODIFY THE FILE TO STORE THE count IN A TXT FILE
	return 100

	with open(count_file_name, 'r') as file:
		count = int(file.read().strip())
	return count

def calculate_bitrate(file_path):
	'''
	Calculate the lowest bitrate while having the detection within the threshold
	'''
	bitrate = 100 #kbps
	increase_factor = 50 #kbps
	file_name = get_file_name_from_path(file_path) #without extension
	extension = file_path[file_path.rindex('.')+1 :]

	#Calculate vehicle count in the original video
	vehicle_count_high_res = compute_vehicle_count(file_path)
	
	#LOOP
	while True:
		#Convert the video to given bitrate
		new_file_path = "compressed_videos/" + file_name +'-bitrate-'+str(bitrate)+ "." + extension
		# set_video_bitrate(file_path, new_file_path, bitrate)

		#Calculate the vehicle count on the low encoding video
		vehicle_count_low_res = compute_vehicle_count(new_file_path)-1

		#If the error is within the threshold, then break
		detection_error = abs(vehicle_count_high_res-vehicle_count_low_res)/vehicle_count_high_res
		print(detection_error, THRESHOLD)
		if (detection_error <= THRESHOLD):
			break
		#If the count is outside the threshold, then increase the bit rate
		else:
			bitrate = bitrate+increase_factor

calculate_bitrate("AB.mp4")
