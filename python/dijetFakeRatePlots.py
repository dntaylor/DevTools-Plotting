import os
import sys
import logging

from DevTools.Plotter.Plotter import Plotter
from copy import deepcopy

import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

dijetFakeRatePlotter = Plotter('DijetFakeRate')

chans = ['e','m']

labelMap = {
    'e': 'e',
    'm': '#mu',
    't': '#tau',
}
chanLabels = [''.join([labelMap[c] for c in chan]) for chan in chans]


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
             #'ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
             #'ST_t-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
             'ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
             'ST_t-channel_top_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
             'ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
             'ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
            ],
    'QCD' : [
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
             'DoubleMuon',
             'DoubleEG',
            ],
}

#samples = ['TT','Z','W','T','WW','QCD']
samples = ['TT','Z','W','T','WW']

allSamplesDict = {'MC':[]}

for s in samples:
    if s=='QCD': continue
    allSamplesDict['MC'] += sigMap[s]

for s in samples:
    dijetFakeRatePlotter.addHistogramToStack(s,sigMap[s])

dijetFakeRatePlotter.addHistogram('data',sigMap['data'])

# plot definitions
plots = {
    'pt'      : {'xaxis': 'p_{T} (GeV)', 'yaxis': 'Events/0.5 GeV', 'rebin': 5, 'rangex': [0,150]},
    'eta'     : {'xaxis': '#eta', 'yaxis': 'Events', 'rebin': 5, 'rangex': [-2.5,2.5]},
    #'met'     : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events/0.2 GeV', 'rebin': 2, 'rangex': [0,200]},
    'wMass'   : {'xaxis': 'm_{T}^{l^{+},MET} (GeV)', 'yaxis': 'Events/0.5 GeV', 'rebin': 5, 'rangex': [0,200]},
}

# signal region
for plot in plots:
    for lepton in ['loose','medium','tight']:
        for chan in chans:
            plotname = '{0}/{1}/{2}'.format(lepton,chan,plot)
            savename = '{0}/{1}/{2}'.format(lepton,chan,plot)
            dijetFakeRatePlotter.plot(plotname,savename,**plots[plot])


# plots of multiple ptcuts on same plot
dijetFakeRatePlotter.clearHistograms()
jetPts = [20,25,30,35,40,45,50]
jetPts = [20,30,40,50]
dRs = [0.5,0.75,1.,1.25,1.5]
jetPtColors = {
    10 : ROOT.TColor.GetColor('#000000'),
    15 : ROOT.TColor.GetColor('#330000'),
    20 : ROOT.TColor.GetColor('#660000'),
    25 : ROOT.TColor.GetColor('#800000'),
    30 : ROOT.TColor.GetColor('#990000'),
    35 : ROOT.TColor.GetColor('#B20000'),
    40 : ROOT.TColor.GetColor('#CC0000'),
    45 : ROOT.TColor.GetColor('#FF0000'),
    50 : ROOT.TColor.GetColor('#FF3333'),
}
for jetPt in jetPts:
    name = 'jetPt{0}'.format(jetPt)
    dijetFakeRatePlotter.addHistogram(name,sigMap['data'],style={'linecolor':jetPtColors[jetPt],'linestyle':3,'name':'Jet p_{{T}} > {0} GeV'.format(jetPt)})
# add the z + tt samples from WZ
dijetFakeRatePlotter.addHistogram('dataDY',sigMap['data'],style={'linecolor':ROOT.kBlue,'linestyle':1,'name':'Data (DY)'},analysis='WZ')
#dijetFakeRatePlotter.addHistogram('dataTT',sigMap['data'],style={'linecolor':ROOT.kGreen,'linestyle':1,'name':'Data (TT)'},analysis='WZ')


ptbins = [0,20,25,30,40,60]
jet_cust = {
    'pt'      : {'yaxis': 'Unit Normalized', 'rebin': 5, 'rangex': [0,60], 'logy': 0},
}

ptVarMap = {
    0 : 'zLeadingLeptonPt',
    1 : 'zSubLeadingLeptonPt',
    2 : 'wLeptonPt',
}

leptonBin = {
    'e' : {
        0 : ['eee','eem'],
        1 : ['eee','eem'],
        2 : ['eee','mme'],
    },
    'm' : {
        0 : ['mme','mmm'],
        1 : ['mme','mmm'],
        2 : ['eem','mmm'],
    },
}

