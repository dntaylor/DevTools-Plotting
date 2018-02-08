import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.Plotter import Plotter
from copy import deepcopy
import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

fakeratePlotter = Plotter('ZTauFakeRate')

#########################
### Define categories ###
#########################

sigMap = {
    'WW'  : [
             'WWTo2L2Nu_13TeV-powheg',
             'WWToLNuQQ_13TeV-powheg',
            ],
    'W'   : [
             'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             #'WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            ],
    'Z'   : [
             'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             #'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY3JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY4JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
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
    'T'   : [
             'ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
             'ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1',
             #'ST_t-channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin',
             'ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1',
             #'ST_t-channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin',
             'ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
             'ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
            ],
    'WZ'  : [
             'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8',
             'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            ],
    'WZsub' : [
             'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8',
            ],
    'ZZ'  : [
             'ZZTo4L_13TeV_powheg_pythia8',
             'ZZTo2L2Q_13TeV_powheg_pythia8',
             'ZZTo2L2Nu_13TeV_powheg_pythia8',
            ],
    'ZZsub'  : [
             'ZZTo4L_13TeV_powheg_pythia8',
            ],
    'TTV' : [
             'tZq_ll_4f_13TeV-amcatnlo-pythia8',
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
             'DoubleMuon',
             'SingleElectron',
             'DoubleEG',
            ],
}

samples = ['W','T','TT','Z','WW','WZ','ZZ','TTV']
subsamples = ['WZ','ZZ','TTV']

for s in samples:
    fakeratePlotter.addHistogramToStack(s,sigMap[s])

fakeratePlotter.addHistogram('data',sigMap['data'])

plots = {
    # z cand
    'zMass'                 : {'xaxis': 'm_{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 1 GeV', 'rebin': 1},
    'zLeadingLeptonPt'      : {'xaxis': 'p_{T}^{Z leading} (GeV)', 'yaxis': 'Events / 10 GeV', 'rebin': 10},
    'zLeadingLeptonEta'     : {'xaxis': '#eta^{Z leading}', 'yaxis': 'Events', 'rebin': 10},
    'zSubLeadingLeptonPt'   : {'xaxis': 'p_{T}^{Z subleading} (GeV)', 'yaxis': 'Events / 10 GeV', 'rebin': 10},
    'zSubLeadingLeptonEta'  : {'xaxis': '#eta^{Z subleading}', 'yaxis': 'Events', 'rebin': 10},
    # t cand
    'wtMt'                  : {'xaxis': 'm_{T}^{#tau} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    'tPt'                   : {'xaxis': 'p_{T}^{#tau} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    'tEta'                  : {'xaxis': '#eta^{#tau}', 'yaxis': 'Events', 'rebin': 5},
    'tDM'                   : {'xaxis': '#tau Decay Mode', 'yaxis': 'Events',},
    # event
    'numVertices'           : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    # runs
    #'wmMt_Run2016B'                  : {'xaxis': 'm_{T}^{#mu} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    #'wmMt_Run2016C'                  : {'xaxis': 'm_{T}^{#mu} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    #'wmMt_Run2016D'                  : {'xaxis': 'm_{T}^{#mu} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    #'wmMt_Run2016E'                  : {'xaxis': 'm_{T}^{#mu} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    #'wmMt_Run2016F'                  : {'xaxis': 'm_{T}^{#mu} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    #'wmMt_Run2016G'                  : {'xaxis': 'm_{T}^{#mu} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    #'wmMt_Run2016H'                  : {'xaxis': 'm_{T}^{#mu} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
}

dms = [0,1,5,6,10]
denomdms = [0,1,5,6,10]
numdms = {
    0 : [0,5],
    1 : [1,6],
    10: [10],
}

for plot in plots:
    for region in  ['loose','medium','tight','newloose']:
        plotname = '{0}/{1}'.format(region,plot)
        savename = '{0}/{1}'.format(region,plot)
        fakeratePlotter.plot(plotname,savename,**plots[plot])
        #for sel in ['WMt']:
        #    plotname = '{0}/{1}/{2}'.format(region,sel,plot)
        #    savename = '{0}/{1}/{2}'.format(region,sel,plot)
        #    fakeratePlotter.plot(plotname,savename,**plots[plot])
        #    for dm in dms:
        #        plotname = '{0}/{1}/dm{2}/{3}'.format(region,sel,dm,plot)
        #        savename = '{0}/{1}/dm{2}/{3}'.format(region,sel,dm,plot)
        #        fakeratePlotter.plot(plotname,savename,**plots[plot])



# ratios of tight/loose as func of pt/eta
sigMap['MC'] = []
for sample in subsamples:
    sigMap['MC'] += sigMap[sample]
fakeratePlotter.clearHistograms()
fakeratePlotter.addHistogram('MC',sigMap['MC'])
fakeratePlotter.addHistogram('Z',sigMap['Z'])
fakeratePlotter.addHistogram('data',sigMap['data'],style={'linecolor':ROOT.kBlack,'name':'Corrected'})
fakeratePlotter.addHistogram('data_uncorrected',sigMap['data'],style={'linecolor':ROOT.kRed,'name':'Uncorrected'})

ptbins = [0,10,15,20,25,30,40,50,60,100]#,200,1000]
etabins = [-2.3,-2.0,-1.479,-1.0,-0.5,0.,0.5,1.0,1.479,2.0,2.3]

cust = {
    'tPt'     : {'yaxis': 'N_{{{num}}} / N_{{{denom}}}', 'rebin': ptbins, 'xrange': [0,100]},
    'tEta'    : {'yaxis': 'N_{{{num}}} / N_{{{denom}}}', 'rebin': etabins},
}

numDenom = [('medium','loose'),('tight','loose'),('tight','medium'),('medium','newloose'),('tight','newloose')]

for plot in ['tPt','tEta']:
    for num,denom in numDenom:
        kwargs = deepcopy(plots[plot])
        if plot in cust:
            kwargs.update(cust[plot])
            kwargs['yaxis'] = kwargs['yaxis'].format(num=num,denom=denom)
        numname = '{0}/all/{1}'.format(num,plot)
        denomname = '{0}/all/{1}'.format(denom,plot)
        savename = 'ratio/{0}_{1}/{2}'.format(num,denom,plot)
        subtractMap = {
            'data': ['MC'],
        }
        customOrder = ['data_uncorrected','data','Z']
        fakeratePlotter.plotRatio(numname,denomname,savename,ymax=1.,customOrder=customOrder,legendpos=34,numcol=2,subtractMap=subtractMap,**kwargs)
        for ndm in numdms:
            kwargs = deepcopy(plots[plot])
            if plot in cust:
                kwargs.update(cust[plot])
                kwargs['yaxis'] = kwargs['yaxis'].format(num=num,denom=denom)
            numname = '{0}/all/dm{1}/{2}'.format(num,ndm,plot)
            denomname = ['{0}/all/dm{1}/{2}'.format(denom,ddm,plot) for ddm in numdms[ndm]]
            savename = 'ratio/{0}_{1}/dm{2}/{4}'.format(num,denom,ndm,ddm,plot)
            subtractMap = {
                'data': ['MC'],
            }
            customOrder = ['data_uncorrected','data','Z']
            fakeratePlotter.plotRatio(numname,denomname,savename,ymax=1.,customOrder=customOrder,legendpos=34,numcol=2,subtractMap=subtractMap,**kwargs)
        #for etabin in range(3):
        #    if plot=='tEta': continue
        #    numname = '{0}/all/etaBin{1}/{2}'.format(num,etabin,plot)
        #    denomname = '{0}/all/etaBin{1}/{2}'.format(denom,etabin,plot)
        #    savename = 'ratio/{0}_{1}/{2}_etabin{3}'.format(num,denom,plot,etabin)
        #    fakeratePlotter.plotRatio(numname,denomname,savename,ymax=1.,customOrder=customOrder,legendpos=34,numcol=2,subtractMap=subtractMap,**kwargs)

