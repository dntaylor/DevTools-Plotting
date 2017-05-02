import os
import sys
import logging

from DevTools.Plotter.Plotter import Plotter
from copy import deepcopy

import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

chargePlotter = Plotter('Charge')

chans = ['ee','mm']

labelMap = {
    'e': 'e',
    'm': '#mu',
    't': '#tau',
}
chanLabels = [''.join([labelMap[c] for c in chan]) for chan in chans]
#chanLabels[-1] = '#tau_{#mu}#tau_{h}'

sigMap = {
    'WW'  : [
             'WWTo2L2Nu_13TeV-powheg',
             #'WWToLNuQQ_13TeV-powheg',
            ],
    'Z'   : [
             'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             #'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
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

#samples = ['WW','TT','Z']
samples = ['TT','Z']

for s in samples:
    chargePlotter.addHistogramToStack(s,sigMap[s])

chargePlotter.addHistogram('data',sigMap['data'])

# plot definitions
plots = {
    # z cand
    'zMass'                 : {'xaxis': 'm_{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 1 GeV', 'rebin': range(81,101,1)},
    'zLeadingLeptonPt'      : {'xaxis': 'p_{T}^{Z_{lead}} (GeV)', 'yaxis': 'Events / 1 GeV', 'rebin': range(0,150,1)},
    'zLeadingLeptonEta'     : {'xaxis': '|#eta^{Z_{lead}}|', 'yaxis': 'Events',},
    'zSubLeadingLeptonPt'   : {'xaxis': 'p_{T}^{Z_{sublead}} (GeV)', 'yaxis': 'Events / 1 GeV', 'rebin': range(0,150,1)},
    'zSubLeadingLeptonEta'  : {'xaxis': '|#eta^{Z_{sublead}}|', 'yaxis': 'Events',},
}

# signal region
for plot in plots:
    for sign in ['SS','OS','SS1','SS2','SSEE','SSBB','OSEE','OSBB']:
        for chan in chans:
            plotname = '{0}/{1}/{2}'.format(sign,chan,plot)
            savename = '{0}/{1}/{2}'.format(sign,chan,plot)
            chargePlotter.plot(plotname,savename,**plots[plot])

# sum gen matched
for plot in plots:
    for chan in chans:
        plotnames = {}
        for sample in samples:
            plotnames[sample] = ['{0}/{1}/{2}'.format('SS1',chan,plot), '{0}/{1}/{2}'.format('SS2',chan,plot)]
        plotnames['data'] = ['{0}/{1}/{2}'.format('SS',chan,plot)]
        savename = '{0}/{1}/{2}'.format('SS12',chan,plot)
        chargePlotter.plot(plotnames,savename,**plots[plot])


# ratios of SS/OS as func of pt/eta
chargePlotter.clearHistograms()

allSamplesDict = {'MC':[]}

for s in samples:
    allSamplesDict['MC'] += sigMap[s]

chargePlotter.addHistogram('MC',allSamplesDict['MC'],style={'linecolor': ROOT.kRed})
chargePlotter.addHistogram('data',sigMap['data'],style={'linecolor':ROOT.kBlack})

ptbins = [10,20,30,40,50,60,80,100,200,1000]
etabins = [-2.5,-2.0,-1.479,-1.0,-0.5,0.,0.5,1.0,1.479,2.0,2.5]

ratio_cust = {
    'zLeadingLeptonPt'     : {'yaxis': 'N_{SS}/N', 'rebin': ptbins},
    'zLeadingLeptonEta'    : {'yaxis': 'N_{SS}/N', 'rebin': etabins},
    'zSubLeadingLeptonPt'  : {'yaxis': 'N_{SS}/N', 'rebin': ptbins},
    'zSubLeadingLeptonEta' : {'yaxis': 'N_{SS}/N', 'rebin': etabins},
}

for plot in ['Pt','Eta']:
    #for lepton in ['zLeadingLepton','zSubLeadingLepton']:
    for lepton in ['zLeadingLepton']:
        kwargs = deepcopy(plots[lepton+plot])
        kwargsOS = deepcopy(plots[lepton+plot])
        if lepton+plot in ratio_cust: kwargs.update(ratio_cust[lepton+plot])
        if lepton+plot in ratio_cust: kwargsOS.update(ratio_cust[lepton+plot])
        kwargsOS['yaxis'] = 'N_{OS}/N'
        for chan in chans:
            for region in ['','EE','BB']:
                subdirs = '{0}/{1}{2}'.format(chan,lepton,plot)
                numname = 'SS{0}/{1}'.format(region,subdirs)
                denomname = ['OS{0}/{1}'.format(region,subdirs),  'SS{0}/{1}'.format(region,subdirs)]
                savename = 'ratio/{0}/{1}{2}'.format(chan,lepton,plot)
                if region: savename += '_'+region
                chargePlotter.plotRatio(numname,denomname,savename,ymax=0.07,plotratio=True,ratiomin=0.9,ratiomax=1.2,**kwargs)
                ## sum gen matched
                #numname = {}
                #denomname = {}
                #numname['MC'] = ['{0}/{1}/{2}{3}'.format('SS1',chan,lepton,plot), '{0}/{1}/{2}{3}'.format('SS2',chan,lepton,plot)]
                #denomname['MC'] = ['{0}/{1}/{2}{3}'.format('SS1',chan,lepton,plot), '{0}/{1}/{2}{3}'.format('SS2',chan,lepton,plot), '{0}/{1}/{2}{3}'.format('OS',chan,lepton,plot)]
                #numname['data'] = ['{0}/{1}/{2}{3}'.format('SS',chan,lepton,plot)]
                #denomname['data'] = ['{0}/{1}/{2}{3}'.format('SS',chan,lepton,plot), '{0}/{1}/{2}{3}'.format('OS',chan,lepton,plot)]
                #savename = 'ratio/{0}/{1}{2}_genMatched'.format(chan,lepton,plot)
                #chargePlotter.plotRatio(numname,denomname,savename,ymax=0.07,plotratio=True,ratiomin=0.9,ratiomax=1.2,**kwargs)
                # OS
                numname = 'OS{0}/{1}'.format(region,subdirs)
                denomname = ['OS{0}/{1}'.format(region,subdirs),  'SS{0}/{1}'.format(region,subdirs)]
                savename = 'ratio/{0}/{1}{2}_OS'.format(chan,lepton,plot)
                if region: savename += '_'+region
                chargePlotter.plotRatio(numname,denomname,savename,ymin=0.8,ymax=1.2,plotratio=True,ratiomin=0.95,ratiomax=1.05,**kwargsOS)
                ## sum gen matched
                #numname = {}
                #denomname = {}
                #numname['MC'] = ['{0}/{1}/{2}{3}'.format('OS',chan,lepton,plot),]
                #denomname['MC'] = ['{0}/{1}/{2}{3}'.format('SS1',chan,lepton,plot), '{0}/{1}/{2}{3}'.format('SS2',chan,lepton,plot), '{0}/{1}/{2}{3}'.format('OS',chan,lepton,plot)]
                #numname['data'] = ['{0}/{1}/{2}{3}'.format('OS',chan,lepton,plot)]
                #denomname['data'] = ['{0}/{1}/{2}{3}'.format('SS',chan,lepton,plot), '{0}/{1}/{2}{3}'.format('OS',chan,lepton,plot)]
                #savename = 'ratio/{0}/{1}{2}_genMatched_OS'.format(chan,lepton,plot)
                #chargePlotter.plotRatio(numname,denomname,savename,ymin=0.8,ymax=1.2,plotratio=True,ratiomin=0.95,ratiomax=1.05,**kwargsOS)


