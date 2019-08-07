import json
from urllib.request import urlopen
import xml.etree.ElementTree as ET
import numpy as np
import time
from glob import glob
import subprocess
import sqlite3

## Some notes:

# time.ctime(<times>) will give a str of the local Toronto time

## MAKE SURE YOU UPDATE THE BASE DIRECTORY (directory that contains
## bikeshare-toronto-data

#homedir = '/home/meyer/dev/'
#homedir = '/Users/relliotmeyer/gitrepos/Personal/'
#homedir = '/home/pi/'

#class BikeShare(object):

class BikeSystem(object):

    def __init__(self, homedir, olddatabase=False):
        self.homedir = homedir
        if self.homedir[-1] != '/':
            self.homedir += '/'
        self.old = olddatabase

        self.initDatabase(old=self.old)

    def initDatabase(self, old=False):
        '''Initializes the database file that will record the bike bay status.'''

        if not old:
            self.conn = sqlite3.connect(self.homedir + 'bikesystem_'+time.strftime('%Y%m%dT%H%M%S')+'.db')
        else:
            self.conn = sqlite3.connect(old)
            self.checkNewStations()
            return

        self.cursor = self.conn.cursor()

        self.stations = self.getStationData()
        self.status = self.getBikeBayData()

        self.cursor.execute('CREATE TABLE station_info (id INTEGER PRIMARY KEY, station_key INTEGER,\
                capacity INTEGER, name TEXT, lat REAL, lon REAL);')

        for station in self.stations:
            station_id = 'station_'+str(station['station_id'])

            self.cursor.execute('INSERT INTO station_info (station_key, capacity, name, lat, lon) \
                    VALUES (?, ?, ?, ?, ?);', (station['station_id'], station['capacity'],\
                    station['name'], station['lat'], station['lon']))
            self.cursor.execute('CREATE TABLE '+station_id+' (id INTEGER PRIMARY KEY, \
                    time INTEGER, last_reported INTEGER, \
                    num_bikes_available INTEGER, num_bikes_disabled INTEGER, num_docks_available INTEGER,\
                    num_docks_disabled INTEGER, is_installed INTEGER, is_renting INTEGER, \
                    is_returning INTEGER);')

            self.conn.commit()

        for station in self.status:

            self.cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
            stationtables = np.array(self.cursor.fetchall())

            station_id = 'station_'+str(station.bayid)
            currtime = int(time.time())

            if station_id not in stationtables[:,0]:
                print("Adding station table not in station_info: "+station_id)
                self.cursor.execute('CREATE TABLE '+station_id+' (id INTEGER PRIMARY KEY, \
                        time INTEGER, last_reported INTEGER, \
                        num_bikes_available INTEGER, num_bikes_disabled INTEGER, num_docks_available INTEGER,\
                        num_docks_disabled INTEGER, is_installed INTEGER, is_renting INTEGER, \
                        is_returning INTEGER);')

            self.cursor.execute('INSERT INTO '+station_id+' (time, last_reported, num_bikes_available, \
                    num_bikes_disabled, num_docks_available, num_docks_disabled, \
                    is_installed, is_renting, is_returning) VALUES \
                    (?, ?, ?, ?, ?, ?, ?, ?, ?);', (currtime, station.lastcomm,\
                    station.nbikes, station.nbikes_dis, station.ndocks, station.ndocks_dis,\
                    station.installed, station.renting, station.returning))


        self.conn.commit()

    def closeDatabase(self):
        
        self.conn.close()

    def updateDatabase(self):

        self.stations = self.getStationData()
        self.status = self.getBikeBayData()

        self.cursor.execute('SELECT station_key FROM station_info;')
        stationkeys = np.array(self.cursor.fetchall())

        self.cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
        stationtables = np.array(self.cursor.fetchall())

        for station in self.stations:
            if int(station['station_id']) not in stationkeys[:,0]:
                print("Adding new station info: "+str(station['station_id']))
                self.cursor.execute('INSERT INTO station_info (station_key, capacity, name, lat, lon) \
                        VALUES (?, ?, ?, ?, ?);', (station['station_id'], station['capacity'],\
                        station['name'], station['lat'], station['lon']))

        self.conn.commit()


        for station in self.status:
            station_id = 'station_'+str(station.bayid)
            currtime = int(time.time())

            if station_id not in stationtables[:,0]:
                print("Adding new station table: "+station_id)
                self.cursor.execute('CREATE TABLE '+station_id+' (id INTEGER PRIMARY KEY, \
                        time INTEGER, last_reported INTEGER, \
                        num_bikes_available INTEGER, num_bikes_disabled INTEGER, num_docks_available INTEGER,\
                        num_docks_disabled INTEGER, is_installed INTEGER, is_renting INTEGER, \
                        is_returning INTEGER);')

            self.cursor.execute('INSERT INTO '+station_id+' (time, last_reported, num_bikes_available, \
                    num_bikes_disabled, num_docks_available, num_docks_disabled, \
                    is_installed, is_renting, is_returning) VALUES \
                    (?, ?, ?, ?, ?, ?, ?, ?, ?);', (currtime, station.lastcomm,\
                    station.nbikes, station.nbikes_dis, station.ndocks, station.ndocks_dis,\
                    station.installed, station.renting, station.returning))

            self.conn.commit()

    def getStationData(self):
        
        stationurl = 'https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_information'
        stationjson = parseJSON(stationurl)

        stations = stationjson['data']['stations']

        return stations

        #    for station in stations:
        #        f.write('station_id:\t'+str(station['station_id'])+'\n')
        #        f.write('capacity:\t'+str(station['capacity'])+'\n')
        #        f.write('name:\t\t'+str(station['name'])+'\n')
        #        f.write('lat:\t\t'+str(station['lat'])+'\n')
        #        f.write('long:\t\t'+str(station['lon'])+'\n\n')

    def getBikeBayData(self, write=False):
        '''Acesses the Toronto Bike Share bike bay data file and returns a list of bike
        bay objects each with the information regarding each bay'''


        bikeurl = 'https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_status'
        bikejson = parseJSON(bikeurl)
      
        bb = bikejson['data']['stations']
        bikebays = []
        for st in bb:
            bikebays.append(BikeBay(st['station_id'],st['last_reported'],st['num_bikes_available'],\
                st['num_bikes_disabled'],st['num_docks_available'],st['num_docks_disabled'],\
                st['is_installed'], st['is_renting'],st['is_returning']))
        
        #if write:
        #    for bay in bikebays:
        #        update_file(bay)

        return bikebays
        
    def run(self):

        starttime = time.time()
        try:
            while True:
                self.updateDatabase()
                print("It has been " + str((time.time()-starttime)/60.0)+" minutes since starting.")
                time.sleep(59)
        finally:
            print("Closing database...")
            self.closeDatabase()

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
