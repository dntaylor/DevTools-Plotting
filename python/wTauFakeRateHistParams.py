from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

genCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'

def buildWTauFakeRate(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['WTauFakeRate'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],               },
        'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': '1./pileupWeight'},
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [500, -3.14159, 3.14159],},
        # z
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [500, 0, 500],           },
        'mllMinusMZ'                  : {'xVariable': 'fabs(z_mass-{0})'.format(ZMASS), 'xBinning': [200, 0, 200],           },
        'zPt'                         : {'xVariable': 'z_pt',                           'xBinning': [500, 0, 500],           },
        'zDeltaR'                     : {'xVariable': 'z_deltaR',                       'xBinning': [500, 0, 5],             },
        # t
        'wtMt'                        : {'xVariable': 'wt_mt',                          'xBinning': [500, 0, 500],           },
        'wtPt'                        : {'xVariable': 'wt_pt',                          'xBinning': [500, 0, 500],           },
        'tPt'                         : {'xVariable': 't_pt',                           'xBinning': [500, 0, 500],           },
        'tEta'                        : {'xVariable': 't_eta',                          'xBinning': [500, -2.5, 2.5],        },
        # m
        'wmMt'                        : {'xVariable': 'wm_mt',                          'xBinning': [500, 0, 500],           },
        'wmPt'                        : {'xVariable': 'wm_pt',                          'xBinning': [500, 0, 500],           },
        'mPt'                         : {'xVariable': 'm_pt',                           'xBinning': [500, 0, 500],           },
        'mEta'                        : {'xVariable': 'm_eta',                          'xBinning': [500, -2.5, 2.5],        },
    }

    frBaseCut = 'z_deltaR>0.02 && m_pt>25.'
    frBaseCutLoose = '{0}'.format(frBaseCut)
    frBaseCutMedium = '{0} && t_passMedium==1'.format(frBaseCut)
    frBaseCutTight = '{0} && t_passTight==1'.format(frBaseCut)
    frScaleFactorLoose = 'm_tightScale*t_looseScale*genWeight*pileupWeight*triggerEfficiency'
    frScaleFactorMedium = 'm_tightScale*t_mediumScale*genWeight*pileupWeight*triggerEfficiency'
    frScaleFactorTight = 'm_tightScale*t_tightScale*genWeight*pileupWeight*triggerEfficiency'
    selectionParams['WTauFakeRate'] = {
        'loose'      : {'args': [frBaseCutLoose],                   'kwargs': {'mcscalefactor': frScaleFactorLoose, }},
        'medium'     : {'args': [frBaseCutMedium],                  'kwargs': {'mcscalefactor': frScaleFactorMedium,}},
        'tight'      : {'args': [frBaseCutTight],                   'kwargs': {'mcscalefactor': frScaleFactorTight, }},
    }
    
    subsels = {
        'SS'     : 't_charge==m_charge',
        'ZVeto'  : '(z_mass<40 || z_mass>100)',
        'WMt'    : 'wm_mt>60.',
        'all'    : '(z_mass<40 || z_mass>100) && wm_mt>60. && t_charge==m_charge',
    }
    
    for sel in ['loose','medium','tight']:
        for sub in subsels:
            name = '{0}/{1}'.format(sel,sub)
            selectionParams['WTauFakeRate'][name] = deepcopy(selectionParams['WTauFakeRate'][sel])
            args = selectionParams['WTauFakeRate'][name]['args']
            selectionParams['WTauFakeRate'][name]['args'][0] = ' && '.join([args[0],subsels[sub]])
    
    etaBins = [0.,0.8,1.479,2.3]
    
    sels = selectionParams['WTauFakeRate'].keys()
    for sel in sels:
        for eb in range(len(etaBins)-1):
            name = '{0}/etaBin{1}'.format(sel,eb)
            selectionParams['WTauFakeRate'][name] = deepcopy(selectionParams['WTauFakeRate'][sel])
            args = selectionParams['WTauFakeRate'][name]['args']
            selectionParams['WTauFakeRate'][name]['args'][0] = ' && '.join([args[0],'fabs(t_eta)>={0} && fabs(t_eta)<{1}'.format(etaBins[eb],etaBins[eb+1])])

