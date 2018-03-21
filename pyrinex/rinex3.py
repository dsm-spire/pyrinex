from . import Path
import numpy as np
from datetime import datetime
from io import BytesIO
import xarray
#
STARTCOL3 = 4 #column where numerical data starts for RINEX 3
"""https://github.com/mvglasow/satstat/wiki/NMEA-IDs"""
SBAS=100 # offset for ID
GLONASS=37
QZSS=192
BEIDOU=0

def _rinexnav3(fn, ofn=None):
    """
    Reads RINEX 3.0 NAV files

    http://www.gage.es/sites/default/files/gLAB/HTML/SBAS_Navigation_Rinex_v3.01.html
    """
    fn = Path(fn).expanduser()

    svs = []; epoch=[]; raws=''

    with fn.open('r') as f:
        """verify RINEX version, and that it's NAV"""
        line = f.readline()
        assert int(float(line[:9]))==3,'see rinexnav2() for RINEX 3.0 files'
        assert line[20] == 'N', 'Did not detect Nav file'

        """
        skip header, which has non-constant number of rows
        """
        while True:
            if 'END OF HEADER' in f.readline():
                break
        """
        now read data
        """
        line = f.readline()
        while True:
            sv,t,fields,svtype = _newnav(line)
            svs.append(sv)
            epoch.append(t)
# %% get the data as one big long string per SV, unknown # of lines per SV
            raw = line[23:80]

            while True:
                line = f.readline()
                if not line or line[0] != ' ': # new SV
                    break

                raw += line[STARTCOL3:80]
            # one line per SV
            raws += raw + '\n'

            if not line: # EOF
                break

    raws = raws.replace('D','E')
# %% parse
    darr = np.genfromtxt(BytesIO(raws.encode('ascii')),
                         delimiter=19)

    nav= xarray.DataArray(data=np.concatenate((np.atleast_2d(svs).T, darr), axis=1),
                coords={'t':epoch,
                'data':fields},
                dims=['t','data'],
                name=svtype)

    if ofn:
        ofn = Path(ofn).expanduser()
        print('saving NAV data to',ofn)
        if ofn.is_file():
            wmode='a'
        else:
            wmode='w'
        nav.to_netcdf(ofn, group='NAV', mode=wmode)

    return nav


def _newnav(l):
    sv = l[:3]

    svtype = sv[0]

    if svtype == 'G':
        sv = int(sv[1:]) + 0
        fields = ['sv','aGf0','aGf1','SVclockDriftRate',
                  'IODE','Crs','DeltaN','M0',
                  'Cuc','Eccentricity','Cus','sqrtA',
                  'Toe','Cic','OMEGA0','Cis',
                  'Io','Crc','omega','OMEGA DOT',
                  'IDOT','CodesL2','GPSWeek','L2Pflag',
                  'SVacc','SVhealth','TGD','IODC',
                  'TransTime','FitIntvl']
    elif svtype == 'C':
        sv = int(sv[1:]) + BEIDOU
    elif svtype == 'R':
        sv = int(sv[1:]) + GLONASS
    elif svtype == 'S':
        sv = int(sv[1:]) + SBAS
        fields=['sv','aGf0','aGf1','MsgTxTime',
                'X','dX','dX2','SVhealth',
                'Y','dY','dY2','URA',
                'Z','dZ','dZ2','IODN']
    elif svtype == 'J':
        sv = int(sv[1:]) + QZSS
    elif svtype == 'E':
        raise NotImplementedError('Galileo PRN not yet known')
    else:
        raise ValueError('Unknown SV type {}'.format(sv[0]))


    year = int(l[4:8]) # I4

    t = datetime(year = year,
                  month   =int(l[9:11]),
                  day     =int(l[12:14]),
                  hour    =int(l[15:17]),
                  minute  =int(l[18:20]),
                  second  =int(l[21:23]))

    return sv, t, fields,svtype
