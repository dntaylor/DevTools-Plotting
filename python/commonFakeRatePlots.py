import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.Plotter import Plotter
from copy import deepcopy
import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


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
    'dataDijetFakeRate': [
             'DoubleMuon',
             'DoubleEG',
            ],
    'dataWFakeRate': [
             'SingleMuon',
             'SingleElectron',
            ],
    'dataZFakeRate': [
             'SingleMuon',
             'DoubleMuon',
             'SingleElectron',
             'DoubleEG',
            ],
}

analyses = ['DijetFakeRate','WFakeRate','ZFakeRate']

fakeratePlotters = {}
for analysis in analyses:
    fakeratePlotters[analysis] = Plotter(analysis)

chanMap = {
    'DijetFakeRate': {
        'e': 'e',
        'm': 'm',
    },
    'WFakeRate': {
        'e': 'me',
        'm': 'em',
    },
    'ZFakeRate': {
        'e': ['mme','eee'],
        'm': ['mmm','eem'],
    },
}

sampleMap = {
    'DijetFakeRate': ['W','T','TT','Z','WW'],
    'WFakeRate'    : ['W','T','TT','Z','WW'],
    'ZFakeRate'    : ['W','T','TT','Z','WW','WZ','ZZ','TTV'],
}

subMap = {
    'DijetFakeRate': ['W','T','TT','Z','WW'],
    'WFakeRate'    : ['TT','Z','WW'],
    'ZFakeRate'    : ['WZsub','ZZsub'],
}


plots = {
    # l cand
    'lPt'                   : {'xaxis': 'p_{T}^{l} (GeV)', 'yaxis': 'Events / 10 GeV', 'rebin': 10},
    'lEta'                  : {'xaxis': '#eta^{l}', 'yaxis': 'Events', 'rebin': 10},
}


# ratios of tight/loose as func of pt/eta
for analysis in analyses:
    sigMap['MC'+analysis] = []
    for sample in subMap[analysis]:
        sigMap['MC'+analysis] += sigMap[sample]
    fakeratePlotter.addHistogram('MC',sigMap['MC'+sample])
    fakeratePlotter.addHistogram('data',sigMap['data'+sample],style={'linecolor':ROOT.kBlack,'name':'Corrected'})
    fakeratePlotter.addHistogram('data_uncorrected',sigMap['data'+sample],style={'linecolor':ROOT.kRed,'name':'Uncorrected'})

ptbins = [0,10,15,20,25,30,50,100]#,200,1000]
etabins = {
    'e': [-2.5,-2.1,-1.479,-1.0,-0.5,0.,0.5,1.0,1.479,2.1,2.5],
    'm': [-2.4,-2.0,-1.0,-0.5,0.,0.5,1.0,2.0,2.4],
}

cust = {
    'lPt'     : {'yaxis': 'N_{{{num}}} / N_{{{denom}}}', 'rebin': ptbins, 'xrange': [0,100]},
    'lEta'    : {'yaxis': 'N_{{{num}}} / N_{{{denom}}}',},
}

numDenom = [('medium','loose'),('tight','loose'),('tight','medium')]


for plot in ['lPt','lEta']:
    for lep in ['e', 'm']:
        for num,denom in numDenom:
            hists = {}
            kwargs = deepcopy(plots[plot])
            if plot in cust:
                kwargs.update(cust[plot])
                if plot=='lEta': kwargs['rebin'] = etabins[lep]
                kwargs['yaxis'] = kwargs['yaxis'].format(num=num,denom=denom)
            customOrder = ['data']
            subtractMap = {
                'data': ['MC'],
            }
            for analysis in analyses:
                if analysis=='ZFakeRate':
                    numname = ['{0}/fullSel/{1}/{2}'.format(num,chan,plot) for chan in chanMap[analysis][lep]]
                    denomname = ['{0}/fullSel/{1}/{2}'.format(denom,chan,plot) for chan in chanMap[analysis][lep]]
                elif analysis == 'WFakeRate':
                    numname = '{0}/full/{1}/{2}'.format(num,chanMap[analysis][lep],plot)
                    denomname = '{0}/full/{1}/{2}'.format(denom,chanMap[analysis][lep],plot)
                else:
                    plotName = 'pt' if plot=='lPt' else 'eta'
                    numname = '{0}/{1}/{2}'.format(num,chanMap[analysis][lep],plotName)
                    denomname = '{0}/{1}/{2}'.format(denom,chanMap[analysis][lep],plotName)
                savename = 'ratio/{0}_{1}/{2}/{3}'.format(num,denom,lep,plot)
                hists[analysis] = fakeratePlotter.plotRatio(numname,denomname,savename,ymax=1.,customOrder=customOrder,legendpos=34,numcol=2,subtractMap=subtractMap,getHists=True,**kwargs)
