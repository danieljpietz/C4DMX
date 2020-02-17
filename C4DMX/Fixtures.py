class ChauvetRogueR1(object):
    """docstring for ChauvetRogueR1."""

    def __init__(self, root):
        super(ChauvetRogueR1, self).__init__()
        self.root = root

    def update(self, DMXPacket):
        obj = self.root
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

        RedVal = rangeMap(Color[0], [0, 1], [1,2**16])
        GreenVal = rangeMap(Color[1], [0, 1], [1,2**16])
        BlueVal = rangeMap(Color[2], [0, 1], [1,2**16])

        RedCourse = int(RedVal/256) - 1
        GreenCourse = int(GreenVal/256) - 1
        BlueCourse = int(BlueVal/256) - 1

        RedFine = int((RedVal % 256)) - 1
        GreenFine = int((GreenVal % 256)) - 1
        BlueFine = int((BlueVal % 256)) - 1

        DMXPacket[BASEADR-1] = PanCourse
        DMXPacket[BASEADR] = PanFine
        DMXPacket[BASEADR+1] = TiltCourse
        DMXPacket[BASEADR+2] = TiltFine
        DMXPacket[BASEADR+4] = 255
        DMXPacket[BASEADR+6] = 255
        DMXPacket[BASEADR+7] = RedCourse
        DMXPacket[BASEADR+8] = RedFine
        DMXPacket[BASEADR+11] = BlueCourse
        DMXPacket[BASEADR+12] = BlueFine
        DMXPacket[BASEADR+9] = GreenCourse
        DMXPacket[BASEADR+10] = GreenFine
        DMXPacket[BASEADR+16] = ZoomVal
        pass
pass
