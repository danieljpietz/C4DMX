"""
Copyright: MAXON Computer GmbH
Author: XXX, Maxime Adam

Description:
    - Tag, force the host object to look at the camera (like the Look At Camera Tag).

Class/method highlighted:
    - c4d.plugins.ObjectData
    - NodeData.Init()
    - TagData.Execute()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21
"""
import os
import sys
import os.path
from os import path
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages')
import c4d
from c4d import utils
import pyenttec as dmx
import marshal
#import Helpers
# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1028285
PI = 3.141592653


"""
Between These Markers include all helper functions
"""

def rangeMap(x,inRange,outRange):
    x = x - inRange[0]
    x = (outRange[1] - outRange[0]) * x / (inRange[1] - inRange[0])
    x = x + outRange[0]
    return x

def min(X):
    x = X[0]
    for i in X:
        if i < x:
            x = i
            pass
        pass
    return x

def getFixturesAtAddress(Univ, Address):
    Fixtures = []
    doc = c4d.documents.GetActiveDocument()
    for obj in doc.GetObjects():
        isLight = False;
        Tag = None
        for tag1 in obj.GetTags():
            if tag1.GetType() == PLUGIN_ID:
                Tag = tag1
                break
            pass
        if (Tag == None or Tag.GetData()[1002] == True):
            continue
            pass
        Layer = obj.GetLayerObject(doc)
        LayerData = Layer.GetLayerData(doc)
        LayerData['manager'] = LayerData['view']
        Layer.GetLayerData(doc)['render'] = False
        if(Layer.GetName() != 'Master' and LayerData['solo'] == True):
            DMXAdr = Tag.GetData()[1000]
            DMXUniv = Tag.GetData()[1001]
            if(DMXAdr == Address and DMXUniv == Univ):
                Fixtures.append(obj)
        pass
    pass
    return Fixtures
pass


def RGB2RGBW(RGB):
    RGB = [RGB[0], RGB[1], RGB[2]]
    White = min(RGB)
    return [RGB[0]- White, RGB[1]- White,RGB[2]- White, White]

"""
Between These Markers include all helper functions
"""


