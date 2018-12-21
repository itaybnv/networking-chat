from colorama import Fore,Back,Style,init
import os, sys
from socket import *
from threading import Thread
from datetime import datetime


# METHODS
def clientPrint(text, textColor):
    print(Fore.LIGHTGREEN_EX + f'[{str(datetime.now().time())[:8]}] ' + textColor + text)

def checkValidIP(IP):
    #  strip the IP string to array of each number 
    stripped = [x.strip() for x in IP.split('.')]
    #  If IP is made of more than 4 numbers return false
    if len(stripped) != 4:
        return False
    #  go through all 4 parts of the ip and make sure its between 0 - 255
    for num in stripped:
        if int(num) > 255 and int(num) < 0:
            return False
    return True  # No problem found 

def checkValidPort(Port):
    #  If port is between 0 - 65535
    return Port > 0 and Port < 65535

def LRProtocol(username=None, password=None, request=None, response=None, struct=None):
    return f'001|{username}|{password}|{request}|{response}' if not struct else [x for x in struct.split('|')]

def getServer():
    global HOST,PORT,ADDR
    #  Get IP from client
    clientPrint('enter server IP (Enter nothing for LOCALHOST): ', Fore.LIGHTCYAN_EX)
    serverIP = input()
    #  If client entered input
    if serverIP:
        # If IP is valid   
        if checkValidIP(serverIP):
            HOST = serverIP #  set HOST IP
    #  Get IP from client
    clientPrint('enter server Port: ', Fore.LIGHTCYAN_EX)
    serverPort = int(input())
    #  If client entered input
    if serverPort:
        # If PORT is valid   
        if checkValidPort(serverPort):
            PORT = serverPort #  set HOST PORT
    ADDR = (HOST,PORT)  # make the address tuple

def getLogin():
    print("Press R for register/ L for login: ")
    # Closest i can get to a do-while loop
    while True:
        req = input()
        if req == "R" or req == "r" or req == "L" or req == "l":
            break 

    usr = input("Enter your username: ")
    pss = input("Enter your password: ")
    return LRProtocol(usr, pss, req, '?')


def receive():
    while client_socket:
        try:
            msg = client_socket.recv(BUFFRESIZE).decode()
            clientPrint(msg, '')
        # In case client left the chat
        except OSError:
            break

def send():
    while True:
        msg = input()
        client_socket.send(msg.encode())
        if msg == '/quit':
            client_socket.close()
            break


# CONST VARIABLES
HOST = '127.0.0.1'
PORT = 55556
BUFFRESIZE = 1024
ADDR = (HOST,PORT)

client_socket = socket(AF_INET, SOCK_STREAM)


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

# Get server info
getServer()

# Connect to the server
client_socket.connect(ADDR)

notLoggedIn = True
while notLoggedIn:
    # Get client's login info
    struct = getLogin()

    # Send to the server the login/register info
    client_socket.send(struct.encode())

    # Receive an answer for login/register info sent
    ans = LRProtocol(struct=client_socket.recv(BUFFRESIZE).decode())
    if ans[4] == 'GOOD LOGIN' or ans[4] == 'GOOD REGISTER':
        notLoggedIn = False
        receive_thread = Thread(target=receive, daemon=True)
        receive_thread.start()
        send_thread = Thread(target=send, daemon=True)
        send_thread.start()
        send_thread.join()
    elif ans[4] == 'BAD LOGIN' or ans[4] == 'BAD REGISTER':
        print('Bad info. Try again...')