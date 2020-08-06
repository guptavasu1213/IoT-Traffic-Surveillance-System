import socket
import sys
import os
import time

def receiveAcknowlegdement(socket, message="OK"):
    '''
    This function waits to receive a message at the given socket. 
    If the expected message is not received, then the program terminates.
    By default, the message is "OK", but can be changed
    '''
    if socket.recv(2048).decode('ascii') != message:
        print("ERROR: Acknowledgement not received")
        exit(1)
        
def sendAcknowledgment(socket, message="OK"):
    '''
    This function sends a message through the passed socket. 
    By default, the message is "OK", but can be changed
    '''
    socket.send(message.encode('ascii'))

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
        
    #The server can only have one connection in its queue waiting for acceptance
    serverSocket.listen(5)
        
    while 1:
        try:
            #Server accepts client connection
            connectionSocket, addr = serverSocket.accept()
            print(addr,'   ',connectionSocket)
            pid = os.fork()
            
            # If it is a client process
            if  pid == 0:
                serverSocket.close() 
                
                #Getting Fog node name
                fogName = connectionSocket.recv(2048).decode('ascii')
                print("Fog name is:", fogName)
                sendAcknowledgment(connectionSocket)
                #Getting the camera name
                cameraName = connectionSocket.recv(2048).decode('ascii')
                print("Cam name is:", cameraName)
                sendAcknowledgment(connectionSocket)
                
                folderName = "./streamed_files/{}/{}".format(fogName, cameraName)
                count_files = 0

                #Byte which denotes the video termination
                videoTerminationByte = "END".encode('ascii')

                receivedAllVideos = False
                #Receiving the video file
                while not receivedAllVideos:
                    fileName = "{}.mp4".format(str(count_files))
                    videoReceived = bytes() # Video initialization
                    with open(os.path.join(folderName, fileName),'wb') as file: 
                        # Receiving the video until the termination
                        while True:
                            recvfile = connectionSocket.recv(4096)
                            videoReceived += recvfile #Appending to the received video 

                            # print(recvfile)
                            if recvfile.endswith(videoTerminationByte):
                                videoReceived = videoReceived[:-len(videoTerminationByte)]
                                count_files += 1
                                print("FILE RECEIVED")
                                #Inform client about full video receival
                                sendAcknowledgment(connectionSocket) 
                                break
                            elif not recvfile: #When client connection terminates
                                receivedAllVideos = True
                                os.remove(os.path.join(folderName, fileName))
                                break
                        #Writing to a file
                        if not receivedAllVideos:
                            file.write(videoReceived)

                #Server sends the client the modified message
                # print(response)
                print("Closing socket")
                connectionSocket.close()
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
