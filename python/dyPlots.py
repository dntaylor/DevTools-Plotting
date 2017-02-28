import os
import sys
import logging

from DevTools.Plotter.Plotter import Plotter
from copy import deepcopy

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

dyPlotter = Plotter('DY')

chans = ['ee','mm']

labelMap = {
    'e': 'e',
    'm': '#mu',
    't': '#tau',
}
chanLabels = [''.join([labelMap[c] for c in chan]) for chan in chans]

sigMap = {
    'Z'   : [
             #'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             #'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            ],
    'TT'  : [
             'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            ],
    'data': [
             'DoubleMuon',
             'DoubleEG',
             'SingleMuon',
             'SingleElectron',
            ],
}

samples = ['TT','Z']

for s in samples:
    dyPlotter.addHistogramToStack(s,sigMap[s])

dyPlotter.addHistogram('data',sigMap['data'])

# per channel counts
countVars = ['default/count'] + ['default/{0}/count'.format(chan) for chan in chans]
countLabels = ['Total'] + chanLabels
savename = 'individualChannels'
dyPlotter.plotCounts(countVars,countLabels,savename,numcol=2)


# plot definitions
plots = {
    # z cand
    'zMass'                 : {'xaxis': 'm_{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 2 GeV', 'rebin': 20, 'rangex': [50,200], 'logy':1},
    'zPt'                   : {'xaxis': 'p_{T}^{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 50, 'rangex': [0,150]},
    'zDeltaR'               : {'xaxis': '#DeltaR(l^{+}l^{-})', 'yaxis': 'Events', 'rebin': 10},
    'zLeadingLeptonPt'      : {'xaxis': 'p_{T}^{Z_{lead}} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 50, 'rangex': [25,150]},
    'zLeadingLeptonIso'     : {'xaxis': 'Rel. Iso.', 'yaxis': 'Events', 'rebin': 10, 'rangex': [0,0.2]},
    'zSubLeadingLeptonPt'   : {'xaxis': 'p_{T}^{Z_{sublead}} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 50, 'rangex': [20,150]},
    'zSubLeadingLeptonIso'  : {'xaxis': 'Rel. Iso.', 'yaxis': 'Events', 'rebin': 10, 'rangex': [0,0.2]},
    # event
    'numVertices'           : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_noreweight': {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'rho'                   : {'xaxis': '#rho', 'yaxis': 'Events'},
    'rho_noreweight'        : {'xaxis': '#rho', 'yaxis': 'Events'},
    'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5, 'rangex': [0,200]},
    'metPhi'                : {'xaxis': '#phi_{E_{T}^{miss}}', 'yaxis': 'Events', 'rebin': 10, 'numcol': 3, 'legendpos': 34},
    'nJets'                 : {'xaxis': 'Number of jets (p_{T} > 30 GeV)', 'yaxis': 'Events', 'rebin': 1},
}

# signal region
for plot in plots:
    plotname = 'default/{0}'.format(plot)
    dyPlotter.plot(plotname,plot,**plots[plot])
    for chan in chans:
        plotname = 'default/{0}/{1}'.format(chan,plot)
        savename = '{0}/{1}'.format(chan,plot)
        dyPlotter.plot(plotname,savename,**plots[plot])

# pileup plots

pileup = {
    'numVertices_60000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_61000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_62000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_63000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_64000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_65000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_66000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_67000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_68000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_69000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_70000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_71000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_72000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_73000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_74000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_75000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_76000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_77000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_78000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_79000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_80000'     : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'numVertices_noreweight': {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
}

#for plot in pileup:
#    plotname = 'default/{0}'.format(plot)
#    savename = 'pileup/{0}'.format(plot)
#    dyPlotter.plot(plotname,savename,**pileup[plot])
#    for chan in chans:
#        plotname = 'default/{0}/{1}'.format(chan,plot)
#        savename = '{0}/pileup/{1}'.format(chan,plot)
#        dyPlotter.plot(plotname,savename,**pileup[plot])
