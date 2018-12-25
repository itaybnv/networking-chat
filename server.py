"""
programmer: itay benvenisti

"""

from colorama import Fore,Back,Style,init
import os, sys
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from datetime import datetime
import re
import mysql.connector


# METHODS
def log(textLine):
    # Write the textline and go a line down
    with open('log.txt','a') as file:
        file.write(f'[{datetime.now().time()}] '  + textLine + '\n')

def serverPrint(text, textColor): 
    print(Fore.LIGHTGREEN_EX + f'[{datetime.now().time()}] ' + textColor + text)
    log(text)



def handleClient(client, clientName, room):
    clientRoom = room
    try:
        # Greet the client
        client.send(f"Greetings {clientName}, You've succesfully connected to the server. \n If you ever want to quit, type /quit to exit.".encode())
        # Broadcast client connected
        broadcastMSG = f"{clientName} has joined the chat!"
        broadcast(broadcastMSG.encode('utf-8'), room= clientRoom)
        serverPrint(broadcastMSG, Fore.GREEN) 
        # Add client to clients dict
        clients[client] = clientName
        # MAIN LOOP
        while True:
            # Get in received a list made of the content of the sent protocol
            received = client_socket.recv(BUFFRESIZE).decode()
            received = ProtocolDeconstruct(received)
            # 001 => LRProtocol
            if received[0] == '001':
                pass
            # 002 => MSGProtocol
            elif received[0] == '002':
                if received[1] != '/quit':
                    broadcast(received[1].encode(), clientRoom, clientName)
                    serverPrint(f'Room {clientRoom}::: {clientName}: {fore.WHITE}{received[1]}', Fore.LIGHTBLUE_EX)
                else: 
                    clients.pop(client)
                    client.close()
                    left = f'{clientName} has left the chat.'
                    broadcast(left.encode(), clientRoom)
                    serverPrint(left, Fore.RED)
                    sys.exit()
            # 003 => ChannelProtocol
            elif received[0] == '003':
                if received[2] == 'CREATE CHANNEL':
                    if received[1] in chatRooms:
                        client.send(ChannelProtocol(received[1], received[2], 'CHANNEL ALREADY EXISTS').encode())
                    # Create the channel and put the client in it
                    else:
                        # Create the channel
                        createChannel(received[1], clientRoom, client)
                        # Update the client's room 
                        clientRoom = received[1]
                # ! Currently you can delete a channel only if you are the first one to join to it, which makes sense looking at the create channel option. But may create some problems with the general channel
                # TODO: Think of a better solution to the problem mentioned above
                elif received[2] == 'DELETE CHANNEL':
                    if clientName == chatRooms[received[1]][0]:
                        deleteChannel(channelName)
                elif received[2] == 'JOIN CHANNEL':
                    if received[1] in chatRooms:
                        joinChannel(received[1], clientRoom, client)
                        clientRoom = received[1]
    except:
        return
# TODO: Check if dict[key].action actually changes the dict[key] value or just changes the returned value            
def createChannel(channelName, prevChannel, socket):
    # Add the channel to chatRooms dictionary
    chatRooms[channelName] = [socket]
    # Remove the client's socket from his previous channel
    chatRooms[prevChannel] = chatRooms[prevChannel].Remove(socket)

def deleteChannel(name):
    # Empty channel
    for socket in chatRooms[name]:
        chatRooms[name] = chatRooms[name].Remove(socket)
        chatRooms[GENERAL] = chatRooms[GENERAL].append(socket)
        # ! TERRIBLE way of changing clientRoom in each client's specific thread. FIND A BETTER WAY!!!
        socket.send(ChannelProtocol(name,'ASK TO JOIN CHANNEL', '?').encode())
    # Delete channel from dictionary
    chatRooms.pop(name)

def joinChannel(channelName, prevChannel, socket):
    # Add socket to requested channel
    chatRooms[channelName] = chatRooms[channelName].append(socket)
    # Remove socket from previous channel
    chatRooms[prevChannel] = chatRooms[prevChannel].Remove(socket)

def broadcast(msg, room, name="" ):
    for client_socket in chatRooms[room]:
        if len(name) == 0:
            client_socket.send(f"{Fore.RED}".encode() + msg)
        else:
            client_socket.send(f"{Fore.BLUE}{name}: {Fore.WHITE}{msg.decode()}".encode())


def LRProtocol(username=None, password=None,nickname=None, request=None, response=None):
    return f'001|{username}|{password}|{nickname}|{request}|{response}'

def MSGProtocol(msg=None):
    return f'002|{msg}'

def ChannelProtocol(channel=None, request=None, response=None):
    return f'003|{channel}|{request}|{response}'

def ProtocolDeconstruct(struct):
    return [x for x in struct.split('|')]

def accountExists(username, password):
    '''Checks if the Account info already exists in accounts database
    
    Arguments:
        username {string} -- the username string to check against the account database
        password {string} -- the password string to check against the account database
    
    Returns:
        boolean -- True: account exists. False: account doesnt exist
    '''

    mycursor.execute(f"SELECT * FROM Accounts WHERE username = '{username}' AND password = '{password}'")
    mycursor.fetchone()
    print('accountexists ' + str(mycursor.rowcount))
    return mycursor.rowcount != -1
   

