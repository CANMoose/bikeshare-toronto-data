import bikebay as bb
import numpy as np
import matplotlib.pyplot as mpl
import time
from glob import glob

def write_localtimes(ind):
    '''Converts a bikebay log file into easily read local times'''

    whereid, datafile, datafiles = bb.get_bikebayfile(ind)

    f = open(datafile)
    lines = f.readlines()[1:]

    for line in lines:
        spl = line.split()
        print time.ctime(float(spl[1])/1000.), \
            spl[2],spl[3], int(spl[2]) + int(spl[3])

def check_nobikes(fl):

    data = read_file(fl)

    n_bikes = data[:,2]

    if 0 in n_bikes:
        return True
    else:
        return False

def read_file(fl):

    f = open(fl)
    lines = f.readlines()[1:]

    spl_lines = []
    for line in lines:
        spl = [int(i) for i in line.split()]
        spl_lines.append(spl)

    spl_lines = np.array(spl_lines)

    return spl_lines

def build_datacube():

    datafiles, datafiles_id = bb.get_datafiles()
    cube = []
    for fl in datafiles:
        data = read_file(fl)
        cube.append(data[:,1:])

    return cube

if __name__ == '__main__':
    
    write_localtimes(88)

    #datafiles, datafiles_id = bb.get_datafiles()
    #for fl in datafiles:
    #    if check_nobikes(fl):
    #        print fl.split()[-1]
    cube = build_datacube()
   
    bay = cube[30]
    times = bay[:,1]
    n_bikes = bay[:,2]
    mpl.plot(times,n_bikes)
    mpl.show()

