import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.Plotter import Plotter
from DevTools.Utilities.utilities import ZMASS
from DevTools.Plotter.higgsUtilities import getSigMap
from copy import deepcopy
import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

blind = False

plotter = Plotter('ThreeLepton')

#########################
### Define categories ###
#########################

sigMap = getSigMap('Hpp3l')


samples = ['TTV','VVV','ZZ','WZ']
allsamples = ['W','T','TT','TTV','Z','WW','VVV','ZZ','WZ']

allSamplesDict = {'BG':[]}
for s in allsamples:
    allSamplesDict['BG'] += sigMap[s]


########################
### plot definitions ###
########################
plots = {
    'Pt'    : {'xaxis': 'p_{T} (GeV)', 'yaxis': 'Events / 10 GeV', 'rebin': 10, 'numcol': 3, 'legendpos':34, 'rangex': [10,250]},
}


############################
### MC based BG estimate ###
############################
for s in allsamples:
    plotter.addHistogramToStack(s,sigMap[s])

if not blind: plotter.addHistogram('data',sigMap['data'])

lepChan = {
    'e1': ['3e0m','2e1m','1e2m'],
    'e2': ['3e0m','2e1m'],
    'm1': ['2e1m','1e2m','0e3m'],
    'm2': ['1e2m','0e3m'],
}
for lep in lepChan:
    for plot in plots:
        kwargs = deepcopy(plots[plot])
        plotname = ['{0}/{1}{2}'.format(chan,lep,plot) for chan in lepChan[lep]]
        savename = 'mc/{0}{1}'.format(lep,plot)
        plotter.plot(plotname,savename,**kwargs)

