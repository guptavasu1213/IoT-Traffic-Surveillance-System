# This is an example from "Computer Networking: A Top Down Approach" textbook chapter 2
# You can try this with nc localhost 12000

import socket
import sys
import os

def receiveAcknowlegdement(clientSocket, message="OK"):
    if clientSocket.recv(2048).decode('ascii') != message:
        exit(1)
        
def sendAcknowledgment(connectionSocket, message="OK"):
    connectionSocket.send(message.encode('ascii'))

def server():
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

                fogName = connectionSocket.recv(2048).decode('ascii')
                print("Fog name is:", fogName)
                sendAcknowledgment(connectionSocket)

                cameraName = connectionSocket.recv(2048).decode('ascii')
                print("Cam name is:", cameraName)
                sendAcknowledgment(connectionSocket)

                # #Server receives client message, decode it and convert it to upper case
                # message = connectionSocket.recv(2048)
                # response = message.decode('ascii').upper()
                
                folderName = "./streamed_files/{}/{}".format(fogName, cameraName)
                count_files = 0
                videoTerminationByte = str.encode(" ") #Converting to bytes

                receivedAllVideos = False
                #Receiving the video file
                while not receivedAllVideos:
                    fileName = "{}.mp4".format(str(count_files))
                    with open(os.path.join(folderName, fileName),'wb') as file: 
                        while True:               
                            recvfile = connectionSocket.recv(4096)
                            # print(recvfile)
                            if recvfile == videoTerminationByte:
                                count_files += 1
                                print("FILE RECEIVED")
                                break
                            elif not recvfile: #When client connection terminates
                                receivedAllVideos = True
                                os.remove(os.path.join(folderName, fileName))
                                break
                            file.write(recvfile)

                # savefilename = "abcd.mp4"
                # #Receiving the video file
                # with connectionSocket,open(savefilename,'wb') as file:
                #     while True:
                #         recvfile = connectionSocket.recv(4096)
                #         if not recvfile: break
                #         file.write(recvfile)
                #     print("FILE RECEIVED")

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
