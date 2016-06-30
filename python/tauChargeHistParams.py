from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

genCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'

def buildTauCharge(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['TauCharge'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],               },
        'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': '1./pileupWeight'},
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [500, -3.14159, 3.14159],},
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [5000, 0, 500],          },
        'zPt'                         : {'xVariable': 'z_pt',                           'xBinning': [5000, 0, 500],          },
        'zEta'                        : {'xVariable': 'z_eta',                          'xBinning': [1000, -5, 5],           },
        'zDeltaR'                     : {'xVariable': 'z_deltaR',                       'xBinning': [500, 0, 5],             },
        'zTauMuPt'                    : {'xVariable': 'm_pt',                           'xBinning': [10000, 0, 1000],        },
        'zTauMuEta'                   : {'xVariable': 'm_eta',                          'xBinning': [500, -2.5, 2.5],        },
        'zTauHadPt'                   : {'xVariable': 't_pt',                           'xBinning': [10000, 0, 1000],        },
        'zTauHadEta'                  : {'xVariable': 't_eta',                          'xBinning': [500, -2.5, 2.5],        },
        'tauMuMt'                     : {'xVariable': 'wm_mt',                          'xBinning': [5000, 0, 500],          },
        'tauHadMt'                    : {'xVariable': 'wt_mt',                          'xBinning': [5000, 0, 500],          },
    }

    chargeBaseCut = 'm_passMedium==1 && t_passMedium==1 && z_deltaR>0.02 && m_pt>25. && t_pt>20.'
    OS = 'm_charge!=t_charge'
    SS = 'm_charge==t_charge'
    chargeOS = '{0} && {1}'.format(chargeBaseCut,OS)
    chargeSS = '{0} && {1}'.format(chargeBaseCut,SS)
    tZMassCut = 'fabs(z_mass-60)<25.'.format(chargeBaseCut)
    chargeScaleFactor = 'm_mediumScale*t_mediumScale*genWeight*pileupWeight*triggerEfficiency'
    selectionParams['TauCharge'] = {
        'OS'       : {'args': [chargeOS],                   'kwargs': {'mcscalefactor': chargeScaleFactor}},
        'SS'       : {'args': [chargeSS],                   'kwargs': {'mcscalefactor': chargeScaleFactor}},
        'OS/mtCut' : {'args': [chargeOS + ' && wm_mt<40.'], 'kwargs': {'mcscalefactor': chargeScaleFactor}},
        'SS/mtCut' : {'args': [chargeSS + ' && wm_mt<40.'], 'kwargs': {'mcscalefactor': chargeScaleFactor}},
    }
    
    channelMap = {
        'tt': ['mt','tm'],
    }
    projectionParams['TauCharge'] = {}
    for chan in channelMap:
        projectionParams['TauCharge'][chan] = channelMap[chan]
    histParams['TauCharge'].update(addChannels(deepcopy(histParams['TauCharge']),'channel',len(channelMap)))

