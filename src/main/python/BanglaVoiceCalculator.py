from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QProgressBar, QPlainTextEdit, QMainWindow, QTextBrowser, \
    QDialog, QMenu, QAction, QMessageBox, QStatusBar, QSlider, QLabel, QCheckBox, QDialogButtonBox
from PyQt5.QtGui import QIcon, QFont
from PyQt5 import uic, QtGui
import sys
from time import sleep
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import resources
import speech_recognition as sr
from speech_to_exp import *
from base import *

class SpeechCal(QObject):
    startSpeech = pyqtSignal(str)
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    errorSignal = pyqtSignal(str)
    finishedListen = pyqtSignal(str)
    finishedCalculation = pyqtSignal(tuple)
    finished = pyqtSignal()
    r = sr.Recognizer()

    def __init__(self, result):
        super(SpeechCal, self).__init__()
        self.PrevResult = result

    def speech(self):
        prevResult = self.PrevResult
        self.status.emit('preparing')
        self.progress.emit(10)
        with open(settings_file,'r') as file:
            setting = json.load(file)

        self.status.emit('Checking Internet Connection')
        self.progress.emit(20)
        if(checkConnection()):
            self.status.emit('Connection Success')
            self.progress.emit(30)
            with sr.Microphone() as source:
                self.status.emit('Adjusting mic for noise cancellation')

                self.r.adjust_for_ambient_noise(source, duration=3)

                self.progress.emit(40)
                self.status.emit('Listening')
                self.startSpeech.emit('বলুন')

                self.audio = self.r.listen(source,phrase_time_limit=setting['limit'],timeout=10)
                self.status.emit('Listening Done')
                self.progress.emit(50)
                self.status.emit('Sending audio for recognition')
                try:
                    self.text = self.r.recognize_google(self.audio, language='bn')
                    self.status.emit('Recognization complete')
                    self.progress.emit(60)
                    self.finishedListen.emit(self.text)
                    self.status.emit('Calculation on the way')
                    self.progress.emit(80)
                    finalResult = SpeechToExp(self.text, prevResult)
                    if finalResult is not None:
                        self.finishedCalculation.emit(finalResult)
                    else:
                        self.errorSignal.emit('MathError')
                    self.status.emit('Process finished')
                    self.progress.emit(100)
                    self.finished()
                except Exception as e:
                    self.finished.emit()
        else:
            self.errorSignal.emit('ConnectionError')
            self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        self.Result = 0
        super(MainWindow, self).__init__()
        uic.loadUi(appContext.get_resource('ui/mainWindow.ui'), self)
        self.fontDB = QtGui.QFontDatabase()
        self.fontID = self.fontDB.addApplicationFont(":Resources/BenSenHandwriting.ttf")
        self.font = QFont('BenSenHandwriting')
        QApplication.setFont(self.font)
        self.btn = self.findChild(QPushButton, 'startBtn')
        self.listen_txt = self.findChild(QPlainTextEdit, 'listenText')
        self.output_txt = self.findChild(QPlainTextEdit,'outputText')
        self.progress_bar = self.findChild(QProgressBar,'progressBar')
        self.status_bar = self.findChild(QStatusBar,'statusbar')

        self.help = self.findChild(QAction, 'actionhelp')
        self.settings = self.findChild(QAction,'actionSettings')
        self.about = self.findChild(QAction, 'actionabout')
        self.exit = self.findChild(QAction, 'actionExit')

        self.progress_bar.setVisible(False)

        self.help.triggered.connect(self.ShowHelp)
        self.settings.triggered.connect(self.ShowSettings)
        self.exit.triggered.connect(self.close)
        self.about.triggered.connect(self.OpenAbout)
        self.btn.clicked.connect(self.BtnClicked)

    def BtnClicked(self):
        self.progress_bar.setVisible(True)
        self.listen_txt.clear()
        self.output_txt.clear()
        self.thread = QThread()
        self.GetSpeech = SpeechCal(self.Result)
        self.GetSpeech.moveToThread(self.thread)
        self.thread.started.connect(self.GetSpeech.speech)
        self.GetSpeech.finished.connect(self.thread.quit)
        self.GetSpeech.finished.connect(self.GetSpeech.deleteLater)
        self.GetSpeech.finished.connect(lambda :self.btn.setText('শুরু করুন'))
        self.GetSpeech.finished.connect(lambda: self.progress_bar.setVisible(False))
        self.thread.finished.connect(self.thread.deleteLater)
        self.GetSpeech.progress.connect(self.ShowProgress)
        self.GetSpeech.status.connect(self.ShowStatus)
        self.GetSpeech.startSpeech.connect(self.ButtonStatus)
        self.GetSpeech.errorSignal.connect(self.ShowError)
        self.GetSpeech.finishedListen.connect(self.ShowListendText)
        self.GetSpeech.finishedCalculation.connect(self.ShowCalculation)
        self.GetSpeech.finishedCalculation.connect(self.SetResult)

        self.thread.start()
        self.btn.setEnabled(False)
        self.thread.finished.connect(lambda :self.btn.setEnabled(True))
        self.thread.finished.connect(lambda :self.progress_bar.setValue(0))
    def ShowProgress(self,i):
        self.progress_bar.setValue(i)
    def ShowStatus(self,str):
        self.status_bar.showMessage(str)
    def ButtonStatus(self,str):
        self.btn.setText(str)
    def ShowListendText(self, text):
        self.listen_txt.insertPlainText(BengalizeNumber(text))
    def ShowCalculation(self, result):
        with open(settings_file, 'r') as file:
            setting = json.load(file)
        if setting['bangla']:
            fullText = BengalizeNumber(str(result[0]))+'='+BengalizeNumber(str(result[1]))
        else:
            fullText = EnglishPresentable(str(result[0])) + '=' + EnglishPresentable(str(result[1]))
        self.output_txt.insertPlainText(fullText)

    def SetResult(self,result):
        self.Result = result[1]
    def ShowError(self, error):
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(r':Resources/SpeechCalTi.png'))
        msg.setStyleSheet('color: white; background-color:#47515c; font-size:20px;')
        msg.setIcon(QMessageBox.Critical)

        if error == 'MathError':
            msg.setText("ম্যাথ ইরোর!")
            #msg.setInformativeText("এপ্লিকেশনটি চালাতে ইন্টারনেট সংযোগ প্রয়োজন")
            msg.setWindowTitle("Math Error")
        elif error == 'ConnectionError':
            msg.setText("সংযোগ পাওয়া যায় নি!")
            # msg.setInformativeText("এপ্লিকেশনটি চালাতে ইন্টারনেট সংযোগ প্রয়োজন")
            msg.setWindowTitle("Connection Error")
        msg.setStandardButtons(QMessageBox.Abort)
        msg.exec_()

    def changeOutputLang(self,bangla):
        if bangla:
            current_text = self.output_txt.toPlainText()
            current_text = BengalizeNumber(current_text)
            self.output_txt.setPlainText(current_text)
        else:
            current_text = self.output_txt.toPlainText()
            current_text = EnglizeNumber(current_text)
            self.output_txt.setPlainText(current_text)
    def ShowHelp(self):
        self.Show_Help = HelpWindow()
        self.Show_Help.show()
        self.Show_Help.exec_()
    def ShowSettings(self):
        self.show_settings = SettingWindow()
        self.show_settings.finished_signal.connect(self.changeOutputLang)
        self.show_settings.show()
        self.show_settings.exec_()
    def OpenAbout(self):
        self.show_about = AboutWindow()
        self.show_about.show()
        self.show_about.exec_()
    def closeEvent(self, event):
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(r':Resources/SpeechCalTi.png'))
        msg.setStyleSheet('color: white; background-color:#47515c; font-size:20px;')

        msg.setIcon(QMessageBox.Question)
        msg.setText("আপনি কি শিওর প্রস্থান করতে চান?")
        # msg.setInformativeText("এপ্লিকেশনটি চালাতে ইন্টারনেট সংযোগ প্রয়োজন")
        msg.setWindowTitle("Exit Warning")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        ensure = msg.exec_()
        if ensure == QMessageBox.Yes:
            app = QApplication([])
            app.closeAllWindows()
            event.accept()
        else:
            event.ignore()

