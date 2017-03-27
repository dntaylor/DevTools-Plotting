import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.Plotter import Plotter
from copy import deepcopy
import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

fakeratePlotter = Plotter('WFakeRate')

#########################
### Define categories ###
#########################

sigMap = {
    'WW'  : [
             'WWTo2L2Nu_13TeV-powheg',
             'WWToLNuQQ_13TeV-powheg',
            ],
    'WWsub'  : [
             'WWTo2L2Nu_13TeV-powheg',
            ],
    'W'   : [
             #'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            ],
    'Z'   : [
             #'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             #'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'DY3JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'DY4JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            ],
    'TT'  : [
             'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            ],
    'TTsub'  : [
             'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            ],
    'T'   : [
             'ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
             'ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1',
             #'ST_t-channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin',
             'ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1',
             #'ST_t-channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin',
             'ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
             'ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
            ],
    'QCD' : [
             'QCD_Pt_5to10_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_10to15_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_15to30_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_30to50_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_50to80_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_80to120_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_120to170_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_170to300_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_300to470_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_470to600_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_600to800_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_800to1000_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_1000to1400_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_1400to1800_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_2400to3200_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_3200toInf_TuneCUETP8M1_13TeV_pythia8',
            ],
    'data': [
             'SingleMuon',
             'SingleElectron',
            ],
}

chans = ['me','em','mm','ee']

samples = ['W','T','TT','Z','WW']

for s in samples:
    fakeratePlotter.addHistogramToStack(s,sigMap[s])

fakeratePlotter.addHistogram('data',sigMap['data'])

plots = {
    # z cand
    'zMass'                 : {'xaxis': 'm_{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 10 GeV', 'rebin': 10},
    # m cand
    'wtMt'                  : {'xaxis': 'm_{T}^{tag} (GeV)', 'yaxis': 'Events / 10 GeV', 'rebin': 10},
    'tPt'                   : {'xaxis': 'p_{T}^{tag} (GeV)', 'yaxis': 'Events / 10 GeV', 'rebin': 10},
    'tEta'                  : {'xaxis': '#eta^{tag}', 'yaxis': 'Events', 'rebin': 10},
    # t cand
    'wlMt'                  : {'xaxis': 'm_{T}^{l} (GeV)', 'yaxis': 'Events / 10 GeV', 'rebin': 10},
    'lPt'                   : {'xaxis': 'p_{T}^{l} (GeV)', 'yaxis': 'Events / 10 GeV', 'rebin': 10},
    'lEta'                  : {'xaxis': '#eta^{l}', 'yaxis': 'Events', 'rebin': 10},
    # event
    #'numVertices'           : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 10 GeV', 'rebin': 10},
    # runs
    #'wmMt_Run2016B'                  : {'xaxis': 'm_{T}^{#mu} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    #'wmMt_Run2016C'                  : {'xaxis': 'm_{T}^{#mu} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    #'wmMt_Run2016D'                  : {'xaxis': 'm_{T}^{#mu} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    #'wmMt_Run2016E'                  : {'xaxis': 'm_{T}^{#mu} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    #'wmMt_Run2016F'                  : {'xaxis': 'm_{T}^{#mu} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    #'wmMt_Run2016G'                  : {'xaxis': 'm_{T}^{#mu} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    #'wmMt_Run2016H'                  : {'xaxis': 'm_{T}^{#mu} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
}

for plot in plots:
    for chan in chans:
        for region in  ['loose','medium','tight']:
            plotname = '{0}/{1}/{2}'.format(region,chan,plot)
            savename = '{0}/{1}/{2}'.format(region,chan,plot)
            fakeratePlotter.plot(plotname,savename,**plots[plot])
            #for sel in ['SS','ZVeto','WMt','full']:
            for sel in ['WVeto','WMt','ZVeto','full']:
                plotname = '{0}/{1}/{2}/{3}'.format(region,sel,chan,plot)
                savename = '{0}/{1}/{2}/{3}'.format(region,sel,chan,plot)
                fakeratePlotter.plot(plotname,savename,**plots[plot])



# ratios of tight/loose as func of pt/eta
sigMap['MC'] = []
for sample in ['TTsub','Z','WWsub']:
    sigMap['MC'] += sigMap[sample]
fakeratePlotter.clearHistograms()
fakeratePlotter.addHistogram('MC',sigMap['MC'])
fakeratePlotter.addHistogram('W',sigMap['W'])
fakeratePlotter.addHistogram('data',sigMap['data'],style={'linecolor':ROOT.kBlack,'name':'Corrected'})
fakeratePlotter.addHistogram('data_uncorrected',sigMap['data'],style={'linecolor':ROOT.kRed,'name':'Uncorrected'})

ptbins = [0,10,15,20,25,30,50,100]#,200,1000]
etabins = [-2.5,-2.0,-1.479,-1.0,-0.5,0.,0.5,1.0,1.479,2.0,2.5]

cust = {
    'lPt'     : {'yaxis': 'N_{{{num}}} / N_{{{denom}}}', 'rebin': ptbins, 'xrange': [0,100]},
    'lEta'    : {'yaxis': 'N_{{{num}}} / N_{{{denom}}}', 'rebin': etabins},
}

numDenom = [('medium','loose'),('tight','loose'),('tight','medium')]

chanMap = {
    'e': ['ee','me'],
    'm': ['em','mm'],
}

for plot in ['lPt','lEta']:
    for lep in ['e','m']:
        for num,denom in numDenom:
            kwargs = deepcopy(plots[plot])
            if plot in cust:
                kwargs.update(cust[plot])
                kwargs['yaxis'] = kwargs['yaxis'].format(num=num,denom=denom)
            numname = ['{0}/full/{1}/{2}'.format(num,chan,plot) for chan in chanMap[lep]]
            denomname = ['{0}/full/{1}/{2}'.format(denom,chan,plot) for chan in chanMap[lep]]
            savename = 'ratio/{0}_{1}/{2}/{3}'.format(num,denom,lep,plot)
            subtractMap = {
                'data': ['MC'],
            }
            customOrder = ['data_uncorrected','data','W']
            #customOrder = ['data_uncorrected','data']
            fakeratePlotter.plotRatio(numname,denomname,savename,ymax=1.,customOrder=customOrder,legendpos=34,numcol=2,subtractMap=subtractMap,**kwargs)
            #for etabin in range(3):
            #    if plot=='tEta': continue
            #    numname = '{0}/full/etaBin{1}/{2}/{3}'.format(num,etabin,chan,plot)
            #    denomname = '{0}/full/etaBin{1}/{2}/{3}'.format(denom,etabin,chan,plot)
            #    savename = 'ratio/{0}_{1}/{2}/{3}_etabin{4}'.format(num,denom,chan,plot,etabin)
            #    fakeratePlotter.plotRatio(numname,denomname,savename,ymax=1.,customOrder=customOrder,legendpos=34,numcol=2,subtractMap=subtractMap,**kwargs)

