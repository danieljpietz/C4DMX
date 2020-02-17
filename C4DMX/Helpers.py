import numpy as np






def rangeMap(x,inRange,outRange):
    x = x - inRange[0]
    x = (outRange[1] - outRange[0]) * x / (inRange[1] - inRange[0])
    x = x + outRange[0]
    return x
