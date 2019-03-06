import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.Plotter import Plotter
from DevTools.Utilities.utilities import ZMASS, getCMSSWVersion
from DevTools.Plotter.haaUtils import *
from copy import deepcopy
import ROOT
ROOT.gROOT.SetBatch(ROOT.kTRUE)

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

version = getCMSSWVersion()

blind = False
doSignals = True
doSignalAs = False
doSignalHs = False
doSignalHAs = False
doMC = True
do2D = True
doDM = False
doAllSignals = False
doDatadriven = True
doLowmass = True
doChi2 = False
doHighmass = False
doDESY = False
doSameSign = False
doMatrix = False
doNormalizations = False
doSignficance = False
doGenMatch = False
#newloose = [-1,-0.2,-0.1,0.0,0.1,0.2,0.3,0.4]
#newloose = [-1,-0.2,0.0,0.2,0.4]
newloose = []

toPlot = []

plotter = Plotter('MuMuTauTau',new=True)


#########################
### Define categories ###
#########################

sigMap = getSampleMap()

#samples = ['QCD','W','Z','TT','WW','WZ','ZZ']
#samples = ['JPsi','Upsilon','W','Z','TT','WW','WZ','ZZ']
#samples = ['JPsi','W','Z','TT','WW','WZ','ZZ']
samples = ['W','Z','TT','WW','WZ','ZZ']
#samples = ['TT','W','Z']

sigMap['BG'] = []
for s in samples:
    sigMap['BG'] += sigMap[s]

signals = ['HToAAH125A15']
allsignals = []

signame = 'HToAAH{h}A{a}'
ggsigname = 'ggHToAAH{h}A{a}'
vbfsigname = 'vbfHToAAH{h}A{a}'

hmasses = [125,300,750]
amasses = ['3p6',4,5,6,7,8,9,10,11,12,13,14,15,17,19,21]
#amasses = [5,9,13,17,21]
amasses = [5,9,15]

vbfmasses = [5,9,15]

for h in hmasses:
    for a in amasses:
        allsignals += [signame.format(h=h,a=a)]


hColors = {
    125: ROOT.TColor.GetColor('#000000'),
    300: ROOT.TColor.GetColor('#B20000'),
    750: ROOT.TColor.GetColor('#FF6666'),
}

aColors = {
    5 : ROOT.TColor.GetColor('#000000'),
    7 : ROOT.TColor.GetColor('#330000'),
    9 : ROOT.TColor.GetColor('#660000'),
    11: ROOT.TColor.GetColor('#800000'),
    13: ROOT.TColor.GetColor('#B20000'),
    15: ROOT.TColor.GetColor('#FF0000'),
    17: ROOT.TColor.GetColor('#FF6666'),
    19: ROOT.TColor.GetColor('#FF9999'),
    21: ROOT.TColor.GetColor('#FFCCCC'),
}
aColors = {
    5 : ROOT.TColor.GetColor('#000000'),
    7 : ROOT.TColor.GetColor('#330000'),
    9 : ROOT.TColor.GetColor('#660000'),
    13: ROOT.TColor.GetColor('#800000'),
    15: ROOT.TColor.GetColor('#800000'),
    17: ROOT.TColor.GetColor('#B20000'),
    21: ROOT.TColor.GetColor('#FF6666'),
}


basesels = ['default','regionA','regionB','regionC','regionD']
sels = list(basesels)
subsels = []
desysels = []
signalsels = list(basesels)
signalsubsels = []
tags = ['']
if doDM: 
    subsels += ['dm0','dm1','dm10']
    signalsubsels += ['dm0','dm1','dm10']
    tags += ['dm0','dm1','dm10']
if doLowmass:
    subsels += ['lowmass']
    tags += ['lowmass']
    if doDM: 
        subsels += ['lowmassdm0','lowmassdm1','lowmassdm10']
        tags += ['lowmassdm0','lowmassdm1','lowmassdm10']
if doHighmass: 
    subsels += ['highmass']
    tags += ['highmass']
    if doDM: 
        subsels += ['highmassdm0','highmassdm1','highmassdm10']
        tags += ['highmassdm0','highmassdm1','highmassdm10']
if doSameSign: 
    subsels += ['samesign']
    signalsubsels += ['samesign']
    tags += ['samesign']
    if doDM: 
        subsels += ['samesigndm0','samesigndm1','samesigndm10']
        signalsubsels += ['samesigndm0','samesigndm1','samesigndm10']
        tags += ['samesigndm0','samesigndm1','samesigndm10']
if doChi2: 
    subsels += ['chi2_125']
    signalsubsels += ['chi2_125']
    tags += ['chi2_125']
    if doDM: 
        subsels       += ['chi2_125dm0','chi2_125dm1','chi2_125dm10']
        signalsubsels += ['chi2_125dm0','chi2_125dm1','chi2_125dm10']
        tags          += ['chi2_125dm0','chi2_125dm1','chi2_125dm10']
if doGenMatch:
    signalsubsels += ['genMatch']
    if doDM:
        signalsubsels += ['genMatchdm0','genMatchdm1','genMatchdm10']

for sel in basesels:
    for subsel in subsels:
        sels += ['{}/{}'.format(subsel,sel)]
    for subsel in signalsubsels:
        signalsels += ['{}/{}'.format(subsel,sel)]
    desysels += ['desy/{}'.format(sel)]