def usernameExists(usr):
    '''Checks if the username already exists in the accounts database
    
    Arguments:
        usr {string} -- the username string to check against the account database
    
    Returns:
        boolean -- True: user exists. False: user doesn't exist
    '''
    # mySQL command that returns accounts with {usr} as their username
    mycursor.execute(f"SELECT * FROM Accounts WHERE username = '{usr}'")
    # Takes the first result. and returns true if it
    mycursor.fetchone()
    return mycursor.rowcount != -1

def addAccount(username, password, nickname):
    '''Adds an account to the accounts database using mySQL
    
    Arguments:
        username {string} -- the USERNAME to add to the database
        password {string} -- the PASSWORD to add to the database
    '''
    # mySQL command that inserts a new records with username and password
    mycursor.execute(f"INSERT INTO Accounts (username, password, nickname) VALUES ('{username}', '{password}', '{nickname}')")
    # Commits the changes to the Accounts database
    mydb.commit()

def signHandle(socket):
    # Get the login/register info from client
    struct = socket.recv(BUFFRSIZE).decode()
    stripped = ProtocolDeconstruct(struct)
    # Client is trying to login into an existing account
    if stripped[4] == 'L' or stripped[4] == 'l':      
        if accountExists(stripped[1], stripped[2]):
            # Login exists
            stripped[5] = 'GOOD LOGIN'
            serverPrint('GOOD LOGIN', Fore.GREEN)
            stripped[3] = getNickname(stripped[1])
            return stripped
        else:
            stripped[5] = 'BAD LOGIN'
            serverPrint('BAD LOGIN', Fore.RED)
            return stripped


    # Client is trying to create a new account         
    elif stripped[4] == 'R' or stripped[4] == 'r':
        if not usernameExists(stripped[1]):
            addAccount(stripped[1], stripped[2], stripped[3])
            stripped[5] = 'GOOD REGISTER'
            serverPrint('GOOD REGISTER', Fore.GREEN)
            stripped[3] = (stripped[3],) # ? TEST
            return stripped
        else:
            stripped[5] = 'BAD REGISTER'
            serverPrint('BAD REGISTER', Fore.RED)
            return stripped

    # Wrong request
    else:
        raise Exception('Invalid request')

def getNickname(username):
    mycursor.execute(f"SELECT nickname FROM Accounts WHERE username = '{username}'")
    return mycursor.fetchone()       

def acceptIncomingConnections():
    while True:
        try:
            # Wait for a connection
            client_socket, addr = server_socket.accept()
            # Print who connected 
            serverPrint( addr[0] + ' Connected.', Fore.LIGHTGREEN_EX)
            notLoggedIn = True
            while notLoggedIn:
                # Handle user login/register
                signH = signHandle(client_socket)
                client_socket.send(LRProtocol(signH[1], signH[2], signH[3], signH[4], signH[5]).encode())
                if signH[5] == 'GOOD LOGIN' or signH[5] == 'GOOD REGISTER':
                    # Exit the loop
                    notLoggedIn = False
                    
                    chatRooms[GENERAL].append(client_socket)
                    # Open a thread that handles the client
                    Thread(target=handleClient, args=(client_socket,signH[3][0], GENERAL,), daemon=True).start()
        except:
            # Server has ended
            break

def connectToDatabase():
    try:
        mydb = mysql.connector.connect(host="localhost", user="root", passwd="Itay01itay01", database='testdb')
        mycursor = mydb.cursor()
        return (mydb, mycursor,)
    except:
        return None

def commands():
    while True:
        command = input()
        if (command == 'quit'):
            shutdown()
            break

def shutdown():
    for client in clients:
        client.close()
    server_socket.close()
    


# CONST VARIABLES
HOST = '0.0.0.0'  #accept everyone
PORT = 55556
BUFFRSIZE = 1024
ADDR = (HOST,PORT)

# VARIABLES
server_socket = socket(AF_INET, SOCK_STREAM)  # Create a socket for client to connect to
#adresses = {}
clients = {}
chatRooms = {}
# Default chat room
GENERAL = '0001'
chatRooms[GENERAL] = []


'''
NOTE: chatRooms and clients are dictionaries that look like this:

    clients:
        socket1 : socket1 client name
        socket2 : socket2 client name
        socket3 : socket3 client name
                    ....

'''

# Colorama init
init()

# Clear console
os.system('cls')

# Connect to accounts database
mydb, mycursor = connectToDatabase()

# Setup server socket to listen for connections on HOST:PORT
server_socket.bind(ADDR)  # bind the socket to the address (HOST:PORT)
server_socket.listen(10)  # set the client queue max length to connect to the server_socket
# Print Wait for connection
serverPrint ('Server waiting for connections...', Fore.LIGHTCYAN_EX)
accept_thread = Thread(target= acceptIncomingConnections)
accept_thread.start()
commands_thread = Thread(target=commands)
commands_thread.start()
commands_thread.join()