"""
Between These Markers include all classes for fixtures used in the scene
"""
class ChauvetRogueR1(object):
    """docstring for ChauvetRogueR1."""

    def __init__(self, root):
        super(ChauvetRogueR1, self).__init__()
        self.root = root
        self.Reds = []
        self.Greens = []
        self.Blues = []
        self.Motion = []
        self.exportChannelInfo = []
    def update(self, DMXPacket):
        obj = self.root
        Tag = None
        for tag1 in obj.GetTags():
            if tag1.GetType() == PLUGIN_ID:
                Tag = tag1
                break
            pass
        Target = obj.GetChildren()[1]
        Pan = obj.GetChildren()[0]
        Tilt = Pan.GetChildren()[0]
        if(Tag.GetData()[1003] == True):
            local = Target.GetMg().off * (~(Pan.GetUpMg() * Pan.GetFrozenMln())) - Pan.GetRelPos()
            hpb = utils.VectorToHPB(local)
            Pan.SetRelRot(c4d.Vector(hpb[0]-2*PI,0,0))
            local = Target.GetMg().off * (~(Tilt.GetUpMg() * Tilt.GetFrozenMln())) - Tilt.GetRelPos()
            hpb = utils.VectorToHPB(local)
            Tilt.SetRelRot(c4d.Vector(0,hpb[1]-PI/2,0))
            pass


        BASEADR = int(Tag.GetData()[1000])
        universe = int(Tag.GetData()[1001])

        Lamp = Tilt.GetChildren()[0]
        Color = Lamp.GetParameter(c4d.LIGHT_COLOR,c4d.DESCFLAGS_SET_0)
        Zoom = Lamp.GetParameter(c4d.LIGHT_DETAILS_OUTERANGLE,c4d.DESCFLAGS_SET_0)

        if(Zoom < 11*PI/180):
            Zoom = 11*PI/180
            Lamp.SetParameter(c4d.LIGHT_DETAILS_OUTERANGLE, Zoom,c4d.DESCFLAGS_SET_0)
        elif(Zoom > 48*PI/180):
            Zoom = 48*PI/180
            Lamp.SetParameter(c4d.LIGHT_DETAILS_OUTERANGLE, Zoom,c4d.DESCFLAGS_SET_0)
        pass


        BeamAngle = rangeMap(Zoom, [11*PI/180, 48*PI/180], [8*PI/180, 30*PI/180])

        Lamp.SetParameter(c4d.LIGHT_DETAILS_INNERANGLE, BeamAngle,c4d.DESCFLAGS_SET_0)

        ZoomVal = rangeMap(Zoom, [11*PI/180, 48*PI/180], [0,255])

        PanVal = Pan.GetRelRot()[0]
        TiltVal = Tilt.GetRelRot()[1]

        PanVal = rangeMap(PanVal+PI/2, [-1.5*PI, 1.5*PI], [1,2**16])
        TiltVal = rangeMap(TiltVal, [-105*PI/180, 105*PI/180], [1,2**16])

        PanCourse = int(PanVal/256) - 1
        PanFine = int((PanVal % 256)) - 1

        TiltCourse = int(TiltVal/256) - 1
        TiltFine = int((TiltVal % 256)) - 1
        Color = RGB2RGBW(Color)
        RedVal = rangeMap(Color[0], [0, 1], [1,2**16])
        GreenVal = rangeMap(Color[1], [0, 1], [1,2**16])
        BlueVal = rangeMap(Color[2], [0, 1], [1,2**16])
        WhiteVal = rangeMap(Color[3], [0, 1], [1,2**16])

        RedCourse = int(RedVal/256) - 1
        GreenCourse = int(GreenVal/256) - 1
        BlueCourse = int(BlueVal/256) - 1
        WhiteCourse = int(WhiteVal/256) - 1

        RedFine = int((RedVal % 256)) - 1
        GreenFine = int((GreenVal % 256)) - 1
        BlueFine = int((BlueVal % 256)) - 1
        WhiteFine = int((WhiteVal % 256)) - 1

        DMXPacket[BASEADR-1] = PanCourse
        DMXPacket[BASEADR] = PanFine
        DMXPacket[BASEADR+1] = TiltCourse
        DMXPacket[BASEADR+2] = TiltFine
        DMXPacket[BASEADR+3] = 0
        DMXPacket[BASEADR+4] = 255
        DMXPacket[BASEADR+6] = 255
        DMXPacket[BASEADR+7] = RedCourse
        DMXPacket[BASEADR+8] = RedFine
        DMXPacket[BASEADR+9] = GreenCourse
        DMXPacket[BASEADR+10] = GreenFine
        DMXPacket[BASEADR+11] = BlueCourse
        DMXPacket[BASEADR+12] = BlueFine
        DMXPacket[BASEADR+13] = WhiteCourse
        DMXPacket[BASEADR+14] = WhiteFine
        DMXPacket[BASEADR+15] = 0
        DMXPacket[BASEADR+16] = ZoomVal

        self.Reds = [BASEADR+7,BASEADR+8]
        self.Greens = [BASEADR+9,BASEADR+10]
        self.Blues = [BASEADR+11,BASEADR+12]
        self.Motion = [BASEADR-1,BASEADR,BASEADR+1,BASEADR+2]
        self.exportChannelInfo = [self.Reds, self.Greens, self.Blues, self.Motion]

        pass

    def GetColor(self):
        Lamp = self.root.GetChildren()[0].GetChildren()[0].GetChildren()[0]
        Lamp.GetParameter(c4d.LIGHT_COLOR,c4d.DESCFLAGS_SET_0)
        pass

    def SetColor(self, Color):
        Lamp = self.root.GetChildren()[0].GetChildren()[0].GetChildren()[0]
        Lamp.SetParameter(c4d.LIGHT_COLOR,Color,c4d.DESCFLAGS_SET_0)
        pass

    def GetLamp(self):
        return self.root.GetChildren()[0].GetChildren()[0].GetChildren()[0]
pass


"""
Between These Markers include all classes for fixtures used in the scene
"""