########################
### plot definitions ###
########################
plots = {
    # h
    'kinFitChi2'            : {'xaxis': 'Kin. Fit #chi^{2}', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': [x*2 for x in range(50)], 'logy': False, 'overflow': True},
    'hMass'                 : {'xaxis': 'm^{#mu#mu#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 20 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,1000,20), 'logy': False, 'overflow': True},
    'hMassKinFit'           : {'xaxis': 'm^{#mu#mu#tau_{#mu}#tau_{h}} Kin. Fit (GeV)', 'yaxis': 'Events / 20 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,1000,20), 'logy': False, 'overflow': True},
    #'hMt'                   : {'xaxis': 'm_{T}^{#mu#mu#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,650,10), 'logy': False, 'overflow': True},
    #'hMcat'                 : {'xaxis': 'm_{CA}^{#mu#mu#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,650,10), 'logy': True, 'overflow': True},
    'hDeltaMass'            : {'xaxis': 'm^{#mu#mu}-m^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(-250,250,10), 'logy': True, 'overflow': True},
    'hDeltaMt'              : {'xaxis': 'm^{#mu#mu}-m_{T}^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(-250,250,10), 'logy': True, 'overflow': True},
    #'mmmMass'               : {'xaxis': 'm^{#mu#mu#tau_{#mu}} (GeV)', 'yaxis': 'Events / 1 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,100,1), 'logy': False, 'overflow': True},
    #'mmtMass'               : {'xaxis': 'm^{#mu#mu#tau_{h}} (GeV)', 'yaxis': 'Events / 1 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,100,1), 'logy': False, 'overflow': True},
    # amm
    'ammMass'               : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'Events / 0.5 GeV', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.5, range(8,60,1)), 'logy': False, 'overflow': True},
    'ammDeltaR'             : {'xaxis': '#Delta R(#mu#mu)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.05, range(0,30,1)), 'logy': False, 'overflow': True},
    'ammDeltaPhi'           : {'xaxis': '#Delta #phi(#mu#mu)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': 5, 'logy': False, 'overflow': False},
    'am1Pt'                 : {'xaxis': 'a_{1}^{#mu#mu} #mu_{1} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(25,150,5), 'logy': False, 'overflow': True},
    'am1Eta'                : {'xaxis': 'a_{1}^{#mu#mu} #mu_{1} #eta', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': 5, 'logy': False, 'overflow': False},
    #'am1GenPtRatio'         : {'xaxis': '#mu_{1} p_{T}^{gen}/p_{T}^{reco}', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(50,150,1)), 'logy': False, 'overflow': True},
    'am2Pt'                 : {'xaxis': 'a_{1}^{#mu#mu} #mu_{2} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,150,5), 'logy': False, 'overflow': True},
    'am2Eta'                : {'xaxis': 'a_{1}^{#mu#mu} #mu_{2} #eta', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': 5, 'logy': False, 'overflow': False},
    #'am2GenPtRatio'         : {'xaxis': '#mu_{2} p_{T}^{gen}/p_{T}^{reco}', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(50,150,1)), 'logy': False, 'overflow': True},
    'am1Iso'                : {'xaxis': 'a_{1}^{#mu#mu} #mu_{1} Rel. Iso.', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'logy': False, 'overflow': True},
    'am2Iso'                : {'xaxis': 'a_{1}^{#mu#mu} #mu_{2} Rel. Iso.', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'logy': False, 'overflow': True},
    #'am1PassMedium'         : {'xaxis': 'a_{1}^{#mu#mu} #mu_{1} Pass Medium', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'logy': False, 'overflow': False},
    #'am2PassMedium'         : {'xaxis': 'a_{1}^{#mu#mu} #mu_{2} Pass Medium', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'logy': False, 'overflow': False},
    # att
    'attMass'               : {'xaxis': 'm^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 1 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,30,1), 'logy': False, 'overflow': True},
    'attMassKinFit'         : {'xaxis': 'm^{#tau_{#mu}#tau_{h}} Kin. Fit (GeV)', 'yaxis': 'Events / 1 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,30,1), 'logy': False, 'overflow': True},
    #'attMt'                 : {'xaxis': 'm_{T}^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 2 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,120,2), 'logy': False, 'overflow': True},
    #'attMcat'               : {'xaxis': 'm_{CA}^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 2 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,120,2), 'logy': True, 'overflow': True},
    'attDeltaR'             : {'xaxis': '#Delta R(#tau_{#mu}#tau_{h})', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.05, range(0,30,1)), 'logy': False, 'overflow': True},
    'attDeltaPhi'           : {'xaxis': '#Delta #phi(#tau_{#mu}#tau_{h})', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': 5, 'logy': False, 'overflow': False},
    'atmPt'                 : {'xaxis': '#tau_{#mu} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,150,5), 'logy': False, 'overflow': True},
    'atmEta'                : {'xaxis': '#tau_{#mu} #eta', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': 5, 'logy': False, 'overflow': False},
    #'atmDxy'                : {'xaxis': 'a_{1}^{#tau_{#mu}#tau_{h}} #tau_{#mu} d_{xy} (cm)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': 1, 'logy': True},
    #'atmDz'                 : {'xaxis': 'a_{1}^{#tau_{#mu}#tau_{h}} #tau_{#mu} d_{z} (cm)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': 1, 'logy': True},
    #'atmGenPtRatio'         : {'xaxis': '#tau_{#mu} p_{T}^{gen}/p_{T}^{reco}', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(50,150,1)), 'logy': False, 'overflow': True},
    'athPt'                 : {'xaxis': '#tau_{h} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(10,150,5), 'logy': False, 'overflow': True},
    'athEta'                : {'xaxis': '#tau_{h} #eta', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': 5, 'logy': False, 'overflow': False},
    #'athDxy'                : {'xaxis': 'a_{1}^{#tau_{#mu}#tau_{h}} #tau_{h} d_{xy} (cm)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': 1, 'logy': True},
    #'athDz'                 : {'xaxis': 'a_{1}^{#tau_{#mu}#tau_{h}} #tau_{h} d_{z} (cm)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': 1, 'logy': True},
    'athDM'                 : {'xaxis': '#tau_{h} Decay Mode', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'logy': False, 'yscale': 1.5,},
    #'athGenPtRatio'         : {'xaxis': '#tau_{h} p_{T}^{reco}/p_{T}^{gen}', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(0,250,5)), 'logy': False, 'overflow': True},
    #'athGenPtRatioDM0'      : {'xaxis': '#tau_{h} p_{T}^{reco}/p_{T}^{gen} (DM 0)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(0,250,5)), 'logy': False, 'overflow': True},
    #'athGenPtRatioDM1'      : {'xaxis': '#tau_{h} p_{T}^{reco}/p_{T}^{gen} (DM 1)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(0,250,5)), 'logy': False, 'overflow': True},
    #'athGenPtRatioDM10'     : {'xaxis': '#tau_{h} p_{T}^{reco}/p_{T}^{gen} (DM 10)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(0,250,5)), 'logy': False, 'overflow': True},
    'athJetCSV'             : {'xaxis': '#tau_{h} CSVv2', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': 10, 'logy': True, 'overflow': True},
    'athIso'                : {'xaxis': '#tau_{h} MVA Iso.', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'logy': False, 'overflow': True},
    #'athIsoCB'              : {'xaxis': '#tau_{h} CB Iso.', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'logy': False, 'overflow': True},
    'atmIso'                : {'xaxis': '#tau_{#mu} Rel. Iso.', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'logy': False, 'overflow': True},
    # event
    'genChannel'            : {'xaxis': 'Gen channel', 'yaxis': 'Events',},
    'numVertices'           : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': range(0,320,20), 'numcol': 2, 'logy': False, 'overflow': True},
    #'nBJetsT'               : {'xaxis': 'Number of b-tagged jets (p_{T} > 20 GeV)', 'yaxis': 'Events', 'rebin': [-0.5,0.5,1.5,2.5], 'overflow': True, 'binlabels': ['0','1','2','#geq3'], 'logy': True,},
    #'nBJetsM'               : {'xaxis': 'Number of b-tagged jets (p_{T} > 20 GeV)', 'yaxis': 'Events', 'rebin': [-0.5,0.5,1.5,2.5], 'overflow': True, 'binlabels': ['0','1','2','#geq3'], 'logy': True,},
    #'nBJetsL'               : {'xaxis': 'Number of b-tagged jets (p_{T} > 20 GeV)', 'yaxis': 'Events', 'rebin': [-0.5,0.5,1.5,2.5], 'overflow': True, 'binlabels': ['0','1','2','#geq3'], 'logy': True,},
    'am1atmDeltaR'          : {'xaxis': '#Delta R(#mu_{1}#tau_{#mu})', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.1, range(0,60,2)), 'logy': False, 'overflow': True},
    'am1athDeltaR'          : {'xaxis': '#Delta R(#mu_{1}#tau_{h})', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.1, range(0,60,2)), 'logy': False, 'overflow': True},
    'am2atmDeltaR'          : {'xaxis': '#Delta R(#mu_{2}#tau_{#mu})', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.1, range(0,60,2)), 'logy': False, 'overflow': True},
    'am2athDeltaR'          : {'xaxis': '#Delta R(#mu_{2}#tau_{h})', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.1, range(0,60,2)), 'logy': False, 'overflow': True},
}

plotsSignal = {
    'hMass'      : {'yaxis': 'Events / 10 GeV', 'rebin': range(0,1000,10),},
    'hMassKinFit': {'yaxis': 'Events / 10 GeV', 'rebin': range(0,1000,10),},
    'ammMass'    : {'yaxis': 'Events / 50 MeV', 'rebin': map(lambda x: x*0.05, range(0,600,1)),},
    'attMass'    : {'yaxis': 'Events / 500 MeV', 'rebin': map(lambda x: x*0.1, range(0,200,5)),},
    'ammDeltaR'  : {'rebin':  map(lambda x: x*0.015, range(0,100,1)),},
    'attDeltaR'  : {'rebin':  map(lambda x: x*0.015, range(0,100,1)),},
}

plots2D = {
    'ammMass_attMass'          : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'm^{#tau_{#mu}#tau_{h}} (GeV)',},
    #'ammMass_attMassKinFit'    : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'm^{#tau_{#mu}#tau_{h}} Kin. Fit (GeV)',},
    'ammMass_hMass'            : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'm^{#mu#mu#tau_{#mu}#tau_{h}} (GeV)', 'rangey': [0,1000],},
    'ammMass_hMassKinFit'      : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'm^{#mu#mu#tau_{#mu}#tau_{h}} Kin. Fit (GeV)', 'rangey': [0,1000],},
    #'attMass_hMass'            : {'xaxis': 'm^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'm^{#mu#mu#tau_{#mu}#tau_{h}} (GeV)', 'rangey': [0,1000],},
    ##'attMassKinFit_hMassKinFit': {'xaxis': 'm^{#tau_{#mu}#tau_{h}} Kin. Fit (GeV)', 'yaxis': 'm^{#mu#mu#tau_{#mu}#tau_{h}} Kin. Fit (GeV)', 'rangey': [0,1000],},
    #'hMass_hMassKinFit'        : {'xaxis': 'm^{#mu#mu#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'm^{#mu#mu#tau_{#mu}#tau_{h}} Kin. Fit (GeV)', 'rangex': [0,1000], 'rangey': [0,1000],},
    #'ammMass_ammDeltaR'        : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': '#Delta R(#mu#mu) (GeV)', 'rangey': [0,3],},
    #'attMass_attDeltaR'        : {'xaxis': 'm^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': '#Delta R(#tau_{#mu}#tau_{h}) (GeV)', 'rangey': [0,3],},
    #'attMcat_attDeltaR'        : {'xaxis': 'm_{CA}^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': '#Delta R(#tau_{#mu}#tau_{h}) (GeV)', 'rangey': [0,6],},
    'am2Iso_athIso'            : {'xaxis': '#mu_{2} Rel. Iso.', 'yaxis': '#tau_{h} MVA Iso.', 'rangex': [0,0.4], 'rangey': [-1,1],},
    'genChannel_athDM'         : {'xaxis': 'Gen Channel', 'yaxis': '#tau_{h} Decay Mode', 'text': True},
}

special = {
    'full_blinder': {
        'ammMass'               : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'Events / 0.5 GeV', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.1, range(10,300,5)), 'blinder': [4,25], 'logy': False, 'overflow': False},
    },
    'low': {
        'ammMass'               : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'Events / 50 MeV', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(100,400,5)), 'logy': False, 'overflow': False},
    },
    'jpsi': {
        'ammMass'               : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'Events / 20 MeV', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(290,400,2)), 'logy': False, 'overflow': False},
    },
    'bmeson': {
        'ammMass'               : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'Events / 100 MeV', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(400,700,10)), 'logy': False, 'overflow': False},
    },
    'upsilon': {
        'ammMass'               : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'Events / 100 MeV', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(850,1150,10)), 'logy': False, 'overflow': False},
    },
}

