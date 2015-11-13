import urllib
import xml.etree.ElementTree as ET
import numpy as np
import time
from glob import glob
import subprocess

## Some notes:

# time.ctime(<times>) will give a str of the local Toronto time

homedir = '/home/meyer/dev/'

#class BikeShare(object):

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

    def updatetimes(self):
        print 'Last Update: '+ time.ctime(float(self.lastupdate)/1000.)
        print 'Last Comm: '+ time.ctime(float(self.lastcomm)/1000.)+'\n'

    
######
def getBikeBayData(url=True, fl=None):
    '''Acesses the Toronto Bike Share bike bay data file and returns a list of bike
    bay objects each with the information regarding each bay'''

    if url:
        url = 'http://www.bikesharetoronto.com/data/stations/bikeStations.xml'
        data = urllib.urlopen(url).read()
    
        # Make record of data
        #filepath = homedir + 'bikeshare-toronto-data/data/'+thetime+'.txt'
        #f = open(filepath,'w')
        #f.write(data)
        #f.close()
    
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

def get_most_recent():

    return glob(homedir+'bikeshare-toronto-data/data/*.txt')[-1]

def check_updated():

    recentfl = get_most_recent()
    recent_data = getBikeBayData(url=False,fl=recentfl)
    new_data = getBikeBayData()

    if len(new_data) != len(recent_data):
        return [True, 'New Bay']
    
    for bay in new_data:
        pass

def update_files(bikebays):
    
    for bay in bikebays:
        bayid = bay.id
        f = open(homedir+"bikeshare-toronto-data/data/"+str(id)+".txt",'a')
        f.write("%s\t%s")

def __init__datadir(clean=False, newbay=False):
    '''Initializes data directory with text files for all bike bays'''

    if clean == True:
        files = glob(homedir+"bikeshare-toronto-data/data/*.txt")
        for fl in files:
            command = ["rm", "-vf", fl]
            subprocess.Popen(command) 


    elif newbay:
        f = open(homedir+'bikeshare-toronto-data/data/%i.txt' % (newbay,), 'w')
        f.close()

    else:
        bikebays = getBikeBayData()
        for i in range(len(bikebays)):
            namearr = [str(bikebays[i].id)] + str(bikebays[i].street).split())
            
            name = '_'.join(namearr)
            
            f = open(homedir+'bikeshare-toronto-data/data/'+name+'.txt', 'w')
            f.write()
            f.close()
        


if __name__ == '__main__':

    root = getBikeBayData()
    __init__datadir(clean = True)
