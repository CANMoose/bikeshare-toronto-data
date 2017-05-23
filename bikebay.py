import json
from urllib.request import urlopen
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
homedir = '/Users/relliotmeyer/gitrepos/Personal/'
#homedir = '/home/pi/'

#class BikeShare(object):

class BikeBay(object):

    def __init__(self, bayid, lastcomm, b_avail, b_dis, d_avail, d_dis, installed,\
        renting, returning):
        self.bayid = int(bayid)
        self.lastcomm = int(lastcomm)
        self.nbikes = int(b_avail)
        self.nbikes_dis = int(b_dis)
        self.ndocks = int(d_avail)
        self.ndocks_dis = int(d_dis)
        self.installed = installed
        self.renting = renting
        self.returning = returning

    def updatetimes(self):
        #print 'Last Update: '+ time.ctime(self.lastupdate)/1000.
        print('Last Comm: '+ time.ctime(self.lastcomm/1000.)+'\n')

######
def parseJSON(url):

    raw = urlopen(url).read()
    urlstr = raw.decode('utf-8')
    urljson = json.loads(urlstr)

    return urljson

def getStationData(write=False):
    
    stationurl = 'https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_information'
    stationjson = parseJSON(stationurl)

    stations = stationjson['data']['stations']

    if write:
        f = open(homedir+'bikeshare-toronto-data/data/stations_info.txt', 'w')
        for station in stations:
            f.write('station_id:\t'+str(station['station_id'])+'\n')
            f.write('capacity:\t'+str(station['capacity'])+'\n')
            f.write('name:\t\t'+str(station['name'])+'\n')
            f.write('lat:\t\t'+str(station['lat'])+'\n')
            f.write('long:\t\t'+str(station['lon'])+'\n\n')
        f.close()

    return stations

def getBikeBayData(write=False):
    '''Acesses the Toronto Bike Share bike bay data file and returns a list of bike
    bay objects each with the information regarding each bay'''

    #OldURL
    #url = 'http://feeds.bikesharetoronto.com/stations/stations.xml'

    bikeurl = 'https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_status'
    bikejson = parseJSON(bikeurl)
  
    bb = bikejson['data']['stations']
    bikebays = []
    for st in bb:
        bikebays.append(BikeBay(st['station_id'],st['last_reported'],st['num_bikes_available'],\
            st['num_bikes_disabled'],st['num_docks_available'],st['num_docks_disabled'],\
            st['is_installed'], st['is_renting'],st['is_returning']))
    
    if write:
        for bay in bikebays:
            update_file(bay)

    return bikebays

def get_datafile():

    datafiles = glob(homedir+'bikeshare-toronto-data/data/*.txt')
    datafiles_id = []
    
    for datafile in datafiles:
        datafiles_id.append(int((datafile.split('/')[-1]).split('.')[0]))

    try:
        whereid = np.where(np.array(datafiles_id) == ind)[0][0]
    except:
        print("Possibly new bikebay, please restart script")
        return None, None, None

    return [whereid, datafiles[whereid], datafiles]

def update_file(bay):
    
    bayid = bay.bayid

    try:
        f = open(homedir+'bikeshare-toronto-data/data/'+str(bayid)+'.txt', 'a')
        f.write("%s\t%s\t%s\t%s\t\t%s\t%s\t\t\t%s\t\t%s\t%s\n" % \
            (str(bay.lastcomm/1000), str(int(time.time())), str(bay.nbikes), \
            str(bay.nbikes_dis), str(bay.ndocks), str(bay.ndocks_dis), str(bay.installed),\
            str(bay.renting), str(bay.returning)))
        f.close()
    except:
        pass

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
        for bay in bikebays:
            f = open(homedir+'bikeshare-toronto-data/data/'+str(bay.bayid)+'.txt', 'w')
            f.write('LastComm\tRead_Time\tN_Bikes\tN_Disabled\tN_Docks\tN_Docks_Disabled\tInstalled\tRenting\tReturning\n')
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
            update_file(bay)

        print("It has been " + str((time.time()-starttime)/60.0)+" minutes since starting.")
        time.sleep(60)

if __name__ == '__main__':
    
    __init__datadir(clean=True)
    getStationData(write=True)
    __init__datadir()
    acquire_data()
