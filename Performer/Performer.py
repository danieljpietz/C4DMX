
import os
import sys
import time
import mido
import threading
import marshal
import math
from os import listdir
from os.path import isfile, join
GlobalFPS = 60
GlobalPacket = 512 * [0]

"""
[Play/Pause, Current Frame, LoopMode, MaxFrame, DMXPacket, Gain, IsAlive, IsInFileBrowser, FileBrowserCursor]
"""
ExportLocation = "/Users/danielpietz/Documents/Lighting/Exports"

Tracks = [[None for i in range(9)] for j in range(4)]
OutputData = [128]
ScrubLast = len(Tracks) * [63]
ScrubDiff = len(Tracks) * [0]


TrackThreads = []
GlobalThread = []

def TrackThread(id, path):

    #path = '/Users/danielpietz/Documents/Lighting/Other/Export1.rdmx'
    Tracks[id][6] = True
    print("Starting Track " + str(id+1) + " With Path: " + path)
    TrackFile = open(path, "rb")
    DMXAr = marshal.load(TrackFile)
    TrackFile.close()
    MetaDeta = DMXAr.pop()
    TrackFps = MetaDeta[0]
    TrackBPM = MetaDeta[1]
    Tracks[id][1] = 0
    Tracks[id][3] = len(DMXAr)
    Tracks[id][5] = 1
    DMXPacket = DMXAr[0][:]

    while 1 == 1:
        if(Tracks[id][0] == True):
            print("H")
            Tracks[id][1] = Tracks[id][1] + 1
            if Tracks[id][1] == Tracks[id][3]:
                if Tracks[id][2] == True:
                    Tracks[id][1] = 0
                else:
                    Tracks[id][1] = Tracks[id][1] -1
                    Tracks[id][0] = False
                    pass
                pass
            #print(Tracks)
            time.sleep(float(TrackBPM)/(OutputData[0])/(TrackFps))
            pass
        if id == 0:
            #print(DMXAr[Tracks[id][1]][:])
            pass
        if(Tracks[id][1] >= 0 and Tracks[id][1] < Tracks[id][3]):
            DMXPacket = DMXAr[Tracks[id][1]][:]
            pass
        #print(Tracks[id][1])
        for i in range(0,len(DMXPacket)):
            DMXPacket[i] = DMXPacket[i] * Tracks[id][5]
        pass

        Tracks[id][4] = DMXPacket[:]

def GlobalThread():
    while (1==1):
        GlobalPacket = 512 * [0]
        for i in range(len(Tracks)):
            if(Tracks[i][6] == True):
                GlobalPacket = GlobalPacket + Tracks[i][4]

        for i in range(len(GlobalPacket)):
            GlobalPacket[i] = int(GlobalPacket[i])
            if(GlobalPacket[i] > 255):
                GlobalPacket[i] = 255
            elif (GlobalPacket[i] < 0):
                GlobalPacket[i] = 0
                pass

        #print(GlobalPacket[0:21])
        time.sleep(1/GlobalFPS)
        pass

def InThread():
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
        instr = []
    pass

def LoadTrack(id, path):
    TrackThreads[id] = threading.Thread(target=TrackThread, args = (id,path))
    TrackThreads[id].start()
    pass

def UnloadTrack(id):
    TrackThreads[id].join()
    Tracks[id][6] = False
    pass



def main():

    onlyfiles = [f for f in listdir(ExportLocation) if isfile(join(ExportLocation, f))]
    RDMXFiles = []
    for f in onlyfiles:
        if f.endswith(".rdmx"):
            RDMXFiles.append(f)
    print(RDMXFiles)
    global TrackThreads, GloblThread
    InputThread = threading.Thread(target=InThread)
    InputThread.start()

    TrackThreads = [threading.Thread(target=TrackThread, args = (i,None)) for  i in range(4)]
    for Track in Tracks:
        Track[0] = False
        Track[6] = False
        Track[7] = False
        Track[8] = 0

    GloblThread = threading.Thread(target=GlobalThread)
    GloblThread.start()

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
                        LoadTrack(msg.channel, ExportLocation + "/" + RDMXFiles[Tracks[msg.channel][8]])
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



if __name__ == '__main__':
    main()
