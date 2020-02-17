import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages')
import pyenttec as dmx




BASEADR = 1
port = dmx.select_port()

for i in range(BASEADR-1,BASEADR+20):
    port[i] = 0
    pass
port.render()
