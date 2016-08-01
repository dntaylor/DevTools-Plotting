import os
import sys
import logging
from itertools import product, combinations_with_replacement
import json
import pickle

from DevTools.Utilities.utilities import python_mkdir
from DevTools.Plotter.LimitPlotter import LimitPlotter
from copy import deepcopy
import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

blind = True

limitPlotter = LimitPlotter()

masses = [200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500]
modes = ['ee100','em100','et100','mm100','mt100','tt100','BP1','BP2','BP3','BP4']

limvals = {mode: {} for mode in modes}
filenames = {mode: {} for mode in modes}

for analysis,prod in [('Hpp3l','AP'),('Hpp3l','PP'),('Hpp4l',''),('HppAP',''),('HppPP',''),('HppComb','')]:
    for mode in modes:
        label = analysis+prod
        filenames[mode][label] = ['asymptotic/{0}/{1}/{2}/limits{3}.txt'.format(analysis,mode,mass,prod) for mass in masses]
        kwargs = {
            'xaxis': '#Phi^{++} Mass (GeV)',
            'yaxis': '95% CLs Upper Limit on #sigma/#sigma_{model}',
        }
        limvals[mode][label] = limitPlotter.plotLimit(masses,filenames[mode][label],'{0}/{1}'.format(label,mode),**kwargs)

for mode in modes:
    limitPlotter.plotCrossSectionLimit(masses,filenames[mode]['HppAP'],filenames[mode]['HppPP'],'HppComb/{0}_crossSection'.format(mode))

limitPlotter.moneyPlot(limvals,'moneyPlot')
limitPlotter.moneyPlot(limvals,'moneyPlot_prevExclusion',doPreviousExclusion=True)

def dumpResults(results,analysis,name):
    jfile = 'jsons/{0}/{1}.json'.format(analysis,name)
    pfile = 'pickles/{0}/{1}.pkl'.format(analysis,name)
    python_mkdir(os.path.dirname(jfile))
    python_mkdir(os.path.dirname(pfile))
    with open(jfile,'w') as f:
        f.write(json.dumps(results, indent=4, sort_keys=True))
    with open(pfile,'wb') as f:
        pickle.dump(results,f)


# save the limvals to a json file
dumpResults(limvals,'Limits','values')
