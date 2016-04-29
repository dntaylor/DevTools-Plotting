import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.Plotter import Plotter
from copy import deepcopy
import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

fakeratePlotter = Plotter('WTauFakeRate')

#########################
### Define categories ###
#########################

sigMap = {
    'WZ'  : [
             'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8',
             'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
             'WZTo1L3Nu_13TeV_amcatnloFXFX_madspin_pythia8',
             'WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            ],
    'ZZ'  : [
             'ZZTo4L_13TeV_powheg_pythia8',
             'GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8',
             'ZZTo2L2Nu_13TeV_powheg_pythia8',
             'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            ],
    'VVV' : [
             'WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
             'WWG_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
            ],
    'VH'  : [
             'WH_HToBB_WToLNu_M125_13TeV_amcatnloFXFX_madspin_pythia8',
             'ZH_HToBB_ZToLL_M125_13TeV_amcatnloFXFX_madspin_pythia8',
             'ZH_HToBB_ZToNuNu_M125_13TeV_amcatnloFXFX_madspin_pythia8',
             'ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8',
             'ZH_HToGG_ZToAll_M125_13TeV_powheg_pythia8',
             'ZH_HToZG_ZToAll_M-125_13TeV_powheg_pythia8',
             'ZH_HToZZ_4LFilter_M125_13TeV_powheg2-minlo-HZJ_JHUgenV6_pythia8',
            ],
    'TTV' : [
             'ttWJets_13TeV_madgraphMLM',
             'ttZJets_13TeV_madgraphMLM',
             'ttH_M125_13TeV_powheg_pythia8',
             'tZq_ll_4f_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
             'tZq_nunu_4f_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
            ],
    'WW'  : [
             'WWTo2L2Nu_13TeV-powheg',
             'WWToLNuQQ_13TeV-powheg',
            ],
    'W'   : [
             'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
            ],
    'Z'   : [
             'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
            ],
    'TT'  : [
             'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            ],
    'T'   : [
             'ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
             #'ST_t-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
             'ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
             'ST_t-channel_top_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
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
             #'DoubleMuon',
             #'DoubleEG',
             #'MuonEG',
             'SingleMuon',
             #'SingleElectron',
             #'Tau',
            ],
    'HppHmm200GeV' : ['HPlusPlusHMinusMinusHTo4L_M-200_13TeV-pythia8'],
    'HppHmm300GeV' : ['HPlusPlusHMinusMinusHTo4L_M-300_13TeV-pythia8'],
    'HppHmm400GeV' : ['HPlusPlusHMinusMinusHTo4L_M-400_13TeV-pythia8'],
    'HppHmm500GeV' : ['HPlusPlusHMinusMinusHTo4L_M-500_13TeV-pythia8'],
    'HppHmm600GeV' : ['HPlusPlusHMinusMinusHTo4L_M-600_13TeV-pythia8'],
    'HppHmm700GeV' : ['HPlusPlusHMinusMinusHTo4L_M-700_13TeV-pythia8'],
    'HppHmm800GeV' : ['HPlusPlusHMinusMinusHTo4L_M-800_13TeV-pythia8'],
    'HppHmm900GeV' : ['HPlusPlusHMinusMinusHTo4L_M-900_13TeV-pythia8'],
    'HppHmm1000GeV': ['HPlusPlusHMinusMinusHTo4L_M-1000_13TeV-pythia8'],
}

samples = ['W','T','TT','TTV','Z','WW','VH','WZ','VVV','ZZ']

for s in samples:
    fakeratePlotter.addHistogramToStack(s,sigMap[s])

fakeratePlotter.addHistogram('data',sigMap['data'])

plots = {
    # z cand
    'zMass'                 : {'xaxis': 'm_{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    # m cand
    'wmMt'                  : {'xaxis': 'm_{T}^{#mu} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    'mPt'                   : {'xaxis': 'p_{T}^{#mu} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    'mEta'                  : {'xaxis': '#eta^{#mu}', 'yaxis': 'Events', 'rebin': 5},
    # t cand
    'wtMt'                  : {'xaxis': 'm_{T}^{#tau} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    'tPt'                   : {'xaxis': 'p_{T}^{#tau} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    'tEta'                  : {'xaxis': '#eta^{#tau}', 'yaxis': 'Events', 'rebin': 5},
    # event
    'numVertices'           : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
}

for plot in plots:
    for region in  ['loose','medium','tight']:
        plotname = '{0}/{1}'.format(region,plot)
        savename = '{0}/{1}'.format(region,plot)
        fakeratePlotter.plot(plotname,savename,**plots[plot])
        for sel in ['SS','ZVeto','WMt','all']:
            plotname = '{0}/{1}/{2}'.format(region,sel,plot)
            savename = '{0}/{1}/{2}'.format(region,sel,plot)
            fakeratePlotter.plot(plotname,savename,**plots[plot])



# ratios of tight/loose as func of pt/eta
sigMap['MC'] = []
for sample in samples:
    if sample!='W': sigMap['MC'] += sigMap[sample]
fakeratePlotter.clearHistograms()
fakeratePlotter.addHistogram('MC',sigMap['MC'])
fakeratePlotter.addHistogram('W',sigMap['W'])
fakeratePlotter.addHistogram('data',sigMap['data'],style={'linecolor':ROOT.kBlack,'name':'Corrected'})
fakeratePlotter.addHistogram('data_uncorrected',sigMap['data'],style={'linecolor':ROOT.kRed,'name':'Uncorrected'})

ptbins = [0,10,15,20,25,30,40,50,60,100]#,200,1000]
etabins = [-2.3,-2.0,-1.479,-1.0,-0.5,0.,0.5,1.0,1.479,2.0,2.3]

cust = {
    'tPt'     : {'yaxis': 'N_{{{num}}} / N_{{{denom}}}', 'rebin': ptbins, 'xrange': [0,100]},
    'tEta'    : {'yaxis': 'N_{{{num}}} / N_{{{denom}}}', 'rebin': etabins},
}

numDenom = [('medium','loose'),('tight','loose'),('tight','medium')]

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
        customOrder = ['data_uncorrected','data','W']
        fakeratePlotter.plotRatio(numname,denomname,savename,ymax=1.,customOrder=customOrder,legendpos=34,numcol=2,subtractMap=subtractMap,**kwargs)
        for etabin in range(3):
            if plot=='tEta': continue
            numname = '{0}/all/etaBin{1}/{2}'.format(num,etabin,plot)
            denomname = '{0}/all/etaBin{1}/{2}'.format(denom,etabin,plot)
            savename = 'ratio/{0}_{1}/{2}_etabin{3}'.format(num,denom,plot,etabin)
            fakeratePlotter.plotRatio(numname,denomname,savename,ymax=1.,customOrder=customOrder,legendpos=34,numcol=2,subtractMap=subtractMap,**kwargs)

