import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.Plotter import Plotter
from DevTools.Utilities.utilities import ZMASS, getCMSSWVersion
from copy import deepcopy
import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

version = getCMSSWVersion()

blind = True

plotter = Plotter('MonoHZZ',new=True)

#########################
### Define categories ###
#########################

sigMap = {
    'Z'   : [
            'DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            'DYJetsToLL_M-10to50_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            ],
    'TT'  : [
            #'TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
            #'TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8',
            #'TT_DiLept_TuneCP5_13TeV-amcatnlo-pythia8',
            'TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            ],
    'WW' : [
            'WWTo2L2Nu_NNPDF31_TuneCP5_13TeV-powheg-pythia8',
            ],
    'WZ' : [
            'WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            #'WZTo3LNu_13TeV-powheg-pythia8',
            'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            ],
    'ZZ' : [
            'ZZTo4L_13TeV_powheg_pythia8',
            'ZZTo2L2Nu_13TeV_powheg_pythia8',
            #'ZZTo2L2Q_13TeV_powheg_pythia8',
            'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            #'GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8',
            #'GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8',
            #'GluGluToContinToZZTo2e2tau_13TeV_MCFM701_pythia8',
            #'GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8',
            #'GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8',
            #'GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8',
            ],
    'TTV' : [
            'ttWJets_TuneCP5_13TeV_madgraphMLM_pythia8',
            'ttZJets_TuneCP5_13TeV_madgraphMLM_pythia8',
            ],
    'VVV' : [
            'WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8',
            'WWZ_4F_TuneCP5_13TeV-amcatnlo-pythia8',
            'WZG_TuneCP5_13TeV-amcatnlo-pythia8',
            'WZZ_TuneCP5_13TeV-amcatnlo-pythia8',
            'ZZZ_TuneCP5_13TeV-amcatnlo-pythia8',
            ],
    'HZZ' : [
            'GluGluHToZZTo4L_M125_13TeV_powheg2_JHUGenV7011_pythia8',
            'VBF_HToZZTo4L_M125_13TeV_powheg2_JHUGenV7011_pythia8',
            #'WminusH_HToZZTo4L_M125_13TeV_powheg2-minlo-HWJ_JHUGenV7011_pythia8',
            #'WplusH_HToZZTo4L_M125_13TeV_powheg2-minlo-HWJ_JHUGenV7011_pythia8',
            #'ttH_HToZZ_4LFilter_M125_13TeV_powheg2_JHUGenV7011_pythia8',
            #'ZH_HToZZ_4LFilter_M125_13TeV_powheg2-minlo-HZJ_JHUGenV7011_pythia8',
            ],
    'data' : [
            'DoubleMuon',
            'DoubleEG',
            'MuonEG',
            'SingleMuon',
            'SingleElectron',
            ],
}

samples = ['TT','TTV','Z','WZ','VVV','ZZ','HZZ']



########################
### plot definitions ###
########################
plots = {
    # h
    'hMass'                 : {'xaxis': 'm_{4l} (GeV)', 'yaxis': 'Events / 2 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(70,172,2),},# 'logx': True,},
    # z cand
    'z1Mass'                : {'xaxis': 'm_{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 2 GeV', 'rebin': range(40,122,2), 'numcol': 3, 'legendpos':34, 'yscale': 1.5,},
    'z2Mass'                : {'xaxis': 'm_{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 2 GeV', 'rebin': range(12,122,2), 'numcol': 3, 'legendpos':34, 'yscale': 1.5,},
    # event
    #'numVertices'           : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': range(0,300,5), 'numcol': 2, 'legendpos':34,  'logy': True, 'overflow': True, 'ymin': 1e-2,},
}

alt_plots = {
    'hMass' : {
        'hMass_full': {'yaxis': 'Events / 3 GeV', 'rebin': range(72,1002,3), 'logx': True,},
    },
}

blind_cust = {
    'hMass' : {'blinder': [116,130],},
    'z2Mass': {'blinder': [12,60],},
    'met'   : {'blinder': [50,300],},
}


############################
### MC based BG estimate ###
############################
for s in samples:
    plotter.addHistogramToStack(s,sigMap[s])

if not blind: plotter.addHistogram('data',sigMap['data'])

for plot in plots:
    kwargs = deepcopy(plots[plot])
    plotname = '{0}/{1}'.format('default',plot)
    savename = '{0}/mc/{1}'.format('default',plot)
    plotter.plot(plotname,savename,**kwargs)

    for alt in alt_plots.get(plot,[]):
        kwargs = deepcopy(plots[plot])
        kwargs.update(alt_plots[plot][alt])
        savename = '{0}/mc/{1}'.format('default',alt)
        plotter.plot(plotname,savename,**kwargs)
    
if blind:
    plotter.addHistogram('data',sigMap['data'])

    for plot in blind_cust:
        kwargs = deepcopy(plots[plot])
        kwargs.update(blind_cust[plot])
        plotname = '{0}/{1}'.format('default',plot)
        savename = '{0}/mc/{1}_blinder'.format('default',plot)
        plotter.plot(plotname,savename,**kwargs)
    
        for alt in alt_plots.get(plot,[]):
            kwargs = deepcopy(plots[plot])
            kwargs.update(alt_plots[plot][alt])
            kwargs.update(blind_cust[plot])
            savename = '{0}/mc/{1}_blinder'.format('default',alt)
            plotter.plot(plotname,savename,**kwargs)
    
