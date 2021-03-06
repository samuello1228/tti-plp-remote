#!/usr/bin/python3
import sys, datetime
from SocketTool import SocketTool
from random import seed, gauss

#Qt
from PySide2.QtCore import Qt, Slot, QTimer, QDateTime 
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout
from PySide2.QtWidgets import QLabel, QLineEdit, QCheckBox, QPushButton
from PySide2.QtCharts import QtCharts
from PySide2.QtGui import QPainter

isEmulate = False
#isEmulate = True

default_psu_ip ='169.254.100.78'
sample_interval_secs = 2.5

max_volt_setting = 30.0
max_milliamp_setting = 3000

class ttiPsu(object):

    def __init__(self, ip, channel=1):
        port = 9221 #default port for socket control
        self.MySocket = SocketTool(ip, port, "\r\n")

        #channel=1 for single PSU and right hand of Dual PSU
        self.channel = channel

        if isEmulate:
            self.identity_emulate = "My Power Supply"
            self.target_volts_emulate = 12.0
            self.target_amps_emulate = 0.5
            self.is_enabled_emulate = False
            self.amp_range_emulate = 1

            self.resistance_emulate = 33.0
            self.out_volts_emulate = 0.0

            seed(1)

    def send_receive_float(self, cmd):
        r = self.MySocket.send_receive_string(cmd)
        #Eg. '-0.007V\r\n'  '31.500\r\n'  'V2 3.140\r\n'
        r=r.rstrip('\r\nVA') #Strip these trailing chars
        l=r.rsplit() #Split to array of strings
        if len(l) > 0:
            return float(l[-1]) #Convert number in last string to float
        return 0.0

    def send_receive_integer(self, cmd):
        r = self.MySocket.send_receive_string(cmd)
        return int(r)

    def send_receive_boolean(self, cmd):
        if self.send_receive_integer(cmd) > 0:
            return True
        return False

    def getIdent(self):
        if isEmulate:
            return self.identity_emulate
        else:
            ident_string = self.MySocket.send_receive_string('*IDN?')
            return ident_string.strip()

    '''
    def getConfig(self):
        cmd = 'CONFIG?'
        v = self.send_receive_integer(cmd)
        return v
    '''

    def getAmpRange(self):
        if isEmulate:
            return self.amp_range_emulate
        else:
            #Supported on PL series
            #Not supported on MX series
            r=0
            try:
                cmd = 'IRANGE{}?'.format(self.channel)
                r = self.send_receive_integer(cmd)
            except:
                pass
            #The response is 1 for Low (500/800mA) range,
            # 2 for High range (3A or 6A parallel)
            # or 0 for no response / not supported
            return r

    def setAmpRangeLow(self):
        if isEmulate:
            self.amp_range_emulate = 1
        else:
            #Supported on PL series
            #Not supported on MX series
            cmd = 'IRANGE{} 1'.format(self.channel)
            self.MySocket.send_only(cmd)

    def setAmpRangeHigh(self):
        if isEmulate:
            self.amp_range_emulate = 2
        else:
            #Supported on PL series
            #Not supported on MX series
            cmd = 'IRANGE{} 2'.format(self.channel)
            self.send_only(cmd)

    def getOutputIsEnabled(self):
        if isEmulate:
            v = self.is_enabled_emulate
        else:
            cmd = 'OP{}?'.format(self.channel)
            v = self.send_receive_boolean(cmd)
        return v

    def getOutputVolts(self):
        if isEmulate:
            if self.is_enabled_emulate:
                v = gauss(self.target_volts_emulate, 0.1)
                self.out_volts_emulate = v
            else:
                v = 0
        else:
            cmd = 'V{}O?'.format(self.channel)
            v = self.send_receive_float(cmd)
        return v

    def getOutputAmps(self):
        if isEmulate:
            if self.is_enabled_emulate:
                v = self.out_volts_emulate / self.resistance_emulate
            else:
                v = 0
        else:
            cmd = 'I{}O?'.format(self.channel)
            v = self.send_receive_float(cmd)
        return v

    def getTargetVolts(self):
        if isEmulate:
            v = self.target_volts_emulate
        else:
            cmd = 'V{}?'.format(self.channel)
            v = self.send_receive_float(cmd)
        return v

    def getTargetAmps(self):
        if isEmulate:
            v = self.target_amps_emulate
        else:
            cmd = 'I{}?'.format(self.channel)
            v = self.send_receive_float(cmd)
        return v

    '''
    def getOverVolts(self):
        cmd = 'OVP{}?'.format(self.channel)
        v = self.send_receive_float(cmd)
        return v

    def getOverAmps(self):
        cmd = 'OCP{}?'.format(self.channel)
        v = self.send_receive_float(cmd)
        return v
    '''

    def setOutputEnable(self, ON):
        if isEmulate:
            if ON == True:
                self.is_enabled_emulate = True
            else:
                self.is_enabled_emulate = False
        else:
            cmd=''
            if ON == True:
                cmd = 'OP{} 1'.format(self.channel)
            else:
                cmd = 'OP{} 0'.format(self.channel)
            self.MySocket.send_only(cmd)

    def setTargetVolts(self, volts):
        if isEmulate:
            self.target_volts_emulate = volts
        else:
            cmd = 'V{0} {1:2.3f}'.format(self.channel, volts)
            self.MySocket.send_only(cmd)

    def setTargetAmps(self, amps):
        if isEmulate:
            self.target_amps_emulate = amps
        else:
            cmd = 'I{0} {1:1.3f}'.format(self.channel, amps)
            self.MySocket.send_only(cmd)

    def setLocal(self):
        if isEmulate:
            pass
        else:
            cmd = 'LOCAL'
            self.MySocket.send_only(cmd)

    def GetData(self):
        # Gather data from PSU
        identity = self.getIdent()
        out_volts = self.getOutputVolts()
        out_amps = self.getOutputAmps()
        target_volts = self.getTargetVolts()
        target_amps = self.getTargetAmps()
        is_enabled = self.getOutputIsEnabled()
        amp_range = self.getAmpRange()
        dataset = DataToGui(identity,
                                out_volts, out_amps,
                                target_volts, target_amps,
                                is_enabled, amp_range)
        return dataset


