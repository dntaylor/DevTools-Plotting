import os
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.LimitPlotter import LimitPlotter
from copy import deepcopy
import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

blind = True

limitPlotter = LimitPlotter()

masses = [200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500]
modes = ['ee100','em100','et100','mm100','mt100','tt100','BP1','BP2','BP3','BP4']

limvals = {mode: {'AP':[],'PP':[]} for mode in modes}
filenames = {mode: {} for mode in modes}

for analysis,prod in [('Hpp3l','AP'),('Hpp3l','PP'),('Hpp4l',''),('HppAP',''),('HppPP',''),('HppComb','')]:
    for mode in modes:
        filenames[mode][analysis+prod] = ['asymptotic/{0}/{1}/{2}/limits{3}.txt'.format(analysis,mode,mass,prod) for mass in masses]
        kwargs = {
            'xaxis': '#Phi^{++} Mass (GeV)',
            'yaxis': '95% CLs Upper Limit on #sigma/#sigma_{model}',
        }
        label = analysis+prod
        limvals[mode][label] = limitPlotter.plotLimit(masses,filenames[mode][analysis+prod],'{0}{1}/{2}'.format(analysis,prod,mode),**kwargs)

for mode in modes:
    limitPlotter.plotCrossSectionLimit(masses,filenames[mode]['HppAP'],filenames[mode]['HppPP'],'HppComb/{0}_crossSection'.format(mode))

limitPlotter.moneyPlot(limvals,'moneyPlot')