if toPlot:
    for p in plots.keys():
        if p not in toPlot: plots.pop(p)
    for s in special.keys():
        for p in special[s].keys():
            if p not in toPlot: special[s].pop(p)


############################
### MC based BG estimate ###
############################
if doMC:
    for sel in sels:
        plotter.clearHistograms()

        for s in samples:
            plotter.addHistogramToStack(s,sigMap[s])
        
        if 'lowmass' not in sel and 'highmass' not in sel:
            for signal in signals:
                plotter.addHistogram(signal,sigMap[signal],signal=True)
        
        if not blind or 'regionA' not in sel or 'lowmass' in sel or 'highmass' in sel: plotter.addHistogram('data',sigMap['data'])
        
        for plot in plots:
            kwargs = deepcopy(plots[plot])
            plotname = '{0}/{1}'.format(sel,plot)
            savename = '{0}/mc/{1}'.format(sel,plot)
            plotter.plot(plotname,savename,**kwargs)
        
        if blind and 'regionA' in sel and 'lowmass' not in sel and 'highmass' not in sel: plotter.addHistogram('data',sigMap['data'])
        
        for s in special:
            for plot in special[s]:
                kwargs = deepcopy(special[s][plot])
                plotname = '{0}/{1}'.format(sel,plot)
                savename = '{0}/mc/{1}_{2}'.format(sel,plot,s)
                plotter.plot(plotname,savename,**kwargs)