'''
#Example usage:
tti = ttiPsu('192.168.128.30', channel=2)
print(tti.getIdent())
print('Output: {0:2.2f} V'.format(tti.getOutputVolts()))
print('Output: {0:2.2f} A'.format(tti.getOutputAmps()))
print('OverV: {0:2.2f} V'.format(tti.getOverVolts()))
print('OverI: {0:2.2f} A'.format(tti.getOverAmps()))
print('Config: {}'.format(tti.getConfig()))
print('isEnabled: {}'.format(tti.getOutputIsEnabled()))
print('AmpRange: {}'.format(tti.getAmpRange()))
print('TargetV: {0:2.2f} V'.format(tti.getTargetVolts()))
print('TargetI: {0:2.2f} A'.format(tti.getTargetAmps()))

tti.setTargetVolts(3.14)
tti.setTargetAmps(1.234)
tti.setOutputEnable(True)
tti.setAmpRangeHigh()
tti.setLocal()
'''

class DataToGui(object):
    def __init__(self, identity, out_volts, out_amps, target_volts, target_amps, is_enabled, amp_range):
        self.identity = identity
        self.out_volts = out_volts
        self.out_amps = out_amps
        self.target_volts = target_volts
        self.target_amps = target_amps
        self.is_enabled = is_enabled
        self.amp_range = amp_range
        
    def print(self):
        print('Name: ' + self.identity)
        print('isEnabled: {}'.format(self.is_enabled))
        print('Target Voltage: {0:.3f} V'.format(self.target_volts))
        print('Current Limit: {0} mA'.format(int(self.target_amps*1000)))
        print('Output Voltage: {0:.3f} V'.format(self.out_volts))
        print('Output Current: {0} mA'.format(int(self.out_amps*1000)))
        print('')

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

        self.ip = default_psu_ip
        self.channel = 1
        layout_final = QVBoxLayout()

        #left top: ip
        text = QLabel("IPv4 Address:", self)
        text.setAlignment(Qt.AlignCenter)
        self.ip_input = QLineEdit(self.ip, self)

        top = QHBoxLayout()
        top.addWidget(text)
        top.addWidget(self.ip_input)

        #left bottom: channel
        text = QLabel("Channel:", self)
        self.channel_input = QLineEdit("{0}".format(self.channel), self)

        bottom = QHBoxLayout()
        bottom.addWidget(text)
        bottom.addWidget(self.channel_input)

        left = QVBoxLayout()
        left.addLayout(top)
        left.addLayout(bottom)

        #right: connect checkbox
        self.checkbox = QCheckBox("connect", self)
        layout = QHBoxLayout()
        layout.addLayout(left)
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

        #layout: target voltage
        text = QLabel("Target Voltage (V):", self)
        self.target_voltage_input = QLineEdit("", self)
        self.target_voltage_output = QLabel("", self)

        layout = QHBoxLayout()
        layout.addWidget(text)
        layout.addWidget(self.target_voltage_input)
        layout.addWidget(self.target_voltage_output)
        layout_final.addLayout(layout)

        #layout: output voltage
        text = QLabel("Output Voltage (V):", self)
        self.output_voltage = QLabel("", self)

        layout = QHBoxLayout()
        layout.addWidget(text)
        layout.addWidget(self.output_voltage)
        layout_final.addLayout(layout)

        #layout: current limit
        text = QLabel("Current Limit (mA):", self)
        self.current_limit_input = QLineEdit("", self)
        self.current_limit_output = QLabel("", self)

        layout = QHBoxLayout()
        layout.addWidget(text)
        layout.addWidget(self.current_limit_input)
        layout.addWidget(self.current_limit_output)
        layout_final.addLayout(layout)

        #layout: output current
        text = QLabel("Output Current (mA):", self)
        self.output_current = QLabel("", self)

        layout = QHBoxLayout()
        layout.addWidget(text)
        layout.addWidget(self.output_current)
        layout_final.addLayout(layout)

        #layout: switch output
        self.switch_input = QPushButton("Switch Output", self)
        self.switch_output = QLabel("", self)

        layout = QHBoxLayout()
        layout.addWidget(self.switch_input)
        layout.addWidget(self.switch_output)
        layout_final.addLayout(layout)

        #layout: ChartView
        chartView = QtCharts.QChartView()
        layout_final.addWidget(chartView)
        self.setLayout(layout_final)

        #signal and slot
        self.ip_input.returnPressed.connect(self.update_ip)
        self.channel_input.returnPressed.connect(self.update_channel)
        self.checkbox.stateChanged.connect(self.connect)
        self.target_voltage_input.returnPressed.connect(self.set_target_voltage)
        self.current_limit_input.returnPressed.connect(self.set_current_limit)
        self.switch_input.clicked.connect(self.toggle_switch)

        #Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)

        #Line Chart
        self.series_voltage = QtCharts.QLineSeries()
        self.series_current = QtCharts.QLineSeries()
        chart = QtCharts.QChart()
        chart.addSeries(self.series_voltage)
        chart.addSeries(self.series_current)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignTop)
        markers = chart.legend().markers()
        markers[0].setLabel("Output Voltage")
        markers[1].setLabel("Output Current")
        #chart.setTitle("")

        self.axisX = QtCharts.QDateTimeAxis()
        self.axisX.setTickCount(5)
        self.axisX.setFormat("hh:mm:ss")
        self.axisX.setTitleText("Time")
        self.axisX.setMin(QDateTime().currentDateTime().addSecs(-60))
        self.axisX.setMax(QDateTime().currentDateTime())
        chart.addAxis(self.axisX, Qt.AlignBottom)
        self.series_voltage.attachAxis(self.axisX)
        self.series_current.attachAxis(self.axisX)

        axisY_voltage = QtCharts.QValueAxis()
        axisY_voltage.setTickCount(8)
        axisY_voltage.setLabelFormat("%.3f")
        axisY_voltage.setTitleText("Output Voltage (V)")
        axisY_voltage.setRange(0,14)
        chart.addAxis(axisY_voltage, Qt.AlignLeft)
        self.series_voltage.attachAxis(axisY_voltage)
        
        axisY_current = QtCharts.QValueAxis()
        axisY_current.setTickCount(8)
        axisY_current.setLabelFormat("%i")
        axisY_current.setTitleText("Output Current (mA)")
        axisY_current.setRange(0,700)
        chart.addAxis(axisY_current, Qt.AlignRight)
        self.series_current.attachAxis(axisY_current)

        chartView.setChart(chart)
        chartView.setRenderHint(QPainter.Antialiasing)

    @Slot()
    def update_ip(self):
        self.ip = self.ip_input.text()

    @Slot()
    def update_channel(self):
        self.channel = int(self.channel_input.text())

    @Slot()
    def connect(self):
        if self.checkbox.isChecked():
            print("connecting " + self.ip)
            self.timer.start(sample_interval_secs *1000)
            self.tti = ttiPsu(self.ip, self.channel)

            dtime = datetime.datetime.now()
            self.time.setText(dtime.strftime('%c'))

            #get data
            data = self.tti.GetData()
            data.print()
         
            self.name.setText(data.identity)
            self.target_voltage_input.setText("{0:.3f}".format(data.target_volts))
            self.target_voltage_output.setText("setpoint: {0:.3f}".format(data.target_volts))
            self.output_voltage.setText("{0:.3f}".format(data.out_volts))
            self.current_limit_input.setText("{0}".format(int(data.target_amps*1000)))
            self.current_limit_output.setText("setpoint: {0}".format(int(data.target_amps*1000)))
            self.output_current.setText("{0}".format(int(data.out_amps*1000)))
            isON = self.tti.getOutputIsEnabled()

            if data.is_enabled:
                self.switch_output.setText("Output is ON")
            else:
                self.switch_output.setText("Output is OFF")

            self.series_voltage.append(QDateTime().currentDateTime().toMSecsSinceEpoch(), data.out_volts)
            self.series_current.append(QDateTime().currentDateTime().toMSecsSinceEpoch(), data.out_amps*1000)
            self.axisX.setMin(QDateTime().currentDateTime().addSecs(-60))
            self.axisX.setMax(QDateTime().currentDateTime())

        else:
            print("disconnecting...")
            self.timer.stop()
            self.tti.setLocal() 
            del self.tti

            self.name.setText("")
            self.time.setText("")
            self.output_voltage.setText("")
            self.output_current.setText("")
            self.switch_output.setText("")
            print("disconnect successfully.")

    @Slot()
    def update_data(self):
        dtime = datetime.datetime.now()
        self.time.setText(dtime.strftime('%c'))

        data = self.tti.GetData()
        data.print()

        self.name.setText(data.identity)
        self.target_voltage_output.setText("setpoint: {0:.3f}".format(data.target_volts))
        self.output_voltage.setText("{0:.3f}".format(data.out_volts))
        self.current_limit_output.setText("setpoint: {0}".format(int(data.target_amps*1000)))
        self.output_current.setText("{0}".format(int(data.out_amps*1000)))

        self.series_voltage.append(QDateTime().currentDateTime().toMSecsSinceEpoch(), data.out_volts)
        self.series_current.append(QDateTime().currentDateTime().toMSecsSinceEpoch(), data.out_amps*1000)
        self.axisX.setMin(QDateTime().currentDateTime().addSecs(-60))
        self.axisX.setMax(QDateTime().currentDateTime())

    @Slot()
    def set_target_voltage(self):
        if self.checkbox.isChecked():
            self.tti.setTargetVolts(float(self.target_voltage_input.text()))

    @Slot()
    def set_current_limit(self):
        if self.checkbox.isChecked():
            self.tti.setTargetAmps(float(self.current_limit_input.text())/1000)

    @Slot()
    def toggle_switch(self):
        if self.checkbox.isChecked():
            isON = self.tti.getOutputIsEnabled()
            if isON:
                self.tti.setOutputEnable(False)
                self.switch_output.setText("Output is OFF")
            else:
                self.tti.setOutputEnable(True)
                self.switch_output.setText("Output is ON")

class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("TTi PL-P Series Remote Control")
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
