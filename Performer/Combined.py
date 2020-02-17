import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget,QLabel,QPushButton, QAction, QLineEdit, QMessageBox, QDesktopWidget, QSlider,QListWidget
import qdarkstyle
import os
from PyQt5.QtGui import QPainter, QBrush, QPen, QIcon, QPixmap, QImage
from PyQt5.QtCore import Qt, QRect, QMetaType
from PyQt5.Qt import QFont
from PyQt5.QtCore import *
from os import listdir
from os.path import isfile, join
import mido
import threading
import marshal
import math
import time
import numpy as np
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages')
import pyenttec as dmx


GlobalFPS = 48
GlobalPacket = 512 * [0]
ImportPath = "/Users/danielpietz/Documents/Lighting/Exports"
PlayRects = []
app = None
RDMXFiles = []
TrackBrowsers = []
shouldEXIT = False
GlobalWindow = None

"""
[Play/Pause, Current Frame, LoopMode, MaxFrame, DMXPacket, Gain, IsAlive, IsInFileBrowser, FileBrowserCursor, TrackName, TrackMetadata]
"""

Tracks = [[None for i in range(11)] for j in range(4)]
OutputData = [128]
ScrubLast = len(Tracks) * [63]
ScrubDiff = len(Tracks) * [0]


TrackThreads = []
GlobalThread = []
MidThread = []
InputThread = []

def listWidgetClear(listwidget):
    for i in range(listwidget.count()):
        item = listwidget.item(i)
        item.setSelected(False)

def TrackThread(id, path):
    global PlayRects
    #path = '/Users/danielpietz/Documents/Lighting/Other/Export1.rdmx'
    print("Starting Track " + str(id+1) + " With Path: " + path)
    TrackFile = open(path, "rb")
    DMXAr = marshal.load(TrackFile)
    TrackFile.close()
    MetaDeta = DMXAr.pop()
    TrackFps = MetaDeta[0]
    TrackBPM = MetaDeta[1]
    Tracks[id][1] = 0
    Tracks[id][3] = len(DMXAr)
    Tracks[id][4] = len(DMXAr[0][:]) * [0]
    Tracks[id][5] = 1
    Tracks[id][10] = MetaDeta
    DMXPacket = []

    pixmapOFF = QPixmap('/Users/danielpietz/Documents/Lighting/Performer/PlayButtonWhite.png')
    pixmapOFF = pixmapOFF.scaled(96, 96, QtCore.Qt.KeepAspectRatio)

    pixmapON = QPixmap('/Users/danielpietz/Documents/Lighting/Performer/PlayButtonGreen.png')
    pixmapON = pixmapON.scaled(96, 96, QtCore.Qt.KeepAspectRatio)
    Tracks[id][6] = True
    started = False
    startTime = 0
    startFrame = 0
    while Tracks[id][6] == True:
        if(Tracks[id][0] == False and started == True):
            started = False
            pass
        if(Tracks[id][0] == True):
            if(started == False):
                startTime = time.time()
                startFrame = Tracks[id][1]
                started = True
            currentTime = time.time() - startTime
            Tracks[id][1] = startFrame + int(currentTime * TrackFps)
            if Tracks[id][1] == Tracks[id][3]:
                if Tracks[id][2] == True:
                    Tracks[id][1] = 0
                else:
                    Tracks[id][1] = Tracks[id][1] -1
                    Tracks[id][0] = False
                    pass
                pass
            #print(Tracks)
            t2 = time.time()

            time.sleep(float(TrackBPM)/(OutputData[0])/(TrackFps))
            pass
        if id == 0:
            #print(DMXAr[Tracks[id][1]][:])
            pass
        if(Tracks[id][1] >= 0 and Tracks[id][1] < Tracks[id][3]):
            DMXPacket = DMXAr[Tracks[id][1]][:]

            pass
        #print(Tracks[id][1])
        for i in range(0,len(DMXPacket)-1):
            DMXPacket[i] = DMXPacket[i] * Tracks[id][5]
        pass

        Tracks[id][4] = DMXPacket[:]


pass

