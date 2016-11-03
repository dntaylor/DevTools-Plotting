from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

genCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'

def buildDijetFakeRate(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['DijetFakeRate'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        'pt'                          : {'xVariable': 'l1_pt',                          'xBinning': [2000,0,2000],           },
        'eta'                         : {'xVariable': 'l1_eta',                         'xBinning': [600,-3.,3.],            },
        'wMass'                       : {'xVariable': 'w_mt',                           'xBinning': [500, 0, 500],           },
    }

    frBaseCut = 'w_mt<25 && met_pt<25'
    frBaseCutLoose = '{0}'.format(frBaseCut)
    frBaseCutMedium = '{0} && l1_passMedium==1'.format(frBaseCut)
    frBaseCutTight = '{0} && l1_passTight==1'.format(frBaseCut)
    frScaleFactorLoose = 'l1_looseScale*genWeight*pileupWeight*triggerEfficiency/triggerPrescale'
    frScaleFactorMedium = 'l1_mediumScale*genWeight*pileupWeight*triggerEfficiency/triggerPrescale'
    frScaleFactorTight = 'l1_tightScale*genWeight*pileupWeight*triggerEfficiency/triggerPrescale'
    #dataScaleFactor = 'triggerPrescale'
    dataScaleFactor = '1'
    selectionParams['DijetFakeRate'] = {
        'loose'      : {'args': [frBaseCutLoose],                   'kwargs': {'mcscalefactor': frScaleFactorLoose,  'datascalefactor': dataScaleFactor}},
        'medium'     : {'args': [frBaseCutMedium],                  'kwargs': {'mcscalefactor': frScaleFactorMedium, 'datascalefactor': dataScaleFactor}},
        'tight'      : {'args': [frBaseCutTight],                   'kwargs': {'mcscalefactor': frScaleFactorTight,  'datascalefactor': dataScaleFactor}},
    }
    
    channels = ['e','m']
    
    etaBins = {
        'e': [0.,0.5,1.0,1.479,2.0,2.5],
        'm': [0.,1.2,2.4],
    }
    ptBins = {
        'e': [10,15,20,25,30,40,50,60,80,100,2000],
        'm': [10,15,20,25,30,40,50,60,80,100,2000],
    }
    
    jetPtBins = [10,15,20,25,30,35,40,45,50]
    
    for sel in ['loose','medium','tight']:
        for chan in channels:
            name = '{0}/{1}'.format(sel,chan)
            selectionParams['DijetFakeRate'][name] = deepcopy(selectionParams['DijetFakeRate'][sel])
            args = selectionParams['DijetFakeRate'][name]['args']
            selectionParams['DijetFakeRate'][name]['args'][0] = args[0] + '&& channel=="{0}"'.format(chan)
            for jetPt in jetPtBins:
                name = '{0}/{1}/jetPt{2}'.format(sel,chan,jetPt)
                selectionParams['DijetFakeRate'][name] = deepcopy(selectionParams['DijetFakeRate'][sel])
                args = selectionParams['DijetFakeRate'][name]['args']
                selectionParams['DijetFakeRate'][name]['args'][0] = args[0] + '&& channel=="{0}" && leadJet_pt>{1}'.format(chan,jetPt)
            if 'pt20' in sel: continue
            for eb in range(len(etaBins[chan])-1):
                directory = '{0}/{1}/etaBin{2}'.format('/'.join(sel.split('_')),chan,eb)
                name = '{0}/{1}/etaBin{2}'.format(sel,chan,eb)
                selectionParams['DijetFakeRate'][name] = deepcopy(selectionParams['DijetFakeRate'][sel])
                args = selectionParams['DijetFakeRate'][name]['args']
                selectionParams['DijetFakeRate'][name]['args'][0] = args[0] + '&& channel=="{0}" && fabs(l1_eta)>={1} && fabs(l1_eta)<{2}'.format(chan,etaBins[chan][eb],etaBins[chan][eb+1])


    # special selections for samples
    # DY-10 0, 1, 2 bins (0 includes 3+)
    # DY-50 0, 1, 2, 3, 4 bins (0 includes 5+)
    sampleCuts = {
        #'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8' : '(numGenJets==0 || numGenJets>2)',
        #'DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8': 'numGenJets==1',
        #'DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8': 'numGenJets==2',
        'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : '(numGenJets==0 || numGenJets>4)',
        'DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==1',
        'DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==2',
        'DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==3',
        'DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==4',
        'WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'           : '(numGenJets==0 || numGenJets>4)',
        'W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : 'numGenJets==1',
        'W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : 'numGenJets==2',
        'W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : 'numGenJets==3',
        'W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : 'numGenJets==4',
    }
    sampleSelectionParams['DijetFakeRate'] = {}
    for sample,cut in sampleCuts.iteritems():
        sampleSelectionParams['DijetFakeRate'][sample] = deepcopy(selectionParams['DijetFakeRate'])
        for sel in selectionParams['DijetFakeRate'].keys():
            sampleSelectionParams['DijetFakeRate'][sample][sel]['args'][0] += ' && {0}'.format(cut)

