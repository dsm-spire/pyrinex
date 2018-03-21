from . import Path
import numpy as np
from datetime import datetime
from io import BytesIO
import xarray
#
STARTCOL2 = 3 #column where numerical data starts for RINEX 2

def _rinexnav2(fn, ofn=None):
    """
    Reads RINEX 2.11 NAV files
    Michael Hirsch, Ph.D.
    SciVision, Inc.

    It may actually be faster to read the entire file via f.read() and then .split()
    and asarray().reshape() to the final result, but I did it frame by frame since RINEX files
    may be enormous.

    http://gage14.upc.es/gLAB/HTML/GPS_Navigation_Rinex_v2.11.html
    ftp://igs.org/pub/data/format/rinex211.txt
    """
    fn = Path(fn).expanduser()

    Nl = 7 #number of additional lines per record, for RINEX 2 NAV
    Nf = 29 # number of fields per record, for RINEX 2 NAV
    Lf = 19 # string length per field

    sv = []; epoch=[]; raws=[]

    with fn.open('r') as f:
        """verify RINEX version, and that it's NAV"""
        line = f.readline()
        ver = float(line[:9])
        assert int(ver)==2,'see rinexnav3() for RINEX 3.0 files'
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
        for l in f:
            # format I2 http://gage.upc.edu/sites/default/files/gLAB/HTML/GPS_Navigation_Rinex_v2.11.html
            sv.append(int(l[:2]))
            # format I2
            year = int(l[3:5])  # yes, skipping one unused columsn
            if 80 <= year <=99:
                year += 1900
            elif year<80: #good till year 2180
                year += 2000

            epoch.append(datetime(year =year,
                                  month   =int(l[6:8]),
                                  day     =int(l[9:11]),
                                  hour    =int(l[12:14]),
                                  minute  =int(l[15:17]),
                                  second  =int(l[17:20]),  # python reads second and fraction in parts
                                  microsecond=int(l[21])*100000))
            """
            now get the data as one big long string per SV
            """
            raw = l[22:79]  # :79, NOT :80
            for _ in range(Nl):
                raw += f.readline()[STARTCOL2:79]
            # one line per SV
            raws.append(raw.replace('D','E'))
# %% parse
    # for RINEX 2, don't use delimiter
    Nt = len(raws)
    darr = np.empty((Nt, Nf))

    for i,r in enumerate(raws):
        darr[i,:] = np.genfromtxt(BytesIO(r.encode('ascii')), delimiter=[Lf]*Nf)

    nav = xarray.Dataset({'sv':              ('time',sv),
                          'SVclockBias':     ('time',darr[:,0]),
                          'SVclockDrift':    ('time',darr[:,1]),
                          'SVclockDriftRate':('time',darr[:,2]),
                          'IODE':            ('time',darr[:,3]),
                          'Crs':             ('time',darr[:,4]),
                          'DeltaN':          ('time',darr[:,5]),
                          'M0':              ('time',darr[:,6]),
                          'Cuc':             ('time',darr[:,7]),
                          'Eccentricity':    ('time',darr[:,8]),
                          'Cus':             ('time',darr[:,9]),
                          'sqrtA':           ('time',darr[:,10]),
                          'Toe':             ('time',darr[:,11]),
                          'Cic':             ('time',darr[:,12]),
                          'OMEGA0':          ('time',darr[:,13]),
                          'Cis':             ('time',darr[:,14]),
                          'Io':              ('time',darr[:,15]),
                          'Crc':             ('time',darr[:,16]),
                          'omega':           ('time',darr[:,17]),
                          'OMEGA DOT':       ('time',darr[:,18]),
                          'IDOT':            ('time',darr[:,19]),
                          'CodesL2':         ('time',darr[:,20]),
                          'GPSWeek':         ('time',darr[:,21]),
                          'L2Pflag':         ('time',darr[:,22]),
                          'SVacc':           ('time',darr[:,23]),
                          'SVhealth':        ('time',darr[:,24]),
                          'TGD':             ('time',darr[:,25]),
                          'IODC':            ('time',darr[:,26]),
                          'TransTime':       ('time',darr[:,27]),
                          'FitIntvl':        ('time',darr[:,28]),
                          },
                          coords={'time':epoch},
                          attrs={'RINEX version':ver,
                                 'RINEX filename':fn.name}
                          )


    if ofn:
        ofn = Path(ofn).expanduser()
        print('saving NAV data to',ofn)
        if ofn.is_file():
            wmode='a'
        else:
            wmode='w'
        nav.to_netcdf(ofn, group='NAV', mode=wmode)

    return nav