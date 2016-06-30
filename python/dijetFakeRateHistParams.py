from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

genCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'

def buildDijetFakeRate(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['DijetFakeRate'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],               },
        'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': '1./pileupWeight'},
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [500, -3.14159, 3.14159],},
        'pt'                          : {'xVariable': 'l1_pt',                          'xBinning': [2000,0,2000],           },
        'eta'                         : {'xVariable': 'l1_eta',                         'xBinning': [600,-3.,3.],            },
        'wMass'                       : {'xVariable': 'w_mt',                           'xBinning': [500, 0, 500],           },
    }

    frBaseCut = 'w_mt<25 && met_pt<25'
    frBaseCutLoose = '{0}'.format(frBaseCut)
    frBaseCutMedium = '{0} && l1_passMedium==1'.format(frBaseCut)
    frBaseCutTight = '{0} && l1_passTight==1'.format(frBaseCut)
    frScaleFactorLoose = 'l1_looseScale*genWeight*pileupWeight*triggerEfficiency'#/triggerPrescale'
    frScaleFactorMedium = 'l1_mediumScale*genWeight*pileupWeight*triggerEfficiency'#/triggerPrescale'
    frScaleFactorTight = 'l1_tightScale*genWeight*pileupWeight*triggerEfficiency'#/triggerPrescale'
    dataScaleFactor = 'triggerPrescale'
    selectionParams['DijetFakeRate'] = {
        'loose'      : {'args': [frBaseCutLoose],                   'kwargs': {'mcscalefactor': frScaleFactorLoose,  'datascalefactor': dataScaleFactor}},
        'medium'     : {'args': [frBaseCutMedium],                  'kwargs': {'mcscalefactor': frScaleFactorMedium, 'datascalefactor': dataScaleFactor}},
        'tight'      : {'args': [frBaseCutTight],                   'kwargs': {'mcscalefactor': frScaleFactorTight,  'datascalefactor': dataScaleFactor}},
        'loose/pt20' : {'args': [frBaseCutLoose + ' && l1_pt>20'],  'kwargs': {'mcscalefactor': frScaleFactorLoose,  'datascalefactor': dataScaleFactor}},
        'medium/pt20': {'args': [frBaseCutMedium + ' && l1_pt>20'], 'kwargs': {'mcscalefactor': frScaleFactorMedium, 'datascalefactor': dataScaleFactor}},
        'tight/pt20' : {'args': [frBaseCutTight + ' && l1_pt>20'],  'kwargs': {'mcscalefactor': frScaleFactorTight,  'datascalefactor': dataScaleFactor}},
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
    
    for sel in ['loose','medium','tight','loose/pt20','medium/pt20','tight/pt20']:
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

