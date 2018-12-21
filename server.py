from colorama import Fore,Back,Style,init
import os, sys
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from datetime import datetime
import re


# METHODS
def log(textLine):
    # Write the textline and go a line down
    with open('log.txt','a') as file:
        file.write(f'[{datetime.now().time()}] '  + textLine + '\n')

def serverPrint(text, textColor): 
    print(Fore.LIGHTGREEN_EX + f'[{datetime.now().time()}] ' + textColor + text)
    log(text)

def handleClient(client, clientName):
    # Greet the client
    client.send(f"Greetings {clientName}, You've succesfully connected to the server. \n If you ever want to quit, type /quit to exit.".encode())
    # Broadcast client connected
    broadcastMSG = f"{clientName} has joined the chat!"
    broadcast(broadcastMSG.encode('utf-8'))
    serverPrint(broadcastMSG, Fore.GREEN) 
    # Add client to clients dict
    clients[client] = clientName
    # MAIN LOOP
    while True:
        # Recieve msg from client
        msg = client.recv(BUFFRSIZE)
        # Broadcast if not /quit
        if msg != b'/quit':
            broadcast(msg, clientName)
            serverPrint(f'{clientName}: {Fore.WHITE}{msg.decode()}', Fore.LIGHTBLUE_EX) 
        else:
            clients.pop(client)
            client.close()
            left = f'{clientName} has left the chat.'
            broadcast(left.encode())
            serverPrint(left, Fore.RED) 
            sys.exit()
            

def broadcast(msg, name=""):
    for client_socket in clients:
        if len(name) == 0:
            client_socket.send(f"{Fore.RED}".encode() + msg)
        else:
            client_socket.send(f"{Fore.BLUE}{name}: {Fore.WHITE}{msg.decode()}".encode())


def LRProtocol(username=None, password=None, request=None, response=None, struct=None):
    return f'001|{username}|{password}|{request}|{response}' if not struct else [x.strip() for x in struct.split('|')]

def signHandle(socket):
    # Get the login/register info from client
    struct = socket.recv(BUFFRSIZE).decode()
    stripped = LRProtocol(struct= struct)
    # Client is trying to login into an existing account
    if stripped[3] == 'L':

        # Open the logins text file
        with open('logins.txt','r') as file:
            prevLine = ''

            lines = [line.rstrip('\n') for line in file]
            print (lines)
            # Go through every line and check if the username that the client entered exists in the file
            # and if it is followed by the password the client entered
            for line in lines:
                if stripped[2] == line and stripped[1] == prevLine:
                    # Login exists
                    stripped[4] = 'GOOD LOGIN'
                    serverPrint('GOOD LOGIN', Fore.GREEN)
                    return stripped
                prevLine = line 
        # Login doesn't exist
        stripped[4] = 'BAD LOGIN'
        serverPrint('BAD LOGIN', Fore.RED)
        return stripped

    # Client is trying to create a new account         
    elif stripped[3] == 'R':
        pass

    # Wrong request
    else:
        raise Exception('Invalid request')
        

def acceptIncomingConnections():
    while True:
        client_socket, addr = server_socket.accept()
        # Print who connected 
        serverPrint( addr[0] + ' Connected.', Fore.LIGHTGREEN_EX)
        notLoggedIn = True
        while notLoggedIn:
            # Handle user login/register
            signH = signHandle(client_socket)
            client_socket.send(LRProtocol(signH[1], signH[2], signH[3], signH[4]).encode())
            if signH[4] == 'GOOD LOGIN' or signH[4] == 'GOOD REGISTER':
                notLoggedIn = False
                Thread(target=handleClient, args=(client_socket,signH[1],), daemon=True).start()


# CONST VARIABLES
HOST = '0.0.0.0'  #accept everyone
PORT = 55556
BUFFRSIZE = 1024
ADDR = (HOST,PORT)

# VARIABLES
server_socket = socket(AF_INET, SOCK_STREAM)  # Create a socket for client to connect to
#adresses = {}
clients = {}
'''
NOTE: adresses and clients are dictionaries that look like this:

    clients:
        socket1 : socket1 client name
        socket2 : socket2 client name
        socket3 : socket3 client name
                    ....

'''

# Colorama init
init()
'''
COLORAMA NOTES:
    * Fore.LIGHTCYAN_EX = normal text color
    * Fore.LIGHTGREEN_EX = good (connected, sent, ETC...)
    * Fore.RED = bad (no response, timeout, ETC...)
    * FORE.BLUE = pending
'''

# Clear console
os.system('cls')
# Setup server socket to listen for connections on HOST:PORT
server_socket.bind(ADDR)  # bind the socket to the address (HOST:PORT)
server_socket.listen(10)  # set the client queue max length to connect to the server_socket
# Print Wait for connection
serverPrint ('Server waiting for connections...', Fore.LIGHTCYAN_EX)
acceptIncomingConnections()


