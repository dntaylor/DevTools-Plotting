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

plotter = Plotter('MonoHZZFakeRate',new=True)

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
            'GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo2e2tau_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8',
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
            'WminusH_HToZZTo4L_M125_13TeV_powheg2-minlo-HWJ_JHUGenV7011_pythia8',
            'WplusH_HToZZTo4L_M125_13TeV_powheg2-minlo-HWJ_JHUGenV7011_pythia8',
            'ttH_HToZZ_4LFilter_M125_13TeV_powheg2_JHUGenV7011_pythia8',
            'ZH_HToZZ_4LFilter_M125_13TeV_powheg2-minlo-HZJ_JHUGenV7011_pythia8',
            ],
    'data' : [
            'DoubleMuon',
            'DoubleEG',
            'MuonEG',
            'SingleMuon',
            'SingleElectron',
            ],
}

sigMap['BG'] = []
for s in ['WZ','ZZ','VVV','TTV']:
    sigMap['BG'] += sigMap[s]

samples = ['TT','TTV','WZ','VVV','ZZ','Z']

selections = ['default','looseNoIso','loose','tight']

channels = ['e','m','eee','eem','mme','mmm']
channelMap = {'e': ['eee','mme'], 'm': ['eem','mmmm'],'eee':['eee'],'eem':['eem'],'mme':['mme'],'mmm':['mmm'],}

###############
### Helpers ###
###############
def plotChannels(plotter,plotname,savename,**kwargs):
    kwargs = deepcopy(kwargs)
    plotter.plot(plotname,savename,**kwargs)
    plotsplit = plotname.split('/')
    savesplit = savename.split('/')
    for chan in channels:
        plotnames = ['/'.join(plotsplit[:-1]+[c]+[plotsplit[-1]]) for c in channelMap[chan]]
        savename = '/'.join(savesplit[:-1]+[chan]+[savesplit[-1]])
        plotter.plot(plotnames,savename,**kwargs)

########################
### plot definitions ###
########################
plots = {
    # z cand
    'zMass'                : {'xaxis': 'm_{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 1 GeV', 'rebin': range(81,102,1), 'numcol': 3, 'legendpos':34, 'yscale': 1.5,},
    'zPt'                  : {'xaxis': 'Z p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': range(0,105,5), 'numcol': 3, 'legendpos':34, 'yscale': 1.5,},
    'z1Pt'                 : {'xaxis': 'Z1 p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': range(0,105,5), },
    'z1Eta'                : {'xaxis': 'Z1 #eta (GeV)', 'yaxis': 'Events', 'rebin': [(x-25)*0.1 for x in range(0,52,2)], },
    'z2Pt'                 : {'xaxis': 'Z2 p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': range(0,105,5), },
    'z2Eta'                : {'xaxis': 'Z2 #eta (GeV)', 'yaxis': 'Events', 'rebin': [(x-25)*0.1 for x in range(0,52,2)], },
    # l
    'lPt'                  : {'xaxis': 'p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': range(0,105,5), },
    'lEta'                 : {'xaxis': '#eta (GeV)', 'yaxis': 'Events', 'rebin': [(x-25)*0.1 for x in range(0,52,2)], },
    # event
    'met'                  : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 1 GeV', 'rebin': range(0,30,1), 'numcol': 2, 'legendpos':34},
}


############################
### MC based BG estimate ###
############################
for sel in selections:
    plotter.clearHistograms()


    for s in samples:
        plotter.addHistogramToStack(s,sigMap[s])
    
    plotter.addHistogram('data',sigMap['data'])

    for plot in plots:
        kwargs = deepcopy(plots[plot])
        plotname = '{0}/{1}'.format(sel,plot)
        savename = '{0}/mc/{1}'.format(sel,plot)
        plotChannels(plotter,plotname,savename,**kwargs)
    


plotter.clearHistograms()
plotter.addHistogram('MC',sigMap['BG'])
plotter.addHistogram('Z',sigMap['Z'])
plotter.addHistogram('data',sigMap['data'],style={'linecolor':ROOT.kBlack,'name':'Data'})
plotter.addHistogram('data_uncorrected',sigMap['data'],style={'linecolor':ROOT.kRed,'name':'Uncorrected'})

denom = 'looseNoIso'
num = 'tight'

ptbins = [5,7,10,15,20,30,50,100]

cust = {
    'lPt' : {'rebin': ptbins,},
}

for plot in cust:
    kwargs = deepcopy(plots[plot])
    kwargs.update(cust[plot])
    kwargs['yaxis'] = 'Ratio'
    for chan in channels:
        numname = ['{}/{}/{}'.format(num,c,plot) for c in channelMap[chan]]
        denomname = ['{}/{}/{}'.format(denom,c,plot) for c in channelMap[chan]]
        savename = 'ratio/{}/{}'.format(chan,plot)
        subtractMap = {'data': ['MC']}
        customOrder = ['data_uncorrected','Z','data']
        plotter.plotRatio(numname,denomname,savename,ymax=1.,customOrder=customOrder,subtractMap=subtractMap,**kwargs)