#########################
### Signals on 1 plot ###
#########################
if doDESY:
    plotter.clearHistograms()
    
    h = 125
    for a in [7,9]:
        name = signame.format(h=h,a=a)
        plotter.addHistogram(name,sigMap[name],signal=True,style={'linecolor': aColors[a]})
    
    for plot in plots:
        for sel in desysels:
            kwargs = deepcopy(plots[plot])
            if plot in plotsSignal: kwargs.update(deepcopy(plotsSignal[plot]))
            plotname = '{0}/{1}'.format(sel,plot)
            savename = '{0}/h{h}/{1}'.format(sel,plot,h=h)
            plotter.plot(plotname,savename,plotratio=False,**kwargs)
    

if doSignals:
    if doSignalHs:
        for h in hmasses:
            plotter.clearHistograms()
        
            for a in amasses:
                name = signame.format(h=h,a=a)
                plotter.addHistogram(name,sigMap[name],signal=True,style={'linecolor': aColors[a]})
        
            for plot in plots:
                for sel in signalsels:
                    if 'lowmass' in sel or 'highmass' in sel: continue
                    kwargs = deepcopy(plots[plot])
                    if plot in plotsSignal: kwargs.update(deepcopy(plotsSignal[plot]))
                    plotname = '{0}/{1}'.format(sel,plot)
                    savename = '{0}/h{h}/{1}'.format(sel,plot,h=h)
                    plotter.plot(plotname,savename,plotratio=False,**kwargs)
            
        
    if doSignalAs:
        for a in [5,15]:
            plotter.clearHistograms()
            
            for h in hmasses:
                name = signame.format(h=h,a=a)
                plotter.addHistogram(name,sigMap[name],signal=True,style={'linecolor': hColors[h]})
        
            for plot in plots:
                for sel in signalsels:
                    if 'lowmass' in sel or 'highmass' in sel: continue
                    kwargs = deepcopy(plots[plot])
                    if plot in plotsSignal: kwargs.update(deepcopy(plotsSignal[plot]))
                    plotname = '{0}/{1}'.format(sel,plot)
                    savename = '{0}/a{a}/{1}'.format(sel,plot,a=a)
                    plotter.plot(plotname,savename,plotratio=False,**kwargs)
        
    if doSignalHAs:
        for a in vbfmasses:
            for h in hmasses:
                plotter.clearHistograms()

                name = signame.format(h=h,a=a)
                ggname = ggsigname.format(h=h,a=a)
                vbfname = vbfsigname.format(h=h,a=a)
                plotter.addHistogram(ggname,sigMap[ggname],signal=True)
                plotter.addHistogram(vbfname,sigMap[vbfname],signal=True)
        
                for plot in plots:
                    for sel in signalsels:
                        if 'lowmass' in sel or 'highmass' in sel: continue
                        kwargs = deepcopy(plots[plot])
                        if plot in plotsSignal: kwargs.update(deepcopy(plotsSignal[plot]))
                        plotname = '{0}/{1}'.format(sel,plot)
                        savename = '{0}/h{h}a{a}/{1}'.format(sel,plot,a=a,h=h)
                        plotter.plotNormalized(plotname,savename,plotratio=False,**kwargs)
    