for plot in ['pt']:
    kwargs = deepcopy(plots[plot])
    if plot in jet_cust: kwargs.update(jet_cust[plot])
    for lepton in ['loose']:
        for chan in chans:
            plotname = {}
            for jetPt in jetPts:
                plotname['jetPt{0}'.format(jetPt)] = '{0}/{1}/jetPt{2}/{3}'.format(lepton,chan,jetPt,plot)
            dyvars = ['dy/{1}/{2}'.format(lepton,wzchan,ptVarMap[p]) for wzchan,p in [(c,i) for i in range(3) for c in leptonBin[chan][i]]]
            ttvars = ['tt/{1}/{2}'.format(lepton,wzchan,ptVarMap[p]) for wzchan,p in [(c,i) for i in range(3) for c in leptonBin[chan][i]]]
            plotname['dataDY'] = dyvars
            #plotname['dataTT'] = ttvars
            savename = '{0}/{1}/allJetPts_{2}'.format(lepton,chan,plot)
            #dijetFakeRatePlotter.plotNormalized(plotname,savename,legendpos=34,numcol=2,**kwargs)
            for lepBin in range(3):
                plotname = {}
                for jetPt in jetPts:
                    plotname['jetPt{0}'.format(jetPt)] = '{0}/{1}/jetPt{2}/{3}'.format(lepton,chan,jetPt,plot)
                dyvars = ['dy/{1}/{2}'.format(lepton,wzchan,ptVarMap[p]) for wzchan,p in [(c,lepBin) for c in leptonBin[chan][lepBin]]]
                ttvars = ['tt/{1}/{2}'.format(lepton,wzchan,ptVarMap[p]) for wzchan,p in [(c,lepBin) for c in leptonBin[chan][lepBin]]]
                plotname['dataDY'] = dyvars
                #plotname['dataTT'] = ttvars
                savename = '{0}/{1}/allJetPts_{2}_{3}'.format(lepton,chan,plot,lepBin)
                #dijetFakeRatePlotter.plotNormalized(plotname,savename,legendpos=34,numcol=2,**kwargs)

# ratios of tight/loose as func of pt/eta
dijetFakeRatePlotter.clearHistograms()
dijetFakeRatePlotter.addHistogram('MC',allSamplesDict['MC'])
dijetFakeRatePlotter.addHistogram('data',sigMap['data'],style={'linecolor':ROOT.kBlack,'name':'EWK Corrected'})
dijetFakeRatePlotter.addHistogram('data_uncorrected',sigMap['data'],style={'linecolor':ROOT.kRed,'name':'Uncorrected'})

ptbins = [0,10,15,20,25,30,50,100]#,200,1000]
etabins = [-2.5,-2.0,-1.479,-1.0,-0.5,0.,0.5,1.0,1.479,2.0,2.5]

cust = {
    'pt'     : {'yaxis': 'N_{num}/N_{denom}', 'rebin': ptbins, 'xrange': [0,100]},
    'eta'    : {'yaxis': 'N_{num}/N_{denom}', 'rebin': etabins},
}

jetPtBins = [20,25,30,35,40,45,50]
dRBins = [0.5,0.75,1.,1.25,1.5]

for plot in ['pt','eta']:
    for num,denom in [('medium','loose'),('tight','loose'),('tight','medium')]:
        kwargs = deepcopy(plots[plot])
        if plot in cust:
            update = deepcopy(cust[plot])
            update['yaxis'] = update['yaxis'].format(num=num,denom=denom)
            kwargs.update(update)
        for chan in chans:
            numname = '{0}/{1}/{2}'.format(num,chan,plot)
            denomname = '{0}/{1}/{2}'.format(denom,chan,plot)
            savename = 'ratio/{0}_{1}/{2}/{3}'.format(num,denom,chan,plot)
            subtractMap = {
                'data': ['MC'],
            }
            customOrder = ['data_uncorrected','data']
            dijetFakeRatePlotter.plotRatio(numname,denomname,savename,ymax=1.,customOrder=customOrder,legendpos=34,numcol=2,subtractMap=subtractMap,**kwargs)
            #for etabin in range(5):
            #    if plot=='eta': continue
            #    if chan=='m' and etabin>1: continue
            #    numname = '{0}/{1}/etaBin{2}/{3}'.format(lepton,chan,etabin,plot)
            #    denomname = 'loose/{0}/etaBin{1}/{2}'.format(chan,etabin,plot)
            #    savename = 'ratio/{0}/{1}/{2}_etabin{3}'.format(lepton,chan,plot,etabin)
            #    dijetFakeRatePlotter.plotRatio(numname,denomname,savename,ymax=1.,customOrder=customOrder,legendpos=34,numcol=2,subtractMap=subtractMap,**kwargs)
            #for jetPt in jetPtBins:
            #    numname = '{0}/{1}/jetPt{2}/{3}'.format(num,chan,jetPt,plot)
            #    denomname = '{0}/{1}/jetPt{2}/{3}'.format(denom,chan,jetPt,plot)
            #    savename = 'ratio/{0}_{1}/{2}/{3}_jetPt{4}'.format(num,denom,chan,plot,jetPt)
            #    dijetFakeRatePlotter.plotRatio(numname,denomname,savename,ymax=1.,customOrder=customOrder,legendpos=34,numcol=2,subtractMap=subtractMap,**kwargs)
            for dR in dRBins:
                numname = '{0}/{1}/dR{2}/{3}'.format(num,chan,dR,plot)
                denomname = '{0}/{1}/dR{2}/{3}'.format(denom,chan,dR,plot)
                savename = 'ratio/{0}_{1}/{2}/{3}_dR{4}'.format(num,denom,chan,plot,dR)
                dijetFakeRatePlotter.plotRatio(numname,denomname,savename,ymax=1.,customOrder=customOrder,legendpos=34,numcol=2,subtractMap=subtractMap,**kwargs)



