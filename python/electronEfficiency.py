import os
import sys
import logging
from DevTools.Plotter.Efficiency import Efficiency
import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


eEfficiency = Efficiency('Electron')

sigMap = {
    'TT'  : [
             #'TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            ],
    'HppHmm200GeV'  : ['HPlusPlusHMinusMinusHTo4L_M-200_TuneCUETP8M1_13TeV_pythia8'],
    'HppHmm300GeV'  : ['HPlusPlusHMinusMinusHTo4L_M-300_TuneCUETP8M1_13TeV_pythia8'],
    'HppHmm400GeV'  : ['HPlusPlusHMinusMinusHTo4L_M-400_TuneCUETP8M1_13TeV_pythia8'],
    'HppHmm500GeV'  : ['HPlusPlusHMinusMinusHTo4L_M-500_TuneCUETP8M1_13TeV_pythia8'],
    'HppHmm600GeV'  : ['HPlusPlusHMinusMinusHTo4L_M-600_TuneCUETP8M1_13TeV_pythia8'],
    'HppHmm700GeV'  : ['HPlusPlusHMinusMinusHTo4L_M-700_TuneCUETP8M1_13TeV_pythia8'],
    'HppHmm800GeV'  : ['HPlusPlusHMinusMinusHTo4L_M-800_TuneCUETP8M1_13TeV_pythia8'],
    'HppHmm900GeV'  : ['HPlusPlusHMinusMinusHTo4L_M-900_TuneCUETP8M1_13TeV_pythia8'],
    'HppHmm1000GeV' : ['HPlusPlusHMinusMinusHTo4L_M-1000_TuneCUETP8M1_13TeV_pythia8'],
    'HppHmm1100GeV' : ['HPlusPlusHMinusMinusHTo4L_M-1100_TuneCUETP8M1_13TeV_pythia8'],
    'HppHmm1200GeV' : ['HPlusPlusHMinusMinusHTo4L_M-1200_TuneCUETP8M1_13TeV_pythia8'],
    'HppHmm1300GeV' : ['HPlusPlusHMinusMinusHTo4L_M-1300_TuneCUETP8M1_13TeV_pythia8'],
    'HppHmm1400GeV' : ['HPlusPlusHMinusMinusHTo4L_M-1400_TuneCUETP8M1_13TeV_pythia8'],
    'HppHmm1500GeV' : ['HPlusPlusHMinusMinusHTo4L_M-1500_TuneCUETP8M1_13TeV_pythia8'],
}

promptCut = '{0}_genMatch==1 && {0}_genIsPrompt==1 && {0}_genDeltaR<0.1'
promptTauCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'
genStatusOneCut = '{0}_genMatch==1 && {0}_genStatus==1 && {0}_genDeltaR<0.1'
genCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'
fakeCut = '({0}_genMatch==0 || ({0}_genMatch==1 && {0}_genIsFromHadron && {0}_genDeltaR<0.1))'
fakeTauCut = '({0}_genMatch==0 || ({0}_genMatch==1 && {0}_genDeltaR>0.1))'

ePrompt = promptCut.format('e')
eFake = fakeCut.format('e')

signal = 'HppHmm1000GeV'
background = 'TT'

sigCutMap = {}
for s in sigMap[signal]:
    sigCutMap[s] = ePrompt
bgCutMap = {}
for b in sigMap[background]:
    bgCutMap[b] = eFake

eEfficiency.addProcess('Prompt',sigMap[signal],sampleCuts=sigCutMap)
eEfficiency.addProcess('Fake',sigMap[background],sampleCuts=bgCutMap)

eEfficiency.printEfficiency(['e_cutBasedMedium'],baseSelection='e_pt>20 && fabs(e_eta)<2.5')
