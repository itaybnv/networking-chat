from PyQt5 import QtCore, QtGui, QtWidgets
import untitled, client
import sys, os
from socket import *
from threading import Thread
from datetime import datetime

def initClient(ip):


def main():
    # Client init

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = untitled.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.setFixedSize(1280,720)
    ui.stackedWidget.setCurrentIndex(0)
    ui.tabWidget.setCurrentIndex(0)
    ui.LoginButton.clicked.connect(lambda: initClient(ui.IPInput.text()))
    MainWindow.show()
    eventhandler = event_handler()
    sys.exit(app.exec_())
    

if __name__ == "__main__":
    
    PORT = 55556
    BUFFRESIZE = 1024

    client_socket = socket(AF_INET, SOCK_STREAM)

    os.system('cls')

    temp = client.getServer()
    HOST = temp if temp else '127.0.0.1'
    ADDR = (HOST, PORT)

    main()

