# This is an example from "Computer Networking: A Top Down Approach" textbook chapter 2
import socket
import sys
import os
import time 

def receiveAcknowlegdement(clientSocket, message="OK"):
    if clientSocket.recv(2048).decode('ascii') != message:
        exit(1)
        
def sendAcknowledgment(connectionSocket, message="OK"):
    connectionSocket.send(message.encode('ascii'))

def client(fogNodeName, cameraName):
    # Server Information
    serverName = '199.116.235.176'
    serverPort = 12000
    
    #Create client socket that using IPv4 and TCP protocols 
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print('Error in client socket creation:',e)
        sys.exit(1)    
    
    try:
        #Client connect with the server
        clientSocket.connect((serverName,serverPort))
        
        #Send Fog Node Name
        clientSocket.send(fogNodeName.encode('ascii'))
        receiveAcknowlegdement(clientSocket)

        # Send Camera name
        clientSocket.send(cameraName.encode('ascii'))
        receiveAcknowlegdement(clientSocket)
        
        count = 0
        folderPath = "./street-cam-videos/" + cameraName
        videoFiles = sorted(os.listdir(folderPath))

        for fileName in videoFiles:   
            filePath = os.path.join(folderPath, fileName)
            # filename = "/home/vasu/Documents/street-videos/youtubeDownloads/easy.mp4"
            with open(filePath, 'rb') as file:
                # sendfile = file.read()
                
                # ==== If sending a file in pieces
                while True:
                    count += 1
                    sendfile = file.read(4096)
                    if not sendfile: break
                    # print(count)

                    clientSocket.send(sendfile)
            time.sleep(2)
            # clientSocket.sendall(sendfile)
            sendAcknowledgment(clientSocket, " ") # " " denotes video termination
            # receiveAcknowlegdement(clientSocket)
            print("{} : {} -- Video sent".format(cameraName, fileName))
        #Client send message to the server
        # response = "OK".encode('ascii')
        # clientSocket.send(response)
        
        # # Client receives a message from the server and print it
        # message = clientSocket.recv(2048)
        # print(message.decode('ascii'))
        
        # Client terminate connection with the server
        clientSocket.close()
        
    except socket.error as e:
        print('An error occured:',e)
        clientSocket.close()
        sys.exit(1)

#----------
# client()
