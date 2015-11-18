import urllib
import xml.etree.ElementTree as ET
import numpy as np
import time
from glob import glob
import subprocess

## Some notes:

# time.ctime(<times>) will give a str of the local Toronto time

## MAKE SURE YOU UPDATE THE BASE DIRECTORY (directory that contains
## bikeshare-toronto-data

#homedir = '/home/meyer/dev/'
#homedir = '/Users/relliotmeyer/gitrepos/'
homedir = '/home/pi/'

#class BikeShare(object):

class BikeBay(object):

    def __init__(self, bayid, street, terminalname, lastcomm, lat, lon, installed, locked,\
        temporary, public, nbikes, nempty, lastupdate):
        self.id = int(bayid)
        self.street = street
        self.terminalname = terminalname
        self.lastcomm = int(lastcomm)
        self.lat = lat
        self.long = lon
        self.installed = installed
        self.locked = locked
        self.temporary = temporary
        self.public = public
        self.nbikes = int(nbikes)
        self.nempty = int(nempty)
        self.lastupdate = int(lastupdate)

    def updatetimes(self):
        print 'Last Update: '+ time.ctime(self.lastupdate)/1000.
        print 'Last Comm: '+ time.ctime(self.lastcomm/1000.)+'\n'

    
######
def getBikeBayData(url=True, write=False):
    '''Acesses the Toronto Bike Share bike bay data file and returns a list of bike
    bay objects each with the information regarding each bay'''

    if url:
        url = 'http://www.bikesharetoronto.com/data/stations/bikeStations.xml'
        data = urllib.urlopen(url).read()

    root = ET.fromstring(data)

    bikebays = []

    for i, st in enumerate(root):
        bikebays.append(BikeBay(st[0].text,st[1].text,st[2].text,st[3].text,\
            st[4].text,st[5].text,st[6].text,st[7].text,st[10].text,st[11].text,\
            st[12].text,st[13].text,st[14].text))
    
    if url and write:
        for bay in bikebays:
            update_file(bay)

    return bikebays

def check_if_updated(bay):

    bayid = bay.id
    whereid, filename, datafiles = get_bikebayfile(bayid)
    
    f = open(filename, 'r')
    lines = f.readlines()[1:]
    f.close()
    
    last_line = lines[-1]
    last_updated = float(last_line.split()[1])
    
    if last_updated < bay.lastupdate:
        return True
    else:
        return False

def get_datafiles():

    datafiles = glob(homedir+'bikeshare-toronto-data/data/*.txt')
    datafiles_id = []
    
    for datafile in datafiles:
        datafiles_id.append(int((datafile.split('/')[-1]).split('_')[0]))

    return [datafiles, datafiles_id]

def get_bikebayfile(ind):
    
    datafiles, datafiles_id = get_datafiles()

    whereid = np.where(np.array(datafiles_id) == ind)[0][0]

    return [whereid, datafiles[whereid], datafiles]

def update_file(bay):
    
    bayid = bay.id
    whereid, filename, datafiles = get_bikebayfile(bayid)
    f = open(filename, 'a')
    f.write("%s\t%s\t%s\t%s\n" % (str(bay.lastcomm), str(bay.lastupdate), \
        str(bay.nbikes), str(bay.nempty)))
    f.close()

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
            street = bikebays[i].street
            street = street.replace('/ ','')
            street = street.replace('/',' ')
            namearr = [str(bikebays[i].id)] + str(street).split()
            
            name = '_'.join(namearr)
            
            f = open(homedir+'bikeshare-toronto-data/data/'+name+'.txt', 'w')
            f.write('LastComm\tLastUpdate\tN_Bikes\tN_Empty\n')
            f.close()
        getBikeBayData(write = True)
        
def acquire_data():

    starttime = time.time()
    while True:
        try:
            bikebays = getBikeBayData()
        except:
            continue
        for bay in bikebays:
            updated = check_if_updated(bay)
            if updated:
                print "Updating bikebay #"+str(bay.id)+ ' ' + str(bay.street)
                update_file(bay)
        time.sleep(30)
        print "It has been " + str((time.time()-starttime)/60.0)+" minutes since starting."

if __name__ == '__main__':
    
    __init__datadir(clean=True)
    __init__datadir()
    acquire_data()
