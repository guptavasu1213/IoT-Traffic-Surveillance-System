'''
One connection per street camera
'''
import os
import signal
import time

# Flags for handlers
analyzeVideo = False
terminate = False

def getProcessState(pid):
	'''
	:param pid: Process ID of the process to be inspected
	:return: State of the process. Example: 'R' for running, 'S' for sleep and so on.
	'''
	for line in open("/proc/%d/status" % pid).readlines():
		if line.startswith("State:"):
			return line.split(":", 1)[1].strip().split(' ')[0]

def receive_signal(signum, stack):
	'''
	Signal handler for receiving a signal to process video files
	'''
	# print('YAYYYYYY:', signum)
	global analyzeVideo
	analyzeVideo = True
	# signal.pause()

def quit(signum, stack):
	'''
	Signal handler for termination of the process
	'''
	if analyzeVideo:
		global terminate
		terminate = True
	else: # Terminating when there is no video analysis happening
		# print("QUITTING")
		exit(0)

def dothis():
	# Setup handlers
	signal.signal(signal.SIGUSR1, receive_signal)
	signal.signal(signal.SIGINT, quit)
	global analyzeVideo

	os.kill(os.getppid(), signal.SIGUSR2)
	print ('My PID is:', os.getpid())

	while True:
		print("SLEEP----------------------")
		signal.pause()
		print("WOKEUP---------------------")
		if analyzeVideo:
			print("Analyze video now","="*8)
			# Go through all the videos in the folder
			# Delete each video after vehicle analysis
			# pass
			analyzeVideo = False

		if terminate:
			print("Terminating video now", "="*8)
			exit(0)

	# while True:
	#     continue
	# while True:
	#     print("Before sleeep")
	#     sig = signal.sigwait([signal.SIGUSR1, signal.SIGINT])
	#     print("Woke uppppppp", sig)
	#     if sig == signal.SIGINT: #SIGINT
	#         quit(sig, "")
	#     elif sig == signal.SIGUSR1: #SIGUSR1
	#         receive_signal(sig, "")

listening = False

def listenToChild(signum, stack):
	'''
	Signal handler to specify that the child process is ready to listen
	'''
	global listening
	listening = True

# Initiate server
# Fork and Client connects
# Fork for a program peeping into the streamed video folder
# Receive video
print("Initiate Server")

pid = os.fork()

if pid == 0:
	print("Client connected")

	#Setup handler
	signal.signal(signal.SIGUSR2, listenToChild)

	pid = os.fork()
	if pid == -1:
		exit(1)
	elif pid == 0: #Child
		print("Listen")
		dothis()
		exit(1)

	while True:
		signal.pause() #Suspends the current process
		if listening:
			break
	sig_lis = [1,1,1,1,1,1,3]

	while True:
		# time.sleep(0.00000000001)
		sig = sig_lis.pop(0)
		# sig = input("Enter sig:\t")
		if sig == 1:
			print("SENT 1")
			os.kill(pid, signal.SIGUSR1)
		else:
			print("KILLED")
			os.kill(pid, signal.SIGINT)
			break

	print("Receiving files")
	exit(1)
print("GParent now")