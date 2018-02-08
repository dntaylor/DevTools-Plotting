from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

def buildMuMuTauFakeRate(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['MuMuTauFakeRate'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        #'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [60,0,60],               },
        #'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [60,0,60],                'mcscale': '1./pileupWeight'},
        #'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        #'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [100, -3.14159, 3.14159],},
        # z
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [120, 60, 120],          },
        'z1Pt'                        : {'xVariable': 'z1_pt',                          'xBinning': [500, 0, 500],           },
        'z2Pt'                        : {'xVariable': 'z2_pt',                          'xBinning': [500, 0, 500],           },
        # t
        'tPt'                         : {'xVariable': 't_pt',                           'xBinning': [500, 0, 500],           },
    }

    baseCut = 'z_mass>81 && z_mass<101 && !(tjet_passCSVv2M>0.5)'
    scaleFactor = 'genWeight*pileupWeight*triggerEfficiency'
    
    selectionParams['MuMuTauFakeRate'] = {
        'default'               : {'args': [baseCut],                                                                                'kwargs': {'mcscalefactor': scaleFactor}},
        'vloose'                : {'args': [baseCut + ' && t_byVLooseIsolationMVArun2v1DBoldDMwLT>0.5'],                             'kwargs': {'mcscalefactor': scaleFactor}},
        'medium'                : {'args': [baseCut + ' && t_byMediumIsolationMVArun2v1DBoldDMwLT>0.5'],                             'kwargs': {'mcscalefactor': scaleFactor}},
        'nearMuon'              : {'args': [baseCut + ' && m_pt>0 && mt_deltaR<0.8'],                                                'kwargs': {'mcscalefactor': scaleFactor}},
        'nearMuonWithMVA'       : {'args': [baseCut + ' && m_pt>0 && mt_deltaR<0.8 && t_byIsolationMVArun2v1DBoldDMwLTraw>0.2'],     'kwargs': {'mcscalefactor': scaleFactor}},
        'nearMuonVLoose'        : {'args': [baseCut + ' && m_pt>0 && mt_deltaR<0.8 && t_byVLooseIsolationMVArun2v1DBoldDMwLT>0.5'],  'kwargs': {'mcscalefactor': scaleFactor}},
        'nearMuonMedium'        : {'args': [baseCut + ' && m_pt>0 && mt_deltaR<0.8 && t_byMediumIsolationMVArun2v1DBoldDMwLT>0.5'],  'kwargs': {'mcscalefactor': scaleFactor}},
    }

    for loosecut in [-1,-0.2,-0.1,0.0,0.1,0.2,0.3,0.4]:
        selectionParams['MuMuTauFakeRate']['nearMuonWithMVA{:.1f}'.format(loosecut)] = {
            'args': [baseCut + ' && m_pt>0 && mt_deltaR<0.8 && t_byIsolationMVArun2v1DBoldDMwLTraw>{}'.format(loosecut)],
            'kwargs': {'mcscalefactor': scaleFactor},
        }

    etaBins = [0.,1.479,2.3]

    for sel in selectionParams['MuMuTauFakeRate'].keys():
        for eb in range(len(etaBins)-1):
            name = '{0}/etaBin{1}'.format(sel,eb)
            selectionParams['MuMuTauFakeRate'][name] = deepcopy(selectionParams['MuMuTauFakeRate'][sel])
            args = selectionParams['MuMuTauFakeRate'][name]['args']
            selectionParams['MuMuTauFakeRate'][name]['args'][0] = args[0] + ' && fabs(t_eta)>={0} && fabs(t_eta)<{1}'.format(etaBins[eb],etaBins[eb+1])
