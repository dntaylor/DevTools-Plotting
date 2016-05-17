import os
import sys
import logging
from DevTools.Plotter.Plotter import Plotter
import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


tPlotter = Plotter('Tau')

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
    'TTV' : [
             #'TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8',
             #'TTZToLLNuNu_M-10_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
             'ttWJets_13TeV_madgraphMLM',
             'ttZJets_13TeV_madgraphMLM',
            ],
    'WW'  : [
             'WWTo2L2Nu_13TeV-powheg',
             'WWToLNuQQ_13TeV-powheg',
            ],
    'Z'   : [
             'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
            ],
    'TT'  : [
             #'TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
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
             'MuonEG',
             'SingleMuon',
             'SingleElectron',
             'DoubleTau',
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

sigcolors = [
    ROOT.TColor.GetColor('#000000'),
    #ROOT.TColor.GetColor('#1A0000'),
    ROOT.TColor.GetColor('#330000'),
    #ROOT.TColor.GetColor('#4C0000'),
    ROOT.TColor.GetColor('#660000'),
    ROOT.TColor.GetColor('#800000'),
    ROOT.TColor.GetColor('#990000'),
    ROOT.TColor.GetColor('#B20000'),
    ROOT.TColor.GetColor('#CC0000'),
    #ROOT.TColor.GetColor('#E60000'),
    ROOT.TColor.GetColor('#FF0000'),
    #ROOT.TColor.GetColor('#FF1919'),
    ROOT.TColor.GetColor('#FF3333'),
    #ROOT.TColor.GetColor('#FF4D4D'),
    ROOT.TColor.GetColor('#FF6666'),
    ROOT.TColor.GetColor('#FF8080'),
    ROOT.TColor.GetColor('#FF9999'),
    ROOT.TColor.GetColor('#FFB2B2'),
    ROOT.TColor.GetColor('#FFCCCC'),
]


tPlotter.addHistogram('signew',sigMap['HppHmm1000GeV'],style={'name': 'New DMs (match tau gen jet)','linecolor':ROOT.kRed})
tPlotter.addHistogram('sigold',sigMap['HppHmm1000GeV'],style={'name': 'Old DMs (match tau gen jet)','linecolor':ROOT.kBlue})
tPlotter.addHistogram('fakenew',sigMap['QCD'],style={'name':'New DMs (fake)','linecolor':ROOT.kRed,'linestyle':2})
tPlotter.addHistogram('fakeold',sigMap['QCD'],style={'name':'Old DMs (fake)','linecolor':ROOT.kBlue,'linestyle':2})

idNames = [
    '{0}_vlooseElectron_looseMuon_looseIsolation',
    '{0}_vlooseElectron_looseMuon_tightIsolation',
    '{0}_vlooseElectron_looseMuon_vtightIsolation',
    '{0}_tightElectron_tightMuon_looseIsolation',
    '{0}_tightElectron_tightMuon_tightIsolation',
    '{0}_tightElectron_tightMuon_vtightIsolation',
]

binning = [0,20,40,60,80,100,120,140,160,180,200,220,240,260,280,300,350,400,450,500,550,600,650,700,800,900,1000]
binning = [0,20,40,60,80,100,120,140,160,180,200,240,300,400,500,600,800,1000]
for idName in idNames:
    num = {
        'signew': 'default/prompt/{0}/pt'.format(idName.format('new')),
        'sigold': 'default/prompt/{0}/pt'.format(idName.format('old')),
        'fakenew': 'default/fake/{0}/pt'.format(idName.format('new')),
        'fakeold': 'default/fake/{0}/pt'.format(idName.format('old')),
    }
    denom = {
        'signew': 'default/prompt/pt',
        'sigold': 'default/prompt/pt',
        'fakenew': 'default/fake/pt',
        'fakeold': 'default/fake/pt',
    }
    savename = idName.format('tau')
    tPlotter.plotRatio(num,denom,savename,rebin=binning,xaxis='p_{T} (GeV)',numcol=2,ymax=1.2)
