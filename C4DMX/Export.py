import marshal
from time import sleep

path = '/Users/danielpietz/Documents/Lighting/Exports/Export.rdmx'
f = open(path, "rb")
DMXAr = marshal.load(f)
f.close()
MetaDeta = DMXAr.pop()
fps = MetaDeta[0]
BPM = MetaDeta[1]
print(fps)
print(BPM)
#print(DMXAr)
i = 0
for packet in DMXAr:
    #print(i)
    #print(packet)
    i = i+1
    sleep(float(1)/fps)
