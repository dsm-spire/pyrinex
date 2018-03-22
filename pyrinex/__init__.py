from __future__ import division  # absolutely needed for Py27 strange behavior
try:
    from pathlib import Path
    Path().expanduser()
except (ImportError,AttributeError):
    from pathlib2 import Path
#
import xarray
from time import time
#
from .rinex2 import _rinexnav2, _scan2
from .rinex3 import _rinexnav3, _scan3


def getRinexVersion(fn):
    fn = Path(fn).expanduser()

    with fn.open('r') as f:
        """verify RINEX version"""
        line = f.readline()
        return float(line[:9])

#%% Navigation file
def rinexnav(fn, ofn=None):

    ver = getRinexVersion(fn)

    if int(ver) == 2:
        return _rinexnav2(fn,ofn)
    elif int(ver) == 3:
        return _rinexnav3(fn,ofn)
    else:
        raise ValueError('unknown RINEX verion {}  {}'.format(ver,fn))


# %% Observation File
def rinexobs(fn, ofn=None, use=None, verbose=False):
    """
    Program overviw:
    1) scan the whole file for the header and other information using scan(lines)
    2) each epoch is read

    rinexobs() returns the data in an xarray.Dataset
    """

    ver = getRinexVersion(fn)
    #open file, get header info, possibly speed up reading data with a premade h5 file
    fn = Path(fn).expanduser()
    if fn.suffix=='.nc':
        return xarray.open_dataset(fn, group='OBS')


        tic = time()
    if int(ver) == 2:
        data = _scan2(fn, verbose)
    elif int(ver) == 3:
        data = _scan3(fn, use, verbose)
    else:
        raise ValueError('unknown RINEX verion {}  {}'.format(ver,fn))
        print("finished in {:.2f} seconds".format(time()-tic))


    if ofn:
        ofn = Path(ofn).expanduser()
        print('saving OBS data to',ofn)
        wmode='a' if ofn.is_file() else 'w'

        data.to_netcdf(ofn, group='OBS', mode=wmode)

    return data


