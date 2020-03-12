#!/usr/bin/python3
import sys, datetime
from SocketTool import SocketTool

#Qt
from PySide2.QtCore import Qt, Slot, QTimer, QDateTime 
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout
from PySide2.QtWidgets import QLabel, QLineEdit, QCheckBox, QPushButton
from PySide2.QtCharts import QtCharts
from PySide2.QtGui import QPainter

default_ip ='169.254.50.194'
sample_interval_secs = 2.5

class MDO3000(object):
    def __init__(self, ip):
        port = 4000 #default port for socket control
        self.MySocket = SocketTool(ip, port, "\n")

        self.channel = 1

    def getIdent(self):
        ident_string = self.MySocket.send_receive_string('*IDN?')
        return ident_string.strip()

'''
#Example usage:
MDO = MDO3000("169.254.5.157")
print(MDO.getIdent())
'''

'''
   _____ _    _ _____       _______ _    _ _____  ______          _____  
  / ____| |  | |_   _|     |__   __| |  | |  __ \|  ____|   /\   |  __ \ 
 | |  __| |  | | | |          | |  | |__| | |__) | |__     /  \  | |  | |
 | | |_ | |  | | | |          | |  |  __  |  _  /|  __|   / /\ \ | |  | |
 | |__| | |__| |_| |_         | |  | |  | | | \ \| |____ / ____ \| |__| |
  \_____|\____/|_____|        |_|  |_|  |_|_|  \_\______/_/    \_\_____/ 
                                                                         
'''

class MyWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.ip = default_ip
        layout_final = QVBoxLayout()

        #layout: ip and connect checkbox
        text = QLabel("IPv4 Address:", self)
        text.setAlignment(Qt.AlignCenter)
        self.ip_input = QLineEdit(self.ip, self)
        self.checkbox = QCheckBox("connect", self)

        layout = QHBoxLayout()
        layout.addWidget(text)
        layout.addWidget(self.ip_input)
        layout.addWidget(self.checkbox)
        layout_final.addLayout(layout)

        #layout: Name
        text = QLabel("Name:", self)
        text.setAlignment(Qt.AlignRight)
        self.name = QLabel("", self)

        layout = QHBoxLayout()
        layout.addWidget(text)
        layout.addWidget(self.name)
        layout_final.addLayout(layout)

        #layout: Time
        text = QLabel("Time:", self)
        text.setAlignment(Qt.AlignRight)
        self.time = QLabel("", self)

        layout = QHBoxLayout()
        layout.addWidget(text)
        layout.addWidget(self.time)
        layout_final.addLayout(layout)

        self.setLayout(layout_final)

        #signal and slot
        self.ip_input.returnPressed.connect(self.update_ip)
        self.checkbox.stateChanged.connect(self.connect)

    @Slot()
    def update_ip(self):
        self.ip = self.ip_input.text()

    @Slot()
    def connect(self):
        if self.checkbox.isChecked():
            print("connecting " + self.ip)
            self.MDO = MDO3000(self.ip)
            self.name.setText(self.MDO.getIdent())

            dtime = datetime.datetime.now()
            self.time.setText(dtime.strftime('%c'))

        else:
            print("disconnecting...")
            del self.MDO

            self.name.setText("")
            print("disconnect successfully.")

class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("MDO3000 Series Remote Control")
        self.setCentralWidget(widget)

'''
   _____ _______       _____ _______                 _____  _____  
  / ____|__   __|/\   |  __ \__   __|          /\   |  __ \|  __ \ 
 | (___    | |  /  \  | |__) | | |            /  \  | |__) | |__) |
  \___ \   | | / /\ \ |  _  /  | |           / /\ \ |  ___/|  ___/ 
  ____) |  | |/ ____ \| | \ \  | |          / ____ \| |    | |     
 |_____/   |_/_/    \_\_|  \_\ |_|         /_/    \_\_|    |_|     
                                                                   
'''

if __name__ == '__main__':
    if True:
    #if False:
        app = QApplication([])
 
        widget = MyWidget()
        window = MainWindow(widget)
        window.resize(800, 800)
        window.show()
 
        sys.exit(app.exec_())
