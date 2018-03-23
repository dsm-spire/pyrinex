#!/usr/bin/env python
"""
Self-test file, registration case
for OBS RINEX reader
"""
import xarray
from pyrinex import Path
from numpy.testing import  run_module_suite
#
from pyrinex import rinexobs, rinexnav
#
rdir=Path(__file__).parent

# %% RINEX 2
def test_obs2_allsat():
    """./ReadRinex.py tests/demo.10o -u all -o tests/test2all.nc"""

    truth = xarray.open_dataset(rdir/'test2all.nc', group='OBS')

# %% test reading all satellites
    for u in (None,'m','all',' ','',['G','R','S']):
        obs = rinexobs(rdir/'demo.10o', use=u)
        assert obs.equals(truth)

def test_obs2_onesat():
    """./ReadRinex.py tests/demo.10o -u G -o tests/test2G.nc"""

    truth = xarray.open_dataset(rdir/'test2G.nc', group='OBS')

    for u in ('G',['G']):
        obs = rinexobs(rdir/'demo.10o', use=u)
        assert obs.equals(truth)

def test_obs2_twosat():
    """./ReadRinex.py tests/demo.10o -u G R -o tests/test2GR.nc"""

    truth = xarray.open_dataset(rdir/'test2GR.nc', group='OBS')

    obs = rinexobs(rdir/'demo.10o', use=('G','R'))
    assert obs.equals(truth)


def test_nav2():
    """./ReadRinex.py tests/demo.10n -o tests/test2all.nc"""

    truth = xarray.open_dataset(rdir/'test2all.nc', group='NAV')
    nav = rinexnav(rdir/'demo.10n')

    assert nav.equals(truth)
# %% RINEX 3

def test_obs3_onesat():
    """
    ./ReadRinex.py tests/demo3.10o -o tests/test3.nc
    One at a time only for now RINEX 3 -- not a big deal since processing is so fast.
    """

    truth = xarray.open_dataset(rdir/'test3.nc', group='OBS')

    for u in ('G',['G']):
        obs = rinexobs(rdir/'demo3.10o', use=u)
        assert obs.equals(truth)


def test_nav3sbas():
    """./ReadRinex.py tests/demo3.10n -o tests/test3sbas.nc"""
    truth = xarray.open_dataset(rdir/'test3sbas.nc', group='NAV')
    nav = rinexnav(rdir/'demo3.10n')

    assert nav.equals(truth)

def test_nav3gps():
    """./ReadRinex.py tests/demo.17n -o tests/test3gps.nc"""
    truth = xarray.open_dataset(rdir/'test3gps.nc', group='NAV')
    nav = rinexnav(rdir/'demo.17n')

    assert nav.equals(truth)


if __name__ == '__main__':
    run_module_suite()
