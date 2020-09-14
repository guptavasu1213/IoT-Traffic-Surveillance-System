import argparse
ap = argparse.ArgumentParser()
ap.add_argument("-et", "--encoding_time", help="The duration of video analysis to calculate the encoding parameters (in sec)", required=False, 
    default=10, type=int)
args = vars(ap.parse_args())

import socket
import sys
from connection import *

def server():
    '''
    Initiates the server and listens for the clients to connect
    '''
    server_port = 12000
    
    #Create server socket that uses IPv4 and TCP protocols 
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print('Error in server socket creation:',e)
        sys.exit(1)
    
    #Associate 12000 port number to the server socket
    try:
        server_socket.bind(('', server_port))
    except socket.error as e:
        print('Error in server socket binding:',e)
        sys.exit(1)        
        
    print('The server is ready to accept connections')
        
    #Specify the queue size waiting for acceptance
    server_socket.listen(5)
    
    while 1:
        try:            
            #Server accepts client connection
            connection_socket, addr = server_socket.accept()
            print(addr,'   ',connection_socket)
            
            pid = os.fork()

            if pid == -1: #Fork failed
                sys.exit(1)
            # If it is a client process
            elif  pid == 0:
                server_socket.close()
                receive_and_analyze_videos(connection_socket, str(args["encoding_time"]))
                return
            #Parent doesn't need this connection
            connection_socket.close()
            
        except socket.error as e:
            print('An error occured:',e)
            server_socket.close()
            sys.exit(1)        
        # except:
        #     print('Goodbye')
        #     serverSocket.close() 
        #     sys.exit(0)        
#-------
server()
