from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

def buildMuMuTauTau(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['MuMuTauTau'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [60,0,60],               },
        'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [60,0,60],                'mcscale': '1./pileupWeight'},
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [100, -3.14159, 3.14159],},
        # h
        'hMass'                       : {'xVariable': 'h_mass',                         'xBinning': [1000, 0, 1000],         },
        'hMt'                         : {'xVariable': 'hmet_mt',                        'xBinning': [1000, 0, 1000],         },
        'hDeltaMass'                  : {'xVariable': 'amm_mass-att_mass',              'xBinning': [1000, -500, 500],       },
        'hDeltaMt'                    : {'xVariable': 'amm_mass-attmet_mt',             'xBinning': [1000, -500, 500],       },
        # amm
        'ammMass'                     : {'xVariable': 'amm_mass',                       'xBinning': [120, 0, 30],            },
        'ammDeltaR'                   : {'xVariable': 'amm_deltaR',                     'xBinning': [100, 0, 1.5],           },
        'am1Pt'                       : {'xVariable': 'am1_pt',                         'xBinning': [500, 0, 500],           },
        'am2Pt'                       : {'xVariable': 'am2_pt',                         'xBinning': [500, 0, 500],           },
        # att
        'attMass'                     : {'xVariable': 'att_mass',                       'xBinning': [300, 0, 300],           },
        'attMt'                       : {'xVariable': 'attmet_mt',                      'xBinning': [300, 0, 300],           },
        'attDeltaR'                   : {'xVariable': 'att_deltaR',                     'xBinning': [400, 0, 6.0],           },
        'atmPt'                       : {'xVariable': 'atm_pt',                         'xBinning': [500, 0, 500],           },
        'athPt'                       : {'xVariable': 'ath_pt',                         'xBinning': [500, 0, 500],           },
    }

    baseCut = '1'
    scaleFactor = 'genWeight*pileupWeight*triggerEfficiency'
    
    selectionParams['MuMuTauTau'] = {
        'default' : {'args': [baseCut],                                                                                                  'kwargs': {'mcscalefactor': scaleFactor}},
        'regionA' : {'args': [baseCut + ' && am1_isolation<0.15 && am2_isolation<0.15 && ath_byVLooseIsolationMVArun2v1DBoldDMwLT>0.5'], 'kwargs': {'mcscalefactor': scaleFactor}},
        'regionB' : {'args': [baseCut + ' && am1_isolation<0.15 && am2_isolation<0.15 && ath_byVLooseIsolationMVArun2v1DBoldDMwLT<0.5'], 'kwargs': {'mcscalefactor': scaleFactor}},
        'regionC' : {'args': [baseCut + ' && am1_isolation>0.15 && am2_isolation>0.15 && ath_byVLooseIsolationMVArun2v1DBoldDMwLT>0.5'], 'kwargs': {'mcscalefactor': scaleFactor}},
        'regionD' : {'args': [baseCut + ' && am1_isolation>0.15 && am2_isolation>0.15 && ath_byVLooseIsolationMVArun2v1DBoldDMwLT<0.5'], 'kwargs': {'mcscalefactor': scaleFactor}},
    }