class C4DMX(c4d.plugins.TagData):
    """Look at Camera"""

    def Export(self, tag, path1):
        doc = c4d.documents.GetActiveDocument()
        Frame = doc.GetTime().GetFrame(doc.GetFps())
        print(self.exportRange)
        if Frame == self.exportRange[0]:
            self.ExportArray = (self.exportRange[1]-self.exportRange[0]) * [None]
        if(Frame >= self.exportRange[0] and Frame < self.exportRange[1]):
            self.ExportArray[Frame - self.exportRange[0]] = self.DMXPacket[:]

        elif Frame == self.exportRange[1]:
            tag[1004] = False
            appendNum = 1
            print(path.exists(path1))
            while (path.exists(path1)):
                path1 = path1.replace(".rdmx", "")
                path1 = path1 + str(appendNum) + ".rdmx"
                appendNum = appendNum + 1
                pass
            print(self.exportChannelInfo)
            self.ExportArray.append([doc.GetFps(), self.ExportBPM])
            f = open(path1, "w")
            marshal.dump(self.ExportArray, f)
            f.close()




    def Init(self, node):
        """
        Called when Cinema 4D Initialize the TagData (used to define, default values)
        :param node: The instance of the TagData.
        :type node: c4d.GeListNode
        :return: True on success, otherwise False.
        """
        self.port  = None
        self.DMXPacket = 512 * [0]
        self.Fixture = None
        self.ExportEnabled = False
        self.ExportBPM = 128
        self.exportRange = [0,0]
        """ [Reds, Greens, Blues, Motion ]"""
        self.exportChannelInfo  = [[], [], [], []]
        self.ExportArray = (self.exportRange[1]-self.exportRange[0]) * [None]
        self.currentFrame = 0
        self.ExportPath = None
        self.InitAttr(node, float, [1005])
        self.InitAttr(node, float, [1006])
        self.InitAttr(node, float, [1007])
        node[1005] = 0
        node[1006] = 0
        node[1007] = 128
        pd = c4d.PriorityData()
        if pd is None:
            raise MemoryError("Failed to create a priority data.")

        pd.SetPriorityValue(c4d.PRIORITYVALUE_CAMERADEPENDENT, True)
        node[c4d.EXPRESSION_PRIORITY] = pd

        return True

    def Execute(self, tag, doc, op, bt, priority, flags):
        """
        Called by Cinema 4D at each Scene Execution, this is the place where calculation should take place.
        :param tag: The instance of the TagData.
        :type tag: c4d.BaseTag
        :param doc: The host document of the tag's object.
        :type doc: c4d.documents.BaseDocument
        :param op: The host object of the tag.
        :type op: c4d.BaseObject
        :param bt: The Thread that execute the this TagData.
        :type bt: c4d.threading.BaseThread
        :param priority: Information about the execution priority of this TagData.
        :type priority: EXECUTIONPRIORITY
        :param flags: Information about when this TagData is executed.
        :type flags: EXECUTIONFLAGS
        :return:
        """
        # Retrieves the current active base draw
        bd = doc.GetRenderBaseDraw()
        if bd is None:
            return c4d.EXECUTIONRESULT_OK
        objs = doc.GetObjects()
        objs.remove(op)
        if (tag.GetData()[1002] == True):
            #print("MASTER")
            self.ExportEnabled = tag.GetData()[1004]
            self.exportRange = [int(tag.GetData()[1005]),int(tag.GetData()[1006])]
            self.exportPath = tag.GetData()[1007]
            if(self.port == None):
                #self.port = dmx.select_port()
                self.port = 512 * [0]
                pass
            for obj in objs:
                isLight = False;
                Tag = None
                for tag1 in obj.GetTags():
                    if tag1.GetType() == PLUGIN_ID:
                        Tag = tag1
                        break
                    pass
                if (Tag == None):
                    continue
                    pass
                self.Fixture = ChauvetRogueR1(obj)

                Layer = obj.GetLayerObject(doc)
                if(Layer.GetName() == 'Master'):
                    DMXAdr = Tag.GetData()[1000]
                    DMXUniv = Tag.GetData()[1001]
                    Lamp = obj.GetChildren()[0].GetChildren()[0].GetChildren()[0]
                    Layers = getFixturesAtAddress(DMXUniv,DMXAdr)
                    NewColor = c4d.Vector(0,0,0)
                    for LayerObj in Layers:
                        Lamp = LayerObj.GetChildren()[0].GetChildren()[0].GetChildren()[0]
                        NewColor = NewColor + Lamp.GetParameter(c4d.LIGHT_COLOR,c4d.DESCFLAGS_SET_0)
                    pass
                    self.Fixture.SetColor(NewColor)
                    self.Fixture.update(self.DMXPacket)
                    if(self.exportRange[0] == doc.GetTime().GetFrame(doc.GetFps())):
                        for i in range(len(self.exportChannelInfo)):
                            for j in self.Fixture.exportChannelInfo[i]:
                                self.exportChannelInfo[i].append(j)
                                pass
                            pass
                pass
            pass
            for i in range(0,511):
                if(int(self.DMXPacket[i]) > 256):
                    (self.DMXPacket[i]) = 255
                elif (int(self.DMXPacket[i]) < 0):
                    (self.DMXPacket[i]) = 0
                pass
                self.port[i] = int(self.DMXPacket[i])
                pass

            if(self.ExportEnabled == True):
                self.Export(tag,self.exportPath)



            #self.port.render()

        return c4d.EXECUTIONRESULT_OK

        def GetFixture(self):
            return self.Fixture









if __name__ == "__main__":
    # Retrieves the icon path
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "tpyC4DMX.png")

    # Creates a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    c4d.plugins.RegisterTagPlugin(id=PLUGIN_ID,
                                  str="C4DMX",
                                  info=c4d.TAG_EXPRESSION | c4d.TAG_VISIBLE,
                                  g=C4DMX,
                                  description="C4DMX",
                                  icon=bmp)
