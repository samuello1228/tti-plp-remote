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
sample_interval_secs = 0.5

class MDO3000(object):
    def __init__(self, ip):
        port = 4000 #default port for socket control
        self.MySocket = SocketTool(ip, port, "\n")
        self.clear()

    def getIdent(self):
        ident_string = self.MySocket.send_receive_string('*IDN?')
        return ident_string.strip()

    def clear(self):
        print("setting protocol Terminal")
        print(self.MySocket.send_receive_string("SocketServer:protocol terminal","> "))
        print("protocol Terminal has already been set")

        print("sending !d")
        print(self.MySocket.send_receive_string('!d',"> "))
        print("!d has already been sent")

        print("setting protocol None")
        print(self.MySocket.send_only("SocketServer:protocol none"))
        print("protocol None has already been set")

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
        self.nPoint = 1000
        self.nChannel = 4
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

        #layout: ChartView
        chartView = QtCharts.QChartView()
        layout_final.addWidget(chartView)

        self.setLayout(layout_final)

        #signal and slot
        self.ip_input.returnPressed.connect(self.update_ip)
        self.checkbox.stateChanged.connect(self.connect)

        #Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)

        #Line Chart
        chart = QtCharts.QChart()
        self.series = []
        for i in range(self.nChannel):
            self.series.append(QtCharts.QLineSeries())
            chart.addSeries(self.series[i])
            for j in range(self.nPoint):
                self.series[i].append(0,0)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignTop)
        markers = chart.legend().markers()
        for i in range(self.nChannel):
            markers[i].setLabel("Ch{0}".format(i+1))

        self.axisX = QtCharts.QValueAxis()
        self.axisX.setTickCount(9)
        self.axisX.setLabelFormat("%.1e")
        self.axisX.setTitleText("Time (s)")
        self.axisX.setRange(-1e-7,3e-7)
        chart.addAxis(self.axisX, Qt.AlignBottom)
        for i in range(self.nChannel):
            self.series[i].attachAxis(self.axisX)

        self.axisY = QtCharts.QValueAxis()
        self.axisY.setTickCount(11)
        self.axisY.setLabelFormat("%.1e")
        self.axisY.setTitleText("Voltage (V)")
        self.axisY.setRange(-5e-3,5e-3)
        chart.addAxis(self.axisY, Qt.AlignLeft)
        for i in range(self.nChannel):
            self.series[i].attachAxis(self.axisY)
        
        chartView.setChart(chart)
        chartView.setRenderHint(QPainter.Antialiasing)

    @Slot()
    def update_ip(self):
        self.ip = self.ip_input.text()

    @Slot()
    def connect(self):
        if self.checkbox.isChecked():
            print("connecting " + self.ip)
            self.timer.start(sample_interval_secs *1000)
            self.MDO = MDO3000(self.ip)
            self.name.setText(self.MDO.getIdent())

            dtime = datetime.datetime.now()
            self.time.setText(dtime.strftime('%c'))
            
            self.isShowChannel = []
            for i in range(self.nChannel):
                self.isShowChannel.append(bool(int(self.MDO.MySocket.send_receive_string("Select:Ch{0}?".format(i+1)))))

            self.MDO.MySocket.send_only("data:source CH1")
            self.MDO.MySocket.send_only("data:start 1")
            self.MDO.MySocket.send_only("data:stop {0}".format(self.nPoint))
            self.MDO.MySocket.send_only("data:encdg ascii")
            self.MDO.MySocket.send_only("data:width 1")
            #self.MDO.MySocket.send_only("data:width 2")
            
            self.MDO.MySocket.send_only("ACQuire:STOPAfter RunStop")
            #self.MDO.MySocket.send_only("ACQuire:STOPAfter sequence")

            #self.MDO.MySocket.send_only(":header 1")
            #self.MDO.MySocket.send_only("verbose on")
            #print(self.MDO.MySocket.send_receive_string("WfmOutPre?"))
            #self.MDO.MySocket.send_only("header 0")

            wfid = self.MDO.MySocket.send_receive_string("WfmOutPre:wfid?")

            #remove quotation mark
            wfid = wfid[1:-1].split(", ")
            print(wfid)

            #remove mV/div
            self.YDiv = float(wfid[2][:-6]) * 1E-3
            print("YDiv:", self.YDiv, "V/div")

            #x-axis
            self.XINCR = float(self.MDO.MySocket.send_receive_string("WfmOutPre:XINCR?"))
            print("XINCR:", self.XINCR)
            self.XZERO = float(self.MDO.MySocket.send_receive_string("WfmOutPre:XZERO?"))
            print("XZERO:", self.XZERO)
            self.axisX.setRange(self.XZERO, self.XZERO + self.XINCR * self.nPoint)

            #y-axis
            self.YMULT = float(self.MDO.MySocket.send_receive_string("WfmOutPre:YMULT?"))
            print("YMULT:", self.YMULT)
            self.YOFF = int(float(self.MDO.MySocket.send_receive_string("WfmOutPre:YOFF?")))
            print("YOFF:", self.YOFF)
            self.YZERO = float(self.MDO.MySocket.send_receive_string("WfmOutPre:YZERO?"))
            print("YZERO:", self.YZERO)
            self.axisY.setRange(self.YDiv *-5, self.YDiv *5)

        else:
            print("disconnecting...")
            self.timer.stop()
            del self.MDO

            self.name.setText("")
            print("disconnect successfully.")

    @Slot()
    def update_data(self):
        dtime = datetime.datetime.now()
        self.time.setText(dtime.strftime('%c'))

        data = []
        YMULT = []
        YOFF = []
        YZERO = []
        for i in range(len(self.isShowChannel)):
            if self.isShowChannel[i]:
                self.MDO.MySocket.send_only("data:source CH{0}".format(i+1))

                #self.MDO.MySocket.send_only(":header 1")
                #self.MDO.MySocket.send_only("verbose on")
                #print(self.MDO.MySocket.send_receive_string("WfmOutPre?"))
                #self.MDO.MySocket.send_only("header 0")

                #get waveform
                data.append(self.MDO.MySocket.send_receive_string("curve?"))
                YMULT.append(float(self.MDO.MySocket.send_receive_string("WfmOutPre:YMULT?")))
                YOFF.append(int(float(self.MDO.MySocket.send_receive_string("WfmOutPre:YOFF?"))))
                YZERO.append(float(self.MDO.MySocket.send_receive_string("WfmOutPre:YZERO?")))
            else:
                data.append("")
                YMULT.append(0)
                YOFF.append(0)
                YZERO.append(0)

        for i in range(len(self.isShowChannel)):
            if self.isShowChannel[i]:
                data[i] = data[i].split(",")

                x = self.XZERO
                index = 0
                for element in data[i]:
                    y = ( (int(element) - YOFF[i]) * YMULT[i] ) + YZERO[i]
                    #print(x,y)
                    self.series[i].replace(index,x,y)
          
                    index += 1
                    x += self.XINCR

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
        window.resize(1200, 800)
        window.show()
 
        sys.exit(app.exec_())