def GlobalThread():
    t1 = 0
    t2 = 0
    port = dmx.select_port()
    while (1==1):
        t1 = time.time()
        GlobalPacket = 512 * [0]
        for i in range(len(Tracks)):
            if(Tracks[i][6] == True):
                for j in range(0,511):
                    GlobalPacket[j] = GlobalPacket[j] + Tracks[i][4][j]

        for i in range(len(GlobalPacket)):
            GlobalPacket[i] = int(GlobalPacket[i])
            if(GlobalPacket[i] > 255):
                GlobalPacket[i] = 255
            elif (GlobalPacket[i] < 0):
                GlobalPacket[i] = 0
                pass

        #print(GlobalPacket[0:21])
        for i in range(0,511):
            port[i] = GlobalPacket[i]
        if(GlobalWindow != None):
            GlobalWindow.update()

        port.render()
        t2 = time.time()
        time.sleep(((1/GlobalFPS) - (t2-t1)) * (((1/GlobalFPS) - (t2-t1)) > 0))
        pass

def InThread():
    global shouldEXIT
    while 1==1:
        instr = input()
        if(instr.startswith("load ")):
            instr = instr.replace("load ", "")
            track = int(instr[0])
            instr = instr.replace(str(track) + " ", "")
            path = instr
            path = path.replace(" ", "")
            LoadTrack(track-1, path)


        elif(instr.startswith("unload ")):
            instr = instr.replace("unload ", "")
            track = int(instr[0])
            UnloadTrack(track-1)
        elif(instr.startswith("exit")):
            for i in range(len(TrackThreads)):
                if(Tracks[i][6] == True):
                    Thread.join()
                    pass
                pass
            MidThread.join()
            GlobalThread.join()
            InputThread.join()
            shouldEXIT = True


        instr = []


    pass

def LoadTrack(id, path):
    TrackThreads[id] = threading.Thread(target=TrackThread, args = (id,path))
    TrackThreads[id].start()
    pass

def UnloadTrack(id):
    Tracks[id][6] = False
    TrackThreads[id].join()

    pass

def MidiThread():

    with mido.open_input('Traktor Kontrol S8 Input') as inport:
        for msg in inport:
            if hasattr(msg, 'control'):
                if(msg.control == 69):
                    Tracks[msg.channel][5] = float(msg.value)/127
                if(msg.control == 10):
                    if(msg.value == 127):
                        if(Tracks[msg.channel][6] == True):
                            if(Tracks[msg.channel][1] == Tracks[msg.channel][3]-1):
                                Tracks[msg.channel][1] = 0
                                pass
                            print(Tracks[msg.channel][0])
                            Tracks[msg.channel][0] = not Tracks[msg.channel][0]
                            print(Tracks[msg.channel][0])

                            if(Tracks[msg.channel][0] == True):
                                print("Now Playing Track " + str(msg.channel + 1))
                            else:
                                print("Stopped Playing Track " + str(msg.channel + 1))
                            pass
                        else:
                            print("No File To Play On Track " + str(msg.channel + 1))
                    pass
                if(msg.channel == 4 and msg.control == 86):
                    OutputData[0] = OutputData[0] + (msg.value == 1) - (msg.value == 127)
                pass

                if(msg.control == 22 and msg.value == 127):
                    Tracks[msg.channel][2] = not Tracks[msg.channel][2]
                pass

                if(msg.control == 2):
                    ScrubDiff[msg.channel] = msg.value - ScrubLast[msg.channel]
                    if(abs(ScrubDiff[msg.channel]) > 30):
                         ScrubDiff[msg.channel] = 0
                    ScrubLast[msg.channel] = msg.value
                    Tracks[msg.channel][1] = Tracks[msg.channel][1] - ScrubDiff[msg.channel]
                if(msg.control == 101 and msg.value == 127):
                    if(Tracks[msg.channel][7] == False):
                        print("Select a File to load into Track " + str(msg.channel + 1))
                        print(RDMXFiles)
                        print("---------------------------------")
                        print(RDMXFiles[Tracks[msg.channel][8]])
                        print("---------------------------------")

                    if(Tracks[msg.channel][7] == True):
                        if(Tracks[msg.channel][6] == True):
                            UnloadTrack(msg.channel)
                        LoadTrack(msg.channel, ImportPath + "/" + RDMXFiles[Tracks[msg.channel][8]])
                        Tracks[msg.channel][9] = RDMXFiles[Tracks[msg.channel][8]]
                        #TrackBrowsers[msg.channel].clearSelection()
                    Tracks[msg.channel][7] = not Tracks[msg.channel][7]
                if(msg.control == 100):
                    if(Tracks[msg.channel][7] == True):
                        Tracks[msg.channel][8] = Tracks[msg.channel][8] + (msg.value == 1) - (msg.value == 127)
                        Tracks[msg.channel][8] = Tracks[msg.channel][8] % len(RDMXFiles)
                        print(RDMXFiles[Tracks[msg.channel][8]])
                        print("---------------------------------")
                #print(Tracks)
            #print(msg)
            pass



