import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget,QLabel,QPushButton, QAction, QLineEdit, QMessageBox, QDesktopWidget, QSlider,QListWidget
import qdarkstyle
import os
from PyQt5.QtGui import QPainter, QBrush, QPen, QIcon, QPixmap, QImage
from PyQt5.QtCore import Qt, QRect
from PyQt5.Qt import QFont
from os import listdir
from os.path import isfile, join

ImportPath = "/Users/danielpietz/Documents/Lighting/Exports"
PlayRects = []
PlayStatus = [True, True, False, False]
app = None
RDMXFiles = []
TrackBrowsers = []
class Login(QtWidgets.QWidget):

    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.title = 'Performer'
        self.left = 100
        self.top = 100
        self.width = 3272
        self.height = 1920
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.initUI()


    def initUI(self):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.width = self.frameGeometry().width()
        self.height = self.frameGeometry().height()
        """label = QLabel('Username', self)
        center  = (QDesktopWidget().availableGeometry().center())
        label.move(center.x()-140,0.8*center.y()-50-50)

        self.textbox = QLineEdit(self)
        self.textbox.resize(280,40)
        self.textbox.move(center.x()-140,0.8*center.y() - 20-50)

        label = QLabel('Password', self)
        label.move(center.x()-140,center.y()-50-50)

        self.textbox1 = QLineEdit(self)
        self.textbox1.setEchoMode(QLineEdit.Password)
        self.textbox1.resize(280,40)
        self.textbox1.move(center.x()-140,center.y() - 20-50)

        self.button = QPushButton('Login', self)
        self.button.resize(140, 30)
        self.button.setCheckable(True)
        self.button.toggle()
        self.button.move(center.x()-70,center.y() + 40-50)"""
        W =  self.frameGeometry().width()
        H = self.frameGeometry().height()
        PlayImages = []
        self.TrackAList = QListWidget(self)
        self.TrackAList.setMaximumWidth(500)
        self.TrackAList.setMaximumHeight(500)
        self.TrackAList.move(16,96)
        self.TrackAList.resize(400,300)

        for i in range(len(RDMXFiles)):
            self.TrackAList.insertItem(i, RDMXFiles[i].replace(".rdmx", ""))
        self.TrackAList.setCurrentRow(0)
        TrackBrowsers.append(self.TrackAList)

        self.TrackBList = QListWidget(self)
        self.TrackBList.setMaximumWidth(500)
        self.TrackBList.setMaximumHeight(500)
        self.TrackBList.move(1024 + 16,96)
        self.TrackBList.resize(400,300)

        for i in range(len(RDMXFiles)):
            self.TrackBList.insertItem(i, RDMXFiles[i].replace(".rdmx", ""))
        self.TrackBList.setCurrentRow(0)
        TrackBrowsers.append(self.TrackBList)

        self.TrackCList = QListWidget(self)
        self.TrackCList.setMaximumWidth(500)
        self.TrackCList.setMaximumHeight(500)
        self.TrackCList.move(16,512 + 96 + 96)
        self.TrackCList.resize(400,300)

        for i in range(len(RDMXFiles)):
            self.TrackCList.insertItem(i, RDMXFiles[i].replace(".rdmx", ""))
        self.TrackCList.setCurrentRow(0)
        TrackBrowsers.append(self.TrackCList)

        self.TrackDList = QListWidget(self)
        self.TrackDList.setMaximumWidth(500)
        self.TrackDList.setMaximumHeight(500)
        self.TrackDList.move(1024 + 16,512 + 96 + 96)
        self.TrackDList.resize(400,300)

        for i in range(len(RDMXFiles)):
            self.TrackDList.insertItem(i, RDMXFiles[i].replace(".rdmx", ""))
        self.TrackDList.setCurrentRow(0)
        TrackBrowsers.append(self.TrackDList)


        self.showMaximized()
        self.show()
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QtCore.Qt.white)
        painter.setBrush(QtCore.Qt.white)
        painter.setFont(QFont('Helvetica', 100))
        W =  self.frameGeometry().width()
        H = self.frameGeometry().height()

        painter.drawLine(0, int(H/2), W, int(H/2))
        painter.drawLine(int(W/2), 0, int(W/2),H)
        painter.drawText(QtCore.QRect(0,0,int(W/20.48),int(W/20.48)), Qt.AlignCenter, "A")
        painter.drawText(QtCore.QRect(int(W/2),0,int(W/20.48),int(W/20.48)), Qt.AlignCenter, "B")
        painter.drawText(QtCore.QRect(0,int(H/2),int(W/20.48),int(W/20.48)), Qt.AlignCenter, "C")
        painter.drawText(QtCore.QRect(int(W/2),int(H/2),int(W/20.48),int(W/20.48)), Qt.AlignCenter, "D")

        pixmapOFF = QPixmap('/Users/danielpietz/Documents/Lighting/Performer/PlayButtonWhite.png')
        pixmapOFF = pixmapOFF.scaled(96, 96, QtCore.Qt.KeepAspectRatio)

        pixmapON = QPixmap('/Users/danielpietz/Documents/Lighting/Performer/PlayButtonGreen.png')
        pixmapON = pixmapON.scaled(96, 96, QtCore.Qt.KeepAspectRatio)

        PlayRects = [QtCore.QRect(int(W/2) - pixmapOFF.width() - 10,int(H/2)- pixmapOFF.width() - 10,int(W/20.48),int(W/20.48)),
        QtCore.QRect(int(W) - pixmapOFF.width() - 10,int(H/2)- pixmapOFF.width() - 10,int(W/20.48),int(W/20.48)),
        QtCore.QRect(int(W) - pixmapOFF.width() - 10,int(H)- pixmapOFF.width() - 10,int(W/20.48),int(W/20.48)),
        QtCore.QRect(int(W/2) - pixmapOFF.width() - 10,int(H)- pixmapOFF.width() - 10,int(W/20.48),int(W/20.48))]

        for i in range(len(PlayRects)):
            rect = PlayRects[i]
            if(PlayStatus[i] == True):
                pixmap = pixmapON
            else:
                pixmap = pixmapOFF
                pass
            Play = QLabel(self)
            Play.setPixmap(pixmap)
            painter.drawPixmap(rect, pixmap)

        self.TrackAList.resize(int(H * (800/3072)),int(W * (300 / 1920)))
        self.TrackBList.resize(int(H * (800/3072)),int(W * (300 / 1920)))
        self.TrackCList.resize(int(H * (800/3072)),int(W * (300 / 1920)))
        self.TrackDList.resize(int(H * (800/3072)),int(W * (300 / 1920)))


        self.TrackAList.move(16, 96)
        self.TrackBList.move(int(W/2)+ 16, 96)
        self.TrackCList.move(16,int(H/2) + 96)
        self.TrackDList.move(int(W/2) + 16,int(H/2) + 96)


class Controller:

    def __init__(self):
        pass

    def show_login(self):
        self.login = Login()

        #self.login.switch_window.connect(self.switchScreen)
        self.login.show()






def GUIMain():
    global app
    sys._excepthook = sys.excepthook
    def exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)
    sys.excepthook = exception_hook
    app = QtWidgets.QApplication(sys.argv)
    os.environ['PYQTGRAPH_QT_LIB']="PyQt5"
    os.environ['QT_API']="pyqt5"
    app.setStyleSheet(qdarkstyle.load_stylesheet_from_environment())
    controller = Controller()
    controller.show_login()
    sys.exit(app.exec_())



def main():
    global RDMXFiles
    onlyfiles = [f for f in listdir(ImportPath) if isfile(join(ImportPath, f))]
    for f in onlyfiles:
        if f.endswith(".rdmx"):
            RDMXFiles.append(f)
    print(RDMXFiles)
    GUIMain()


if __name__ == '__main__':
    main()
