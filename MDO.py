#!/usr/bin/python3
import sys, datetime
from SocketTool import SocketTool

#Qt
from PySide2.QtCore import Qt, Slot, QTimer, QDateTime 
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout
from PySide2.QtWidgets import QLabel, QLineEdit, QCheckBox, QPushButton, QComboBox, QTableWidget, QTableWidgetItem
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
        print(self.MySocket.send_receive_string("SocketServer:protocol terminal", "> ", True))
        print("protocol Terminal has already been set")

        print("sending !d")
        print(self.MySocket.send_receive_string('!d', "Sending device clear\r\n> ", True))
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
        self.nRow = 4
        layout_final = QVBoxLayout()

        #layout: ip and connect checkbox
        text = QLabel("IPv4 Address:", self)
        text.setAlignment(Qt.AlignCenter)
        self.ip_input = QLineEdit(self.ip, self)
        self.connect_input = QCheckBox("connect", self)

        layout = QHBoxLayout()
        layout.addWidget(text)
        layout.addWidget(self.ip_input)
        layout.addWidget(self.connect_input)
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

        #layout: Horizontal
        text = QLabel("Horizontal: Scale (second per division):", self)
        self.x_scale_output = QLineEdit("", self)
        self.x_scale_input_zoom_in = QPushButton("+",self)
        self.x_scale_input_zoom_out = QPushButton("-",self)

        layout = QHBoxLayout()
        layout.addWidget(text)
        layout.addWidget(self.x_scale_output)
        layout.addWidget(self.x_scale_input_zoom_in)
        layout.addWidget(self.x_scale_input_zoom_out)
        layout_final.addLayout(layout)

        #layout: Vertical
        text1 = QLabel("Vertical: Channel:", self)
        self.y_channel_input = QComboBox(self)
        for i in range(self.nChannel):
            self.y_channel_input.insertItem(i, "Ch{0}".format(i+1))
        self.y_enabled = QCheckBox("Enabled", self)

        text2 = QLabel("Coupling:", self)
        self.y_coupling = QComboBox(self)
        self.y_coupling.insertItem(0, "DC")
        self.y_coupling.insertItem(1, "AC")

        text3 = QLabel("Scale (V per division):", self)
        self.y_scale_output = QLineEdit("", self)
        self.y_scale_input_zoom_in = QPushButton("+",self)
        self.y_scale_input_zoom_out = QPushButton("-",self)

        layout = QHBoxLayout()
        layout.addWidget(text1)
        layout.addWidget(self.y_channel_input)
        layout.addWidget(self.y_enabled)
        layout.addWidget(text2)
        layout.addWidget(self.y_coupling)
        layout.addWidget(text3)
        layout.addWidget(self.y_scale_output)
        layout.addWidget(self.y_scale_input_zoom_in)
        layout.addWidget(self.y_scale_input_zoom_out)
        layout_final.addLayout(layout)

        #layout: Measurement config
        text1 = QLabel("Measurement:", self)
        text2 = QLabel("Row:", self)
        text2.setAlignment(Qt.AlignRight)
        self.measurement_row_input = QComboBox(self)
        for i in range(self.nRow):
            self.measurement_row_input.insertItem(i, str(i+1))
        self.measurement_row_input.setCurrentText("1")

        self.measurement_enabled = QCheckBox("Enabled", self)

        text3 = QLabel("Channel:", self)
        text3.setAlignment(Qt.AlignRight)
        self.measurement_channel_input = QComboBox(self)
        for i in range(self.nChannel):
            self.measurement_channel_input.insertItem(i, "CH{0}".format(i+1))

        text4 = QLabel("Type:", self)
        text4.setAlignment(Qt.AlignRight)
        self.measurement_type_input = QComboBox(self)
        self.measurement_type_input.insertItem(0, "MEAN")
        self.measurement_type_input.insertItem(1, "RMS")

        layout = QHBoxLayout()
        layout.addWidget(text1)
        layout.addWidget(text2)
        layout.addWidget(self.measurement_row_input)
        layout.addWidget(self.measurement_enabled)
        layout.addWidget(text3)
        layout.addWidget(self.measurement_channel_input)
        layout.addWidget(text4)
        layout.addWidget(self.measurement_type_input)
        layout_final.addLayout(layout)

        #layout: ChartView
        chartView = QtCharts.QChartView()
        layout_final.addWidget(chartView)

        #layout: Measurement table
        self.measurement_table = QTableWidget(self)
        self.measurement_table.setRowCount(self.nRow)

        self.measurement_statistics_list = ["Value", "Mean", "Minimum", "Maximum", "StdDev"]
        self.measurement_table.setColumnCount(2+len(self.measurement_statistics_list))
        self.measurement_table.setHorizontalHeaderItem(0, QTableWidgetItem("Channel"))
        self.measurement_table.setHorizontalHeaderItem(1, QTableWidgetItem("Type"))

        for i in range(len(self.measurement_statistics_list)):
            self.measurement_table.setHorizontalHeaderItem(2+i, QTableWidgetItem(self.measurement_statistics_list[i]))
        layout_final.addWidget(self.measurement_table)

        self.setLayout(layout_final)

        #signal and slot
        self.ip_input.returnPressed.connect(self.update_ip)
        self.connect_input.stateChanged.connect(self.connect)

        self.x_scale_input_zoom_in.clicked.connect(self.x_scale_zoom_in)
        self.x_scale_input_zoom_out.clicked.connect(self.x_scale_zoom_out)
        self.x_scale_output.returnPressed.connect(self.set_x_scale)

        self.y_channel_input.activated.connect(self.update_channel)
        self.y_enabled.clicked.connect(self.channel_enabled)
        self.y_coupling.activated.connect(self.set_coupling)
        self.y_scale_input_zoom_in.clicked.connect(self.y_scale_zoom_in)
        self.y_scale_input_zoom_out.clicked.connect(self.y_scale_zoom_out)
        self.y_scale_output.returnPressed.connect(self.set_y_scale)

        self.measurement_row_input.activated.connect(self.update_measurement_config)
        self.measurement_enabled.clicked.connect(self.enable_measurement)
        self.measurement_channel_input.activated.connect(self.update_measurement_channel)
        self.measurement_type_input.activated.connect(self.update_measurement_type)

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
        self.axisX.setTickCount(11)
        self.axisX.setLabelFormat("%.1e")
        self.axisX.setTitleText("Time (s)")
        self.axisX.setRange(-2e-3,2e-3)
        chart.addAxis(self.axisX, Qt.AlignBottom)
        for i in range(self.nChannel):
            self.series[i].attachAxis(self.axisX)

        self.axisY = QtCharts.QValueAxis()
        self.axisY.setTickCount(11)
        self.axisY.setLabelFormat("%.1e")
        self.axisY.setTitleText("Voltage Division")
        self.axisY.setRange(-5,5)
        self.axisY.setLabelsVisible(False)
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
        if self.connect_input.isChecked():
            print("connecting " + self.ip)
            self.timer.start(sample_interval_secs *1000)
            self.MDO = MDO3000(self.ip)
            self.name.setText(self.MDO.getIdent())

            dtime = datetime.datetime.now()
            self.time.setText(dtime.strftime('%c'))
            
            self.isShowChannel = []
            for i in range(self.nChannel):
                self.isShowChannel.append(bool(int(self.MDO.MySocket.send_receive_string("Select:Ch{0}?".format(i+1)))))

            self.x_scale_output.setText(self.MDO.MySocket.send_receive_string("horizontal:scale?"))
            self.update_channel()

            self.MDO.MySocket.send_only("data:source CH1")
            self.MDO.MySocket.send_only("data:start 1")
            self.MDO.MySocket.send_only("data:stop {0}".format(self.nPoint))
            self.MDO.MySocket.send_only("data:encdg ascii")
            self.MDO.MySocket.send_only("data:width 1")
            #self.MDO.MySocket.send_only("data:width 2")
            
            self.MDO.MySocket.send_only("ACQuire:STOPAfter RunStop")
            #self.MDO.MySocket.send_only("ACQuire:STOPAfter sequence")

            #measurement
            self.measurement_channel_list = []
            self.measurement_type_list = []
            for i in range(self.nRow):
                channel = self.MDO.MySocket.send_receive_string("Measurement:Meas{0}:source?".format(i+1))
                self.measurement_channel_list.append(channel)
                Type = self.MDO.MySocket.send_receive_string("Measurement:Meas{0}:type?".format(i+1))
                self.measurement_type_list.append(Type)

            #measurement config
            self.update_measurement_config()

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

        #waveform chart
        data = []
        YMULT = []
        YOFF = []
        YZERO = []
        YDiv = []
        for i in range(len(self.isShowChannel)):
            if self.isShowChannel[i]:
                self.MDO.MySocket.send_only("data:source CH{0}".format(i+1))

                #self.MDO.MySocket.send_only(":header 1")
                #self.MDO.MySocket.send_only("verbose on")
                #print(self.MDO.MySocket.send_receive_string("WfmOutPre?"))
                #self.MDO.MySocket.send_only("header 0")

                #x-axis
                self.XINCR = float(self.MDO.MySocket.send_receive_string("WfmOutPre:XINCR?"))
                self.XZERO = float(self.MDO.MySocket.send_receive_string("WfmOutPre:XZERO?"))
                self.axisX.setRange(self.XZERO, self.XZERO + self.XINCR * self.nPoint)

                #y-axis
                data.append(self.MDO.MySocket.send_receive_string("curve?"))
                YMULT.append(float(self.MDO.MySocket.send_receive_string("WfmOutPre:YMULT?")))
                YOFF.append(int(float(self.MDO.MySocket.send_receive_string("WfmOutPre:YOFF?"))))
                YZERO.append(float(self.MDO.MySocket.send_receive_string("WfmOutPre:YZERO?")))
                YDiv.append(float(self.MDO.MySocket.send_receive_string("CH{0}:scale?".format(i+1))))
            else:
                data.append("")
                YMULT.append(0)
                YOFF.append(0)
                YZERO.append(0)
                YDiv.append(0)

        for i in range(len(self.isShowChannel)):
            if self.isShowChannel[i]:
                data[i] = data[i].split(",")

                x = self.XZERO
                index = 0
                for element in data[i]:
                    y = ( (int(element) - YOFF[i]) * YMULT[i] ) + YZERO[i]
                    y = y/YDiv[i]
                    #print(x,y)
                    self.series[i].replace(index,x,y)
          
                    index += 1
                    x += self.XINCR

        #layout: Measurement table
        for i in range(self.nRow):
            self.measurement_table.setItem(i, 0, QTableWidgetItem(self.measurement_channel_list[i]))
            self.measurement_table.setItem(i, 1, QTableWidgetItem(self.measurement_type_list[i]))

            state = self.MDO.MySocket.send_receive_string("Measurement:Meas{0}:state?".format(i+1))
            if state == "1":
                unit = self.MDO.MySocket.send_receive_string("Measurement:Meas{0}:units?".format(i+1))
                unit = unit[1:]
                unit = unit[:-1]
                for j in range(len(self.measurement_statistics_list)):
                    value = self.MDO.MySocket.send_receive_string("Measurement:Meas{0}:".format(i+1) + self.measurement_statistics_list[j] + "?")
                    self.measurement_table.setItem(i, 2+j, QTableWidgetItem(value + " " + unit))

    @Slot()
    def x_scale_zoom_in(self):
        if self.connect_input.isChecked():
            self.MDO.MySocket.send_only("FPanel:turn HorzScale, 1")
            self.x_scale_output.setText(self.MDO.MySocket.send_receive_string("horizontal:scale?"))

    @Slot()
    def x_scale_zoom_out(self):
        if self.connect_input.isChecked():
            self.MDO.MySocket.send_only("FPanel:turn HorzScale, -1")
            self.x_scale_output.setText(self.MDO.MySocket.send_receive_string("horizontal:scale?"))

    @Slot()
    def set_x_scale(self):
        if self.connect_input.isChecked():
            self.MDO.MySocket.send_only("horizontal:scale " + self.x_scale_output.text())
            self.x_scale_output.setText(self.MDO.MySocket.send_receive_string("horizontal:scale?"))

    @Slot()
    def update_channel(self):
        if self.connect_input.isChecked():
            channel_string = self.y_channel_input.currentText()
            isEnabled = self.MDO.MySocket.send_receive_string("Select:" + channel_string + "?")

            #enabled
            if isEnabled == "0":
                self.y_enabled.setCheckState(Qt.Unchecked)
            elif isEnabled == "1":
                self.y_enabled.setCheckState(Qt.Checked)

            #coupling
            self.y_coupling.setCurrentText(self.MDO.MySocket.send_receive_string(channel_string + ":coupling?"))

            #vertical scale
            self.y_scale_output.setText(self.MDO.MySocket.send_receive_string(channel_string + ":scale?"))

    @Slot()
    def channel_enabled(self):
        if self.connect_input.isChecked():
            channel_string = self.y_channel_input.currentText()
            channel_index = int(channel_string[-1:]) -1
            if self.y_enabled.isChecked():
                self.MDO.MySocket.send_only("Select:" + channel_string + " on")
                self.isShowChannel[channel_index] = True
            else:
                self.isShowChannel[channel_index] = False
                self.MDO.MySocket.send_only("Select:" + channel_string + " off")
                for i in range(self.nPoint):
                    self.series[channel_index].replace(i,0,0)

    @Slot()
    def set_coupling(self):
        if self.connect_input.isChecked():
            channel_string = self.y_channel_input.currentText()
            channel_index = int(channel_string[-1:]) -1
            if self.isShowChannel[channel_index]:
                self.MDO.MySocket.send_only(channel_string + ":coupling " + self.y_coupling.currentText())

    @Slot()
    def y_scale_zoom_in(self):
        if self.connect_input.isChecked():
            channel_string = self.y_channel_input.currentText()
            channel_index = int(channel_string[-1:]) -1
            if self.isShowChannel[channel_index]:
                self.MDO.MySocket.send_only("FPanel:turn VertScale" + channel_string[-1:] + ", 1")
                self.y_scale_output.setText(self.MDO.MySocket.send_receive_string(channel_string + ":scale?"))

    @Slot()
    def y_scale_zoom_out(self):
        if self.connect_input.isChecked():
            channel_string = self.y_channel_input.currentText()
            channel_index = int(channel_string[-1:]) -1
            if self.isShowChannel[channel_index]:
                self.MDO.MySocket.send_only("FPanel:turn VertScale" + channel_string[-1:] + ", -1")
                self.y_scale_output.setText(self.MDO.MySocket.send_receive_string(channel_string + ":scale?"))

    @Slot()
    def set_y_scale(self):
        if self.connect_input.isChecked():
            channel_string = self.y_channel_input.currentText()
            channel_index = int(channel_string[-1:]) -1
            if self.isShowChannel[channel_index]:
                self.MDO.MySocket.send_only(channel_string + ":scale " + self.y_scale_output.text())
                self.y_scale_output.setText(self.MDO.MySocket.send_receive_string(channel_string + ":scale?"))

    @Slot()
    def update_measurement_config(self):
        if self.connect_input.isChecked():
            state = self.MDO.MySocket.send_receive_string("Measurement:Meas" + self.measurement_row_input.currentText() + ":state?")
            if state == "0":
                self.measurement_enabled.setCheckState(Qt.Unchecked)
            elif state == "1":
                self.measurement_enabled.setCheckState(Qt.Checked)

            channel = self.MDO.MySocket.send_receive_string("Measurement:Meas" + self.measurement_row_input.currentText() + ":source?")
            self.measurement_channel_input.setCurrentText(channel)
            Type = self.MDO.MySocket.send_receive_string("Measurement:Meas" + self.measurement_row_input.currentText() + ":type?")
            self.measurement_type_input.setCurrentText(Type)

    @Slot()
    def enable_measurement(self):
        if self.connect_input.isChecked():
            row_string = self.measurement_row_input.currentText()
            index = int(row_string) -1
            if self.measurement_enabled.isChecked():
                self.MDO.MySocket.send_only("Measurement:Meas" + row_string + ":state on")
            else:
                self.MDO.MySocket.send_only("Measurement:Meas" + row_string + ":state off")
                for j in range(len(self.measurement_statistics_list)):
                    self.measurement_table.setItem(index, 2+j, QTableWidgetItem(""))

    @Slot()
    def update_measurement_channel(self):
        if self.connect_input.isChecked():
            row_string = self.measurement_row_input.currentText()
            index = int(row_string) -1
            self.MDO.MySocket.send_only("Measurement:Meas" + row_string + ":source " + self.measurement_channel_input.currentText())
            self.measurement_channel_list[index] = self.measurement_channel_input.currentText()

    @Slot()
    def update_measurement_type(self):
        if self.connect_input.isChecked():
            row_string = self.measurement_row_input.currentText()
            index = int(row_string) -1
            self.MDO.MySocket.send_only("Measurement:Meas" + row_string + ":type " + self.measurement_type_input.currentText())
            self.measurement_type_list[index] = self.measurement_type_input.currentText()

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
