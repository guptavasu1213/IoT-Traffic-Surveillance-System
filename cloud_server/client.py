# This is an example from "Computer Networking: A Top Down Approach" textbook chapter 2
import socket
import sys

def client():
    # Server Information
    serverName = '137.186.146.107' #where the server is hosted
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
        
        # Client receives a message and send it to the client
        message = clientSocket.recv(2048).decode('ascii')
        
        #Client send message to the server
        message = input(message).encode('ascii')
        clientSocket.send(message)
        
        # Client receives a message from the server and print it
        message = clientSocket.recv(2048)
        print(message.decode('ascii'))
        
        # Client terminate connection with the server
        clientSocket.close()
        
    except socket.error as e:
        print('An error occured:',e)
        clientSocket.close()
        sys.exit(1)

#----------
client()