class HelpWindow(QDialog):
    def __init__(self):
        super(HelpWindow, self).__init__()
        uic.loadUi(appContext.get_resource('ui/help.ui'),self)
        self.textBrowser = self.findChild(QTextBrowser, 'textBrowser')
        # self.fontDB = QtGui.QFontDatabase()
        # self.fontID = self.fontDB.addApplicationFont(":Resources/BenSenHandwriting.ttf")
        self.font = QFont('BenSenHandwriting')
        self.textBrowser.setFont(self.font)

class AboutWindow(QDialog):
    def __init__(self):
        super(AboutWindow, self).__init__()
        uic.loadUi(appContext.get_resource('ui/aboutWindow.ui'),self)

class SettingWindow(QDialog):
    finished_signal = pyqtSignal(bool)
    def __init__(self):
        super(SettingWindow, self).__init__()
        uic.loadUi(appContext.get_resource('ui/SettingsWindow.ui'),self)
        with open(settings_file,'r') as file:
            self.setting = json.load(file)

        self.timeCheck = self.findChild(QCheckBox,'listenTimeCBox')
        self.slider = self.findChild(QSlider,'listenTimeSlider')
        self.timeLabel = self.findChild(QLabel,'label')
        self.BanglaResult = self.findChild(QCheckBox,'BanglaResCBox')
        self.buttonBox =self.findChild(QDialogButtonBox, 'buttonBox')

        self.timeLabel.setText('Set Time:'+str(self.slider.value()))
        self.slider.valueChanged.connect(self.updateLabel)
        self.buttonBox.accepted.connect(self.updateSetting)
        self.buttonBox.rejected.connect(self.reject)

        if self.setting['limit'] is None:
            self.timeCheck.setChecked(False)
        else:
            self.timeCheck.setChecked(True)
            self.slider.setValue(self.setting['limit'])
        if self.setting['bangla']:
            self.BanglaResult.setChecked(True)
        else:
            self.BanglaResult.setChecked(False)

    def updateLabel(self):
        self.timeLabel.setText('Set Time:'+str(self.slider.value()))

    def updateSetting(self):
        if self.timeCheck.isChecked():
            limit = self.slider.value()
        else:
            limit = None
        self.setting['limit'] = limit
        self.setting['bangla'] = self.BanglaResult.isChecked()
        with open(settings_file,'w') as file:
            json.dump(self.setting, file)
        if self.setting['bangla']:
            self.finished_signal.emit(True)
        else:
            self.finished_signal.emit(False)




# app = QApplication([])
# window = MainWindow()
# window.show()
# sys.exit(app.exec_())
#
# del window,app