class MainScreen(QtWidgets.QWidget):

    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        global GlobalWindow
        GlobalWindow = self
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

        self.button = QPushButton('MainScreen', self)
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
        self.TrackAList.setSelectionMode(1)
        global TrackBrowsers
        for i in range(len(RDMXFiles)):
            self.TrackAList.insertItem(i, RDMXFiles[i].replace(".rdmx", ""))

        TrackBrowsers.append(self.TrackAList)





        self.TrackBList = QListWidget(self)
        self.TrackBList.setMaximumWidth(500)
        self.TrackBList.setMaximumHeight(500)
        self.TrackBList.move(1024 + 16,96)
        self.TrackBList.resize(400,300)

        for i in range(len(RDMXFiles)):
            self.TrackBList.insertItem(i, RDMXFiles[i].replace(".rdmx", ""))

        TrackBrowsers.append(self.TrackBList)

        self.TrackCList = QListWidget(self)
        self.TrackCList.setMaximumWidth(500)
        self.TrackCList.setMaximumHeight(500)
        self.TrackCList.move(16,512 + 96 + 96)
        self.TrackCList.resize(400,300)

        for i in range(len(RDMXFiles)):
            self.TrackCList.insertItem(i, RDMXFiles[i].replace(".rdmx", ""))

        TrackBrowsers.append(self.TrackCList)

        self.TrackDList = QListWidget(self)
        self.TrackDList.setMaximumWidth(500)
        self.TrackDList.setMaximumHeight(500)
        self.TrackDList.move(1024 + 16,512 + 96 + 96)
        self.TrackDList.resize(400,300)

        for i in range(len(RDMXFiles)):
            self.TrackDList.insertItem(i, RDMXFiles[i].replace(".rdmx", ""))

        TrackBrowsers.append(self.TrackDList)

        self.TrackADisplay = QLabel('128', self)


        self.showMaximized()
        self.show()
    def paintEvent(self, event):
        if(shouldEXIT == True):
            sys.exit(app.exec_())
            pass

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setFont(QFont('Helvetica', 100))
        W =  self.frameGeometry().width()
        H = self.frameGeometry().height()

        painter.drawLine(0, int(H/2), W, int(H/2))
        painter.drawLine(int(W/2), 0, int(W/2),H)
        if(Tracks[0][7] == True):
            painter.setPen(QtCore.Qt.blue)
            painter.setBrush(QtCore.Qt.blue)
        else:
            painter.setPen(QtCore.Qt.white)
            painter.setBrush(QtCore.Qt.white)
            pass
        painter.drawText(QtCore.QRect(0,0,int(W/20.48),int(W/20.48)), Qt.AlignCenter, "1")
        if(Tracks[1][7] == True):
            painter.setPen(QtCore.Qt.blue)
            painter.setBrush(QtCore.Qt.blue)
        else:
            painter.setPen(QtCore.Qt.white)
            painter.setBrush(QtCore.Qt.white)
            pass
        painter.drawText(QtCore.QRect(int(W/2),0,int(W/20.48),int(W/20.48)), Qt.AlignCenter, "2")
        if(Tracks[2][7] == True):
            painter.setPen(QtCore.Qt.blue)
            painter.setBrush(QtCore.Qt.blue)
        else:
            painter.setPen(QtCore.Qt.white)
            painter.setBrush(QtCore.Qt.white)
            pass
        painter.drawText(QtCore.QRect(0,int(H/2),int(W/20.48),int(W/20.48)), Qt.AlignCenter, "3")
        if(Tracks[3][7] == True):
            painter.setPen(QtCore.Qt.blue)
            painter.setBrush(QtCore.Qt.blue)
        else:
            painter.setPen(QtCore.Qt.white)
            painter.setBrush(QtCore.Qt.white)
            pass
        painter.drawText(QtCore.QRect(int(W/2),int(H/2),int(W/20.48),int(W/20.48)), Qt.AlignCenter, "4")

        pixmapOFF = QPixmap('/Users/danielpietz/Documents/Lighting/Performer/PlayButtonWhite.png')
        pixmapOFF = pixmapOFF.scaled(96, 96, QtCore.Qt.KeepAspectRatio)

        pixmapON = QPixmap('/Users/danielpietz/Documents/Lighting/Performer/PlayButtonGreen.png')
        pixmapON = pixmapON.scaled(96, 96, QtCore.Qt.KeepAspectRatio)

        global PlayRects

        PlayRects = [QtCore.QRect(int(W/2) - pixmapOFF.width() - 10,int(H/2)- pixmapOFF.width() - 10,int(W/20.48),int(W/20.48)),
        QtCore.QRect(int(W) - pixmapOFF.width() - 10,int(H/2)- pixmapOFF.width() - 10,int(W/20.48),int(W/20.48)),
        QtCore.QRect(int(W) - pixmapOFF.width() - 10,int(H)- pixmapOFF.width() - 10,int(W/20.48),int(W/20.48)),
        QtCore.QRect(int(W/2) - pixmapOFF.width() - 10,int(H)- pixmapOFF.width() - 10,int(W/20.48),int(W/20.48))]
        self.TrackADisplay.move(int(W/8) + int(W * (150 / 1920)),int(H/32))
        if(Tracks[0][1] == 0):
            Tracks[0][1] = 1
        Ba = (Tracks[0][1] * (Tracks[0][10][1]/60.0) / (Tracks[0][10][0]))
        Pa = int(np.sign(Ba)*(int(abs(Ba)/32) + 1))
        Ma = int(np.sign(Ba)*(int(abs(Ba)/8) % 4 + 1))
        Ba = round(np.sign(Ba)*((abs(Ba)) % 8 + 1), 1)
        self.TrackADisplay.setText(Tracks[0][9].replace(".rdmx","") + "\n\nCurrent: " + str(Tracks[0][1]) + "\n\nMax: " + str(Tracks[0][3]) + "\n\nP:M:B " +str(Pa) + ":"+ str(Ma) + ":" + str(Ba))
        self.TrackADisplay.resize(500,500)
        self.TrackADisplay.setFont(QFont('Helvetica', 50))
        self.TrackADisplay.setAlignment(Qt.AlignCenter)



        for i in range(len(PlayRects)):
            rect = PlayRects[i]
            if(Tracks[i][0] == True):
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

        self.TrackAList.setCurrentRow(Tracks[0][8])
        self.TrackBList.setCurrentRow(Tracks[1][8])
        self.TrackCList.setCurrentRow(Tracks[2][8])
        self.TrackDList.setCurrentRow(Tracks[3][8])





class Controller:

    def __init__(self):
        pass

    def show_mainScreen(self):
        self.mainScreen = MainScreen()
        self.mainScreen.show()






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
    controller.show_mainScreen()
    sys.exit(app.exec_())



def main():
    global RDMXFiles
    onlyfiles = [f for f in listdir(ImportPath) if isfile(join(ImportPath, f))]
    for f in onlyfiles:
        if f.endswith(".rdmx"):
            RDMXFiles.append(f)
    print(RDMXFiles)
    global TrackThreads, GloblThread, MidThread, InputThread
    InputThread = threading.Thread(target=InThread)
    InputThread.start()

    TrackThreads = [threading.Thread(target=TrackThread, args = (i,None)) for  i in range(4)]
    for Track in Tracks:
        Track[0] = False
        Track[6] = False
        Track[7] = False
        Track[8] = 0
        Track[9] = "--"
        Track[1] = 0
        Track[10] = [1,1]

    GloblThread = threading.Thread(target=GlobalThread)
    GloblThread.start()

    MidThread = threading.Thread(target=MidiThread)
    MidThread.start()

    GUIMain()


if __name__ == '__main__':
    main()
