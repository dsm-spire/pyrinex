#!/usr/bin/env python
from matplotlib.pyplot import show
#
from pyrinex import rinexnav,rinexobs
from pyrinex.plots import plotnav, plotobs

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='example of reading RINEX 2/3 Navigation/Observation file')
    p.add_argument('rinexfn',help='path to RINEX 2 or RINEX 3 file')
    p.add_argument('-o','--outfn',help='write data as NetCDF4 file')
    p.add_argument('-v','--verbose',action='store_true')
    p.add_argument('-use',help='select which GNSS systems to use (for now, GPS only)',nargs='+',default='G')
    p = p.parse_args()

    rinexfn = p.rinexfn
    if rinexfn.lower().endswith('n') or rinexfn.lower().endswith('n.rnx'):
        nav = rinexnav(rinexfn, p.outfn)

        plotnav(nav)
    elif rinexfn.lower().endswith('o') or rinexfn.lower().endswith('o.rnx'):
        obs = rinexobs(rinexfn, p.outfn, p.use, p.verbose)

        plotobs(obs)
    #%% TEC can be made another column (on the last axis) of the blocks array.
    else:
        raise ValueError("I dont know what type of file you're trying to read: {}".format(p.rinexfn))

    show()