##################
### Datadriven ###
##################
# for now, only data (no mc subtraction)
def getDatadrivenPlot(*plots,**kwargs):
    region = kwargs.pop('region','A')
    source = kwargs.pop('source','D')
    looseMVA = kwargs.pop('looseMVA',None)
    tag = kwargs.pop('tag',None)
    histMap = {}
    for s in samples+signals+allsignals+['data','datadriven']: histMap[s] = []
    for plot in plots:
        aplot = '{}region{}/{}'.format(tag+'/' if tag else '',region,plot)
        bplot = '{}region{}_fakeFor{}/{}'.format(tag+'/' if tag else '',source,region,plot)
        if looseMVA:
            bplot = '{}region{}_fakeFor{}{:.1f}/{}'.format(tag+'/' if tag else '',source,region,looseMVA,plot)
        for s in samples+signals+allsignals+['data']: histMap[s] += [aplot]
        histMap['datadriven'] += [bplot]
    return histMap

if doDatadriven:
    ddSamples = []
    for s in ['data']:
        ddSamples += sigMap[s]

    for tag in tags:
        for looseMVA in [None]+newloose:
            for region, source in [('A','B'),('C','D'),('A','D'),('A','C'),('B','D')]:
                plotter.clearHistograms()

                plotter.addHistogramToStack('datadriven',ddSamples)

                for s in []:
                    plotter.addHistogramToStack(s,sigMap[s])
                
                if 'lowmass' not in tag and 'highmass' not in tag:
                    for signal in signals:
                        plotter.addHistogram(signal,sigMap[signal],signal=True)
                
                if not blind or 'lowmass' in tag or 'highmass' in tag: plotter.addHistogram('data',sigMap['data'])
            
                for plot in plots:
                    kwargs = deepcopy(plots[plot])
                    plotname = '{}'.format(plot)
                    savename = '{}region{}/datadriven_from{}/{}'.format(tag+'/' if tag else '',region,source,plot)
                    if looseMVA: savename = '{}region{}/datadriven_from{}{:.1f}/{}'.format(tag+'/' if tag else '',region,source,looseMVA,plot)
                    plotter.plot(getDatadrivenPlot(plotname,region=region,source=source,looseMVA=looseMVA,tag=tag),savename,**kwargs)

                if blind or ('lowmass' not in tag and 'highmass' not in tag): plotter.addHistogram('data',sigMap['data'])
                
                for s in special:
                    for plot in special[s]:
                        kwargs = deepcopy(special[s][plot])
                        plotname = '{}'.format(plot)
                        savename = '{}region{}/datadriven_from{}/{}_{}'.format(tag+'/' if tag else '',region,source,plot,s)
                        if looseMVA: savename = '{}region{}/datadriven_from{}{:.1f}/{}_{}'.format(tag+'/' if tag else '',region,source,looseMVA,plot,s)
                        plotter.plot(getDatadrivenPlot(plotname,region=region,source=source,looseMVA=looseMVA,tag=tag),savename,doGOF=False,**kwargs)

                for h in hmasses:
                    sigOrder = []
                    bgOrder = []
                    for a in amasses:
                        name = signame.format(h=h,a=a)
                        sigOrder += [name]
                        bgOrder += ['datadriven']
                        plotter.addHistogram(name,sigMap[name],signal=True,style={'linecolor': aColors[a]})

                    for plot in ['kinFitChi2']:
                        kwargs = deepcopy(plots[plot])
                        kwargs['yaxis'] = 'Significance'
                        kwargs['rebin'] = [x*0.2 for x in range(50)]
                        plotname = '{}'.format(plot)
                        savename = '{}region{}/datadriven_from{}/{}_significance_h{}'.format(tag+'/' if tag else '',region,source,plot,h)
                        if looseMVA: savename = '{}region{}/datadriven_from{}{:.1f}/{}_significiance_h{}'.format(tag+'/' if tag else '',region,source,looseMVA,plot,h)
                        plotter.plotSignificance(getDatadrivenPlot(plotname,region=region,source=source,looseMVA=looseMVA,tag=tag),sigOrder,bgOrder,savename,**kwargs)



