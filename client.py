from colorama import Fore,Back,Style,init
import os, sys
from socket import *
from threading import Thread
from datetime import datetime
import untitled
from PyQt5 import QtCore, QtGui, QtWidgets


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

def LRProtocol(username=None, password=None,nickname=None, request=None, response=None):
    return f'001|{username}|{password}|{nickname}|{request}|{response}'

def MSGProtocol(msg=None):
    return f'002|{msg}'

def ChannelProtocol(channel=None, request=None, response=None):
    return f'003|{channel}|{request}|{response}'

def ProtocolDeconstruct(struct):
    return [x for x in struct.split('|')]

def getServer():
    #  Get IP from client
    clientPrint('enter server IP (Enter nothing for LOCALHOST): ', Fore.LIGHTCYAN_EX)
    serverIP = input()
    #  If client entered input
    if serverIP:
        # If IP is valid   
        if checkValidIP(serverIP):
            return serverIP

def getLogin():
    print("Press R for register/ L for login: ")
    # Closest i can get to a do-while loop
    while True:
        req = input()
        if req == "R" or req == "r" or req == "L" or req == "l":
            break 
    nick = None
    usr = input("Enter your username: ")
    pss = input("Enter your password: ")
    if req == "R" or req == "r":
        nick = input("What is your nickname: ")
    return LRProtocol(usr, pss, nick, req, '?')


def receive():
    while client_socket:
        try:
            # Get in received a list made of the content of the sent protocol
            received = client_socket.recv(BUFFRESIZE).decode()
            received = ProtocolDeconstruct(received)
            print(received)
            # 001 => LRProtocol
            if received[0] == '001':
                pass
            # 002 => MSGProtocol
            elif received[0] == '002':
                clientPrint(received[1], '')
            # 003 => ChannelProtocol
            elif received[0] == '003':
                
                if received[3] == 'CHANNEL DOESNT EXIST':
                    clientPrint(received[3], Fore.RED)
                elif received[3] == 'CHANNEL ALREADY EXISTS':
                    clientPrint(received[3], Fore.YELLOW)
                elif received[3] == 'ACCESS DENIED':
                    clientPrint(received[3], Fore.RED)
                elif received[3] == 'DELETED SUCCESSFULLY':
                    clientPrint(received[3], Fore.YELLOW)
                elif received[3] == 'JOINED SUCCESSFULLY':
                    clientPrint(received[3], Fore.YELLOW)
                elif received[3] == 'CREATED SUCCESSFULLY':
                    clientPrint(received[3], Fore.YELLOW)
                elif received[3] == 'ALREADY IN CHANNEL':
                    clientPrint(received[3], Fore.YELLOW)
                

                elif received[2] == 'ASK TO JOIN CHANNEL':
                    client_socket.send(ChannelProtocol(received[1], 'JOIN CHANNEL','?').encode())

        # In case client left the chat
        except Exception as ex:
            print("except Number 1")
            print(ex)
            break

def send():
    while True:
        msg = input()
        # Skip input that has nothing in it
        if len(msg) > 0:
            # User entered command
            if msg[0] == '/':
                if msg == '/quit':
                    client_socket.close()
                    break
                elif msg[:6] == '/join ':
                    joinTo = msg[6:]
                    if ' ' not in joinTo:
                        client_socket.send(ChannelProtocol(joinTo, 'JOIN CHANNEL', '?').encode())
                    else:
                        clientPrint("A channel name can't contain spaces! Try again", Fore.RED)
                elif msg[:8] == '/create ':
                    channelName = msg[8:]
                    if ' ' not in channelName:   
                        client_socket.send(ChannelProtocol(channelName, 'CREATE CHANNEL', '?').encode())
                    else:
                        clientPrint("A channel name can't contain spaces! Try again", Fore.RED)
                elif msg[:8] == '/delete ':
                    channelName = msg[8:]
                    if ' ' not in channelName:
                        client_socket.send(ChannelProtocol(channelName,'DELETE CHANNEL', '?').encode())
                    else:
                        clientPrint("A channel name can't contain spaces! Try again", Fore.RED)
                else:
                    clientPrint('INVALID COMMAND!', Fore.RED)
            # User entered a message to send
            else:
                client_socket.send(MSGProtocol(msg).encode())

def event_handler():
    ui.LoginButton.clicked.connect(lambda: sys.exit())


# CONST VARIABLES
HOST = '127.0.0.1'
PORT = 55556
BUFFRESIZE = 1024
ADDR = (HOST,PORT)

client_socket = socket(AF_INET, SOCK_STREAM)

# Clear console
os.system('cls')

app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = untitled.Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.setFixedSize(1280,720)
ui.stackedWidget.setCurrentIndex(0)
ui.tabWidget.setCurrentIndex(0)
MainWindow.show()
event_handler()
sys.exit(app.exec_())


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
    ans = ProtocolDeconstruct(client_socket.recv(BUFFRESIZE).decode())
    if ans[5] == 'GOOD LOGIN' or ans[5] == 'GOOD REGISTER':
        notLoggedIn = False
        receive_thread = Thread(target=receive, daemon=True)
        receive_thread.start()
        send_thread = Thread(target=send, daemon=True)
        send_thread.start()
        # Join means that the main script follows into send_thread => doesn't end until send_thread closes
        send_thread.join()
    elif ans[5] == 'BAD LOGIN':
        print('Account doesnt exist')
    elif ans[5] == 'BAD REGISTER':
        print('Username already taken!')
    else: 
        print('Server is not responding')
        break