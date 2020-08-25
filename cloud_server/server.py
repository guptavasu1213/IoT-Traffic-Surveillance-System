import socket
import sys
from connection import *

def server():
    '''
    Initiates the server and listens for the clients to connect
    '''
    #Server port
    serverPort = 12000
    
    #Create server socket that uses IPv4 and TCP protocols 
    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print('Error in server socket creation:',e)
        sys.exit(1)
    
    #Associate 12000 port number to the server socket
    try:
        serverSocket.bind(('', serverPort))
    except socket.error as e:
        print('Error in server socket binding:',e)
        sys.exit(1)        
        
    print('The server is ready to accept connections')
        
    #Specify the queue size waiting for acceptance
    serverSocket.listen(5)
    
    while 1:
        try:            
            #Server accepts client connection
            connectionSocket, addr = serverSocket.accept()
            print(addr,'   ',connectionSocket)
            
            pid = os.fork()

            if pid == -1: #Fork failed
                sys.exit(1)
            # If it is a client process
            elif  pid == 0:
                serverSocket.close()
                receiveAndAnalyzeVideos(connectionSocket)
                return
            #Parent doesn't need this connection
            connectionSocket.close()
            
        except socket.error as e:
            print('An error occured:',e)
            serverSocket.close() 
            sys.exit(1)        
        # except:
        #     print('Goodbye')
        #     serverSocket.close() 
        #     sys.exit(0)        
#-------
server()