def getMatrixDatadrivenPlot(*plots,**kwargs):
    region = kwargs.pop('region','A')
    sources = kwargs.pop('sources',['A','C'])
    fakeRegion = kwargs.pop('region','B')
    fakeSources = kwargs.pop('sources',['B','D'])
    tag = kwargs.pop('tag',None)
    doPrompt = kwargs.pop('doPrompt',True)
    doFake = kwargs.pop('doFake',False)
    histMap = {}
    for s in samples+signals+['data','matP','matF']: histMap[s] = []
    for plot in plots:
        #aplot = '{}region{}/{}'.format(tag+'/' if tag else '',region,plot)
        #for s in samples+signals+['data']: histMap[s] += [aplot]
        applot = ['matrixP/{}region{}_for{}/{}'.format(tag+'/' if tag else '',source,region,plot) for source in sources]
        afplot = ['matrixF/{}region{}_for{}/{}'.format(tag+'/' if tag else '',source,region,plot) for source in sources]
        bpplot = ['matrixP/{}region{}_for{}_fakeFor{}/{}'.format(tag+'/' if tag else '',source,fakeRegion,region,plot) for source in fakeSources]
        bfplot = ['matrixF/{}region{}_for{}_fakeFor{}/{}'.format(tag+'/' if tag else '',source,fakeRegion,region,plot) for source in fakeSources]
        if doPrompt:
            for s in samples+signals+['data']: histMap[s] += applot
            histMap['matP'] += bpplot
        if doFake:
            for s in samples+signals+['data']: histMap[s] += afplot
            histMap['matF'] += bfplot
    return histMap

def getMatrixPlot(*plots,**kwargs):
    region = kwargs.pop('region','A')
    sources = kwargs.pop('sources',['A','B','C','D'])
    tag = kwargs.pop('tag',None)
    doPrompt = kwargs.pop('doPrompt',True)
    doFake = kwargs.pop('doFake',True)
    histMap = {}
    for s in samples+signals+['data','matP','matF']: histMap[s] = []
    for plot in plots:
        #aplot = '{}region{}/{}'.format(tag+'/' if tag else '',region,plot)
        #for s in samples+signals+['data']: histMap[s] += [aplot]
        if doPrompt and doFake:
            aplot = ['{}region{}/{}'.format(tag+'/' if tag else '',source,plot) for source in sources]
        elif doPrompt:
            aplot = ['matrixP/{}region{}_for{}/{}'.format(tag+'/' if tag else '',source,region,plot) for source in sources]
        else:
            aplot = ['matrixF/{}region{}_for{}/{}'.format(tag+'/' if tag else '',source,region,plot) for source in sources]
        pplot = ['matrixP/{}region{}_for{}/{}'.format(tag+'/' if tag else '',source,region,plot) for source in sources]
        fplot = ['matrixF/{}region{}_for{}/{}'.format(tag+'/' if tag else '',source,region,plot) for source in sources]
        for s in samples+signals+['data']: histMap[s] += aplot
        if doPrompt: histMap['matP'] += pplot
        if doFake: histMap['matF'] += fplot
    return histMap

def getMatrixPredictionPlot(*plots,**kwargs):
    region = kwargs.pop('region','A')
    sources = kwargs.pop('sources',['A','B','C','D'])
    tag = kwargs.pop('tag',None)
    histMap = {}
    for s in samples+signals+['data','matP','matF']: histMap[s] = []
    for plot in plots:
        #aplot = '{}region{}/{}'.format(tag+'/' if tag else '',region,plot)
        #for s in samples+signals+['data']: histMap[s] += [aplot]
        aplot = ['{}region{}/{}'.format(tag+'/' if tag else '',region,plot)]
        pplot = ['matrixP/{}region{}_for{}_p/{}'.format(tag+'/' if tag else '',source,region,plot) for source in sources]
        fplot = ['matrixF/{}region{}_for{}_f/{}'.format(tag+'/' if tag else '',source,region,plot) for source in sources]
        for s in samples+signals+['data']: histMap[s] += aplot
        histMap['matP'] += pplot
        histMap['matF'] += fplot
    return histMap

