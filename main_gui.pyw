# ???????
# Icons made by <a href="https://www.flaticon.com/authors/freepik" title="Freepik">Freepik
#               </a> from <a href="https://www.flaticon.com/" title="Flaticon"> www.flaticon.com</a>

import sys
sys.path.append('C:\\Users\\לובה שמרוב\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages')
from threading import Thread, ThreadError, currentThread
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pollutionApi import Pollution
# TODO: fix color changing bug in auto update mode
# TODO: improve the GPL value label stylesheet
# TODO: set the different GPL state icons
style_sheet = '''
            QWidget {
                    background-color: #DDDDDD;
            }
            QLabel {
                    background-color: #EEEEEE;
            }
            QLabel#gpl_title {
                    text-decoration: underline;
                    qproperty-alignment: AlignCenter;
            }
            QLabel#GPL_value {
                    font: 25px bold;
                    qproperty-alignment: AlignCenter;
                    min-height: 78px;
                    border-radius: 7px;
                    
            }
            QLabel#time_label {
                    background-color: #DDDDDD
            }
            QLabel#weather_value_label {
                    background-color: #DDDDDD
                    
            }
            QFrame#pollution_frame {
                    background-color: #EEEEEE;
                    border-style: sunken transparent;
                    border_color: #000000;
                    border-width: 1px;
                    border-radius: 6px;
                    padding: 10px;
                    margin: 20px;
                    font: bold;
                    opacity: 200;
            }
            QPushButton#update_button {
                    font: 16px;
                    margin-right: 8px;
                    width: 75px;
                    height: 35px;
            }
            QCheckBox#update_cb {
                    margin-top: 0px;
                    font: 14px;

            }
'''


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.thread_pool = QThreadPool()
        self.pollution = Pollution()
        self.initUI()


    def initUI(self):
        self.setGeometry(100, 100, 400, 250)
        self.setWindowTitle("Pollution 1.0b")
        self.setUpdatesEnabled(True)

        self.setupWidgets()
        self.getPollutionData(self.pollution)
        self.show()

    def setupWidgets(self):

        # Pollutants' values frame and widgets
        pollutants_frame = QFrame()
        pollutants_frame.setObjectName('pollution_frame')

        o3_title_label = QLabel('O3:')
        so2_title_label = QLabel('SO2:')
        no2_title_label = QLabel('NO2:')
        NOx_title_label = QLabel('NOx:')
        PM2_5_title_label = QLabel('PM2.5:')


        self.o3_value = QLabel()
        self.so2_value = QLabel()
        self.no2_value = QLabel()
        self.NOx_value = QLabel()
        self.PM2_5_value = QLabel()

        pollutants_title_layout = QVBoxLayout()
        pollutants_title_layout.addWidget(o3_title_label)
        pollutants_title_layout.addWidget(so2_title_label)
        pollutants_title_layout.addWidget(no2_title_label)
        pollutants_title_layout.addWidget(NOx_title_label)
        pollutants_title_layout.addWidget(PM2_5_title_label)
        pollutants_title_layout.addStretch()

        pollutants_values_layout = QVBoxLayout()
        pollutants_values_layout.addWidget(self.o3_value)
        pollutants_values_layout.addWidget(self.so2_value)
        pollutants_values_layout.addWidget(self.no2_value)
        pollutants_values_layout.addWidget(self.NOx_value)
        pollutants_values_layout.addWidget(self.PM2_5_value)
        pollutants_values_layout.addStretch()

        # General pollution score and description
        GPL_label = QLabel('Pollution Status:')
        GPL_label.setObjectName('gpl_title')
        GPL_label.setFont(QFont('Ariel', 10))
        self.GPL_value_label = QLabel()
        self.GPL_value_label.setObjectName('GPL_value')

        GPL_layout = QVBoxLayout()
        GPL_layout.addWidget(GPL_label)
        GPL_layout.addWidget(self.GPL_value_label)
        GPL_layout.addStretch()

        pollutant_frame_layout = QHBoxLayout()
        pollutant_frame_layout.addStretch()
        pollutant_frame_layout.addStretch()
        pollutant_frame_layout.addLayout(pollutants_title_layout)
        pollutant_frame_layout.addLayout(pollutants_values_layout)
        pollutant_frame_layout.addStretch()
        pollutant_frame_layout.addLayout(GPL_layout)
        pollutant_frame_layout.addStretch()
        pollutant_frame_layout.addStretch()

        pollutants_frame.setLayout(pollutant_frame_layout)

        # Creating the weather frame and labels
        weather_frame = QFrame()
        temp_title = QLabel('Temp:')
        rain_title = QLabel('Rain:')
        humidity_title = QLabel('Humidity:')

        self.temp_label = QLabel()
        self.temp_label.setObjectName('weather_value_label')
        self.rain_label = QLabel()
        self.rain_label.setObjectName('weather_value_label')
        self.humidity_label = QLabel()
        self.humidity_label.setObjectName('weather_value_label')

        weather_layout = QHBoxLayout()
        weather_layout.addWidget(temp_title)
        weather_layout.addWidget(self.temp_label)
        weather_layout.addWidget(rain_title)
        weather_layout.addWidget(self.rain_label)
        weather_layout.addWidget(humidity_title)
        weather_layout.addWidget(self.humidity_label)

        weather_frame.setLayout(weather_layout)

        # Creating the update and graph QPushButtons, and their layout.
        buttons_frame = QFrame()

        update_button = QPushButton('Update')
        update_button.setObjectName('update_button')
        update_button.setToolTip('Update pollutant value.')
        update_button.clicked.connect(self.updateData)

        buttons_frame_layout =QHBoxLayout()
        buttons_frame_layout.addStretch()
        buttons_frame_layout.addWidget(update_button)

        buttons_frame.setLayout(buttons_frame_layout)

        # Creating the auto update frame and widgets
        auto_update_frame = QFrame()

        self.auto_update_cb = QCheckBox('Auto Update')
        self.auto_update_cb.setObjectName('update_cb')
        self.auto_update_cb.toggled.connect(self.handleWorker)

        self.update_time_label = QLabel()
        self.update_time_label.setObjectName('time_label')

        auto_update_layout = QHBoxLayout()
        auto_update_layout.addWidget(self.update_time_label)
        auto_update_layout.addStretch()
        auto_update_layout.addWidget(self.auto_update_cb)
        auto_update_frame.setLayout(auto_update_layout)

        main_layout = QVBoxLayout()

        main_layout.addWidget(pollutants_frame)
        main_layout.addWidget(weather_frame)
        main_layout.addWidget(buttons_frame)
        main_layout.addWidget(auto_update_frame)

        self.setLayout(main_layout)

    def handleWorker(self):
        if self.auto_update_cb.isChecked():
            self.worker = AutoUpdateThread(self.updateData)
            self.thread_pool.start(self.worker)
        else:
            print('auto update stopped')
            self.worker.running = False

    def getPollutionData(self, pollution_data):
        data = pollution_data.stationData()
        O3 = data['O3']['value']
        SO2 = data['SO2']['value']
        NO2 = data['NO2']['value']
        NOx = data['NOX']['value']
        PM2_5 = data['PM2_5']['value']
        general_pollution = self.pollution.calcPollution()
        self.o3_value.setText(str(O3) + ' ppb')
        self.so2_value.setText(str(SO2) + ' ppb')
        self.no2_value.setText(str(NO2) + ' ppb')
        self.NOx_value.setText(str(NOx) + ' ppb')
        self.PM2_5_value.setText(str(PM2_5) + ' µg/m³')

        self.pollution_color = general_pollution[0]
        self.pollution_description = general_pollution[1]

        self.GPL_value_label.setText(self.pollution_description)
        print(self.pollution_color)
        self.GPL_value_label.setFont(QFont('Ariel', 20))
        self.GPL_value_label.setStyleSheet(f"background-color: {self.pollution_color}")
        self.update_time_label.setText(f'last info at:\n {self.pollution.j_data["data"][0]["datetime"]}')
        weather = self.pollution.weather_values
        self.rain_label.setText(str(weather['rain']['value']) + ' mm')
        self.temp_label.setText(str(weather['temp']['value']) + ' °c')
        self.humidity_label.setText(str(weather['humidity']['value']) + ' %')

    def updateData(self):
        self.pollution = Pollution()
        print(f'Data updating - last info at {self.pollution.j_data["data"][0]["datetime"]}')
        self.update_time_label.setText(f'last info at:\n {self.pollution.j_data["data"][0]["datetime"]}')
        self.getPollutionData(self.pollution)


class AutoUpdateThread(QRunnable):
    def __init__(self, update_func):
        super(AutoUpdateThread, self).__init__()
        self.update_func = update_func

    @pyqtSlot()
    def run(self):
        self.running = True
        while self.running:
            time.sleep(60)
            print('loop process')
            self.update_func()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    win = MainWindow()
    sys.exit(app.exec_())