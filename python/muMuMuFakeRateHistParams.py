from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

def buildMuMuMuFakeRate(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['MuMuMuFakeRate'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        #'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [60,0,60],               },
        #'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [60,0,60],                'mcscale': '1./pileupWeight'},
        #'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        #'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [100, -3.14159, 3.14159],},
        # z
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [120, 60, 120],          },
        'z1Pt'                        : {'xVariable': 'z1_pt',                          'xBinning': [500, 0, 500],           },
        'z2Pt'                        : {'xVariable': 'z2_pt',                          'xBinning': [500, 0, 500],           },
        # m
        'mPt'                         : {'xVariable': 'm_pt',                           'xBinning': [500, 0, 500],           },
    }

    baseCut = 'z_mass>81 && z_mass<101'
    scaleFactor = 'genWeight*pileupWeight*triggerEfficiency'
    
    selectionParams['MuMuMuFakeRate'] = {
        'default'               : {'args': [baseCut],                                                                                   'kwargs': {'mcscalefactor': scaleFactor}},
        'iso0.15'               : {'args': [baseCut + ' && m_isolation<0.15'],                                                          'kwargs': {'mcscalefactor': scaleFactor}},
        'iso0.25'               : {'args': [baseCut + ' && m_isolation<0.25'],                                                          'kwargs': {'mcscalefactor': scaleFactor}},
        'iso0.40'               : {'args': [baseCut + ' && m_isolation<0.40'],                                                          'kwargs': {'mcscalefactor': scaleFactor}},
        'defaulttrig'           : {'args': [baseCut + ' && (m_matches_IsoMu24 || m_matches_IsoTkMu24)'],                                'kwargs': {'mcscalefactor': scaleFactor}},
        'iso0.15trig'           : {'args': [baseCut + ' && (m_matches_IsoMu24 || m_matches_IsoTkMu24)' + ' && m_isolation<0.15'],       'kwargs': {'mcscalefactor': scaleFactor}},
        'iso0.25trig'           : {'args': [baseCut + ' && (m_matches_IsoMu24 || m_matches_IsoTkMu24)' + ' && m_isolation<0.25'],       'kwargs': {'mcscalefactor': scaleFactor}},
        'iso0.40trig'           : {'args': [baseCut + ' && (m_matches_IsoMu24 || m_matches_IsoTkMu24)' + ' && m_isolation<0.40'],       'kwargs': {'mcscalefactor': scaleFactor}},
    }

    etaBins = [0.,1.0,1.5,2.4]

    for sel in selectionParams['MuMuMuFakeRate'].keys():
        for eb in range(len(etaBins)-1):
            name = '{0}/etaBin{1}'.format(sel,eb)
            selectionParams['MuMuMuFakeRate'][name] = deepcopy(selectionParams['MuMuMuFakeRate'][sel])
            args = selectionParams['MuMuMuFakeRate'][name]['args']
            selectionParams['MuMuMuFakeRate'][name]['args'][0] = args[0] + ' && fabs(m_eta)>={0} && fabs(m_eta)<{1}'.format(etaBins[eb],etaBins[eb+1])