if doMatrix:
    ddSamples = []
    for s in ['data']:
        ddSamples += sigMap[s]

    for tag in tags:
        for doPrompt, doFake in [(1,1),(1,0),(0,1)]:

            for region, sources in [('B',['B','D']),('A',['A','C'])]:
                plotter.clearHistograms()

                if doFake: plotter.addHistogramToStack('matF',ddSamples)
                if doPrompt: plotter.addHistogramToStack('matP',ddSamples)

                for s in []:
                    plotter.addHistogramToStack(s,sigMap[s])
                
                if 'lowmass' not in tag and 'highmass' not in tag:
                    for signal in signals:
                        plotter.addHistogram(signal,sigMap[signal],signal=True)
                
                if not blind or 'lowmass' in tag or 'highmass' in tag: plotter.addHistogram('data',sigMap['data'])
            
                for plot in plots:
                    kwargs = deepcopy(plots[plot])
                    plotname = '{}'.format(plot)
                    savename = '{}region{}/matrix/{}'.format(tag+'/' if tag else '',region,plot)
                    if doPrompt and not doFake: savename = '{}region{}/matrix_prompt/{}'.format(tag+'/' if tag else '',region,plot)
                    if not doPrompt and doFake: savename = '{}region{}/matrix_fake/{}'.format(tag+'/' if tag else '',region,plot)
                    plotter.plot(getMatrixPlot(plotname,region=region,sources=sources,tag=tag,doPrompt=doPrompt,doFake=doFake),savename,**kwargs)
                
                if blind or ('lowmass' not in tag and 'highmass' not in tag): plotter.addHistogram('data',sigMap['data'])
                
                for s in special:
                    for plot in special[s]:
                        kwargs = deepcopy(special[s][plot])
                        plotname = '{}'.format(plot)
                        savename = '{}region{}/matrix/{}_{}'.format(tag+'/' if tag else '',region,plot,s)
                        if doPrompt and not doFake: savename = '{}region{}/matrix_prompt/{}_{}'.format(tag+'/' if tag else '',region,plot,s)
                        if not doPrompt and doFake: savename = '{}region{}/matrix_fake/{}_{}'.format(tag+'/' if tag else '',region,plot,s)
                        plotter.plot(getMatrixPlot(plotname,region=region,sources=sources,tag=tag,doPrompt=doPrompt,doFake=doFake),savename,doGOF=False,**kwargs)


        for region, sources in [('B',['B','D']),('A',['A','C'])]:
            plotter.clearHistograms()

            plotter.addHistogramToStack('matF',ddSamples)
            plotter.addHistogramToStack('matP',ddSamples)

            for s in []:
                plotter.addHistogramToStack(s,sigMap[s])
            
            if tag=='':
                for signal in signals:
                    plotter.addHistogram(signal,sigMap[signal],signal=True)
            
            if not blind or 'lowmass' in tag or 'highmass' in tag: plotter.addHistogram('data',sigMap['data'])
        
            for plot in plots:
                kwargs = deepcopy(plots[plot])
                plotname = '{}'.format(plot)
                savename = '{}region{}/matrix_prediction/{}'.format(tag+'/' if tag else '',region,plot)
                plotter.plot(getMatrixPredictionPlot(plotname,region=region,sources=sources,tag=tag),savename,**kwargs)
            
            if blind or ('lowmass' not in tag and 'highmass' not in tag): plotter.addHistogram('data',sigMap['data'])
            
            for s in special:
                for plot in special[s]:
                    kwargs = deepcopy(special[s][plot])
                    plotname = '{}'.format(plot)
                    savename = '{}region{}/matrix_prediction/{}_{}'.format(tag+'/' if tag else '',region,plot,s)
                    plotter.plot(getMatrixPredictionPlot(plotname,region=region,sources=sources,tag=tag),savename,doGOF=False,**kwargs)

        for doPrompt, doFake in [(1,1),(1,0),(0,1)]:

            region = 'A'
            fakeRegion = 'B'
            sources = ['A','C']
            fakeSources = ['B','D']

            plotter.clearHistograms()

            if doFake: plotter.addHistogramToStack('matF',ddSamples)
            if doPrompt: plotter.addHistogramToStack('matP',ddSamples)

            for s in []:
                plotter.addHistogramToStack(s,sigMap[s])
            
            if 'lowmass' not in tag and 'highmass' not in tag:
                for signal in signals:
                    plotter.addHistogram(signal,sigMap[signal],signal=True)
            
            if not blind or 'lowmass' in tag or 'highmass' in tag: plotter.addHistogram('data',sigMap['data'])
        
            for plot in plots:
                kwargs = deepcopy(plots[plot])
                plotname = '{}'.format(plot)
                savename = '{}region{}/matrixDatadriven/{}'.format(tag+'/' if tag else '',region,plot)
                if doPrompt and not doFake: savename = '{}region{}/matrixDatadriven_prompt/{}'.format(tag+'/' if tag else '',region,plot)
                if not doPrompt and doFake: savename = '{}region{}/matrixDatadriven_fake/{}'.format(tag+'/' if tag else '',region,plot)
                plotter.plot(getMatrixDatadrivenPlot(plotname,region=region,sources=sources,fakeRegions=fakeRegion,fakeSources=fakeSources,tag=tag,doFake=doFake,doPrompt=doPrompt),savename,**kwargs)
            
            if blind or ('lowmass' not in tag and 'highmass' not in tag): plotter.addHistogram('data',sigMap['data'])
            
            for s in special:
                for plot in special[s]:
                    kwargs = deepcopy(special[s][plot])
                    plotname = '{}'.format(plot)
                    savename = '{}region{}/matrixDatadriven/{}_{}'.format(tag+'/' if tag else '',region,plot,s)
                    if doPrompt and not doFake: savename = '{}region{}/matrixDatadriven_prompt/{}_{}'.format(tag+'/' if tag else '',region,plot,s)
                    if not doPrompt and doFake: savename = '{}region{}/matrixDatadriven_fake/{}_{}'.format(tag+'/' if tag else '',region,plot,s)
                    plotter.plot(getMatrixDatadrivenPlot(plotname,region=region,sources=sources,fakeRegions=fakeRegion,fakeSources=fakeSources,tag=tag,doFake=doFake,doPrompt=doPrompt),savename,doGOF=False,**kwargs)


