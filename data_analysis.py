import urllib
import xml.etree.ElementTree as ET
import numpy as np
import time

## Some notes:

# time.ctime(<times>) will give a str of the local Toronto time

class BikeBay(object):

    def __init__(self, bayid, street, terminalname, lastcomm, lat, lon, installed, locked,\
        temporary, public, nbikes, nempty, lastupdate):
        self.id = bayid
        self.street = street
        self.terminalname = terminalname
        self.lastcomm = lastcomm
        self.lat = lat
        self.long = lon
        self.installed = installed
        self.locked = locked
        self.temporary = temporary
        self.public = public
        self.nbikes = nbikes
        self.nempty = nempty
        self.lastupdate = lastupdate

######
def getBikeBayData(url=True, fl=None):
    '''Acesses the Toronto Bike Share bike bay data file and returns a list of bike
    bay objects each with the information regarding each bay'''

    if url:
        url = 'http://www.bikesharetoronto.com/data/stations/bikeStations.xml'
        data = urllib.urlopen(url).read()
    
        # Make record of data
        f = open('/Users/relliotmeyer/gitrepos/bikeshare-toronto-data/data/'+time.asctime()+'.txt','w')
        f.write(data)
        f.close()
    
    elif fl:
        flopen = open(fl,'r')
        data = flopen.read()

    root = ET.fromstring(data)

    bikebays = []

    for i, st in enumerate(root):
        bikebays.append(BikeBay(st[0].text,st[1].text,st[2].text,st[3].text,\
            st[4].text,st[5].text,st[6].text,st[7].text,st[10].text,st[11].text,\
            st[12].text,st[13].text,st[14].text))
        
    return bikebays

def check_updated(last):

    new_data = getBikeBayData()

    for bay in new_data:
        pass
        


if __name__ == '__main__':

    root = getBikeBayData()