if doNormalizations:
    if doLowmass:
        regions = ['A','B','C','D']
    
        colors = {
            'A': ROOT.kBlue,
            'B': ROOT.kGreen,
            'C': ROOT.kOrange,
            'D': ROOT.kRed,
        }
    
        plotter.clearHistograms()
    
        for region in regions:
            plotter.addHistogram('region{}'.format(region),sigMap['data'],style={'name':'Region {}'.format(region), 'linecolor': colors[region], 'fillcolor': colors[region]})
    
            
        for plot in plots:
            kwargs = deepcopy(plots[plot])
            plotname = {'region{}'.format(region): 'lowmass/region{}/{}'.format(region,plot) for region in regions}
            savename = 'lowmass/regions/{}'.format(plot)
            plotter.plot(plotname,savename,**kwargs)
            savename = 'lowmass/regions_normalized/{}'.format(plot)
            plotter.plotNormalized(plotname,savename,**kwargs)
    
        for s in special:
            for plot in special[s]:
                kwargs = deepcopy(special[s][plot])
                plotname = {'region{}'.format(region): 'lowmass/region{}/{}'.format(region,plot) for region in regions}
                savename = 'lowmass/regions/{}_{}'.format(plot,s)
                plotter.plot(plotname,savename,**kwargs)
                savename = 'lowmass/regions_normalized/{}_{}'.format(plot,s)
                plotter.plotNormalized(plotname,savename,**kwargs)
    
        for plot in plots:
            kwargs = deepcopy(plots[plot])
            plotname = {
                'regionA': 'lowmass/regionA/{}'.format(plot),
                'regionB': 'lowmass/regionB_fakeForA/{}'.format(plot),
                'regionC': 'lowmass/regionC_fakeForA/{}'.format(plot),
                'regionD': 'lowmass/regionD_fakeForA/{}'.format(plot),
            }
            savename = 'lowmass/regions_datadriven/{}'.format(plot)
            plotter.plot(plotname,savename,**kwargs)
            savename = 'lowmass/regions_datadriven_normalized/{}'.format(plot)
            plotter.plotNormalized(plotname,savename,**kwargs)
    
        for s in special:
            for plot in special[s]:
                kwargs = deepcopy(special[s][plot])
                plotname = {
                    'regionA': 'lowmass/regionA/{}'.format(plot),
                    'regionB': 'lowmass/regionB_fakeForA/{}'.format(plot),
                    'regionC': 'lowmass/regionC_fakeForA/{}'.format(plot),
                    'regionD': 'lowmass/regionD_fakeForA/{}'.format(plot),
                }
                savename = 'lowmass/regions_datadriven/{}_{}'.format(plot,s)
                plotter.plot(plotname,savename,**kwargs)
                savename = 'lowmass/regions_datadriven_normalized/{}_{}'.format(plot,s)
                plotter.plotNormalized(plotname,savename,**kwargs)
                    
    
    if doHighmass:
        regions = ['A','B','C','D']
    
        colors = {
            'A': ROOT.kBlue,
            'B': ROOT.kGreen,
            'C': ROOT.kOrange,
            'D': ROOT.kRed,
        }
    
        plotter.clearHistograms()
    
        for region in regions:
            plotter.addHistogram('region{}'.format(region),sigMap['data'],style={'name':'Region {}'.format(region), 'linecolor': colors[region], 'fillcolor': colors[region]})
    
            
        for plot in plots:
            kwargs = deepcopy(plots[plot])
            plotname = {'region{}'.format(region): 'highmass/region{}/{}'.format(region,plot) for region in regions}
            savename = 'highmass/regions/{}'.format(plot)
            plotter.plot(plotname,savename,**kwargs)
            savename = 'highmass/regions_normalized/{}'.format(plot)
            plotter.plotNormalized(plotname,savename,**kwargs)
    
        for s in special:
            for plot in special[s]:
                kwargs = deepcopy(special[s][plot])
                plotname = {'region{}'.format(region): 'highmass/region{}/{}'.format(region,plot) for region in regions}
                savename = 'highmass/regions/{}_{}'.format(plot,s)
                plotter.plot(plotname,savename,**kwargs)
                savename = 'highmass/regions_normalized/{}_{}'.format(plot,s)
                plotter.plotNormalized(plotname,savename,**kwargs)
    
        for plot in plots:
            kwargs = deepcopy(plots[plot])
            plotname = {
                'regionA': 'highmass/regionA/{}'.format(plot),
                'regionB': 'highmass/regionB_fakeForA/{}'.format(plot),
                'regionC': 'highmass/regionC_fakeForA/{}'.format(plot),
                'regionD': 'highmass/regionD_fakeForA/{}'.format(plot),
            }
            savename = 'highmass/regions_datadriven/{}'.format(plot)
            plotter.plot(plotname,savename,**kwargs)
            savename = 'highmass/regions_datadriven_normalized/{}'.format(plot)
            plotter.plotNormalized(plotname,savename,**kwargs)
    
        for s in special:
            for plot in special[s]:
                kwargs = deepcopy(special[s][plot])
                plotname = {
                    'regionA': 'highmass/regionA/{}'.format(plot),
                    'regionB': 'highmass/regionB_fakeForA/{}'.format(plot),
                    'regionC': 'highmass/regionC_fakeForA/{}'.format(plot),
                    'regionD': 'highmass/regionD_fakeForA/{}'.format(plot),
                }
                savename = 'highmass/regions_datadriven/{}_{}'.format(plot,s)
                plotter.plot(plotname,savename,**kwargs)
                savename = 'highmass/regions_datadriven_normalized/{}_{}'.format(plot,s)
                plotter.plotNormalized(plotname,savename,**kwargs)
                    

################
### 2D plots ###
################
if do2D:
    allsamples = signals+['data']
    if doAllSignals:
        allsamples = allsignals+['data']
    for sample in allsamples:
        plotter.clearHistograms()
        plotter.addHistogram(sample,sigMap[sample])
        
        for plot in plots2D:
            thesels = signalsels if sample in allsignals else sels
            for sel in thesels:
                #if sample=='data' and blind and 'regionD' not in sel: continue
                kwargs = deepcopy(plots2D[plot])
                #if sample not in allsignals:
                #    kwargs['rebinx'] = 10
                #    kwargs['rebiny'] = 10
                plotname = '{0}/{1}'.format(sel,plot)
                savename = '{0}/2D/{1}/{2}'.format(sel,sample,plot)
                plotter.plot2D(plotname,savename,**kwargs)





