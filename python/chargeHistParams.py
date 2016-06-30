from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

genCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'

def buildCharge(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['Charge'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],               },
        'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': '1./pileupWeight'},
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [500, -3.14159, 3.14159],},
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [5000, 0, 500],          },
        'mllMinusMZ'                  : {'xVariable': 'fabs(z_mass-{0})'.format(ZMASS), 'xBinning': [2000, 0, 200],          },
        'zPt'                         : {'xVariable': 'z_pt',                           'xBinning': [5000, 0, 500],          },
        'zEta'                        : {'xVariable': 'z_eta',                          'xBinning': [1000, -5, 5],           },
        'zDeltaR'                     : {'xVariable': 'z_deltaR',                       'xBinning': [500, 0, 5],             },
        'zLeadingLeptonPt'            : {'xVariable': 'z1_pt',                          'xBinning': [10000, 0, 1000],        },
        'zLeadingLeptonEta'           : {'xVariable': 'z1_eta',                         'xBinning': [500, -2.5, 2.5],        },
        'zSubLeadingLeptonPt'         : {'xVariable': 'z2_pt',                          'xBinning': [10000, 0, 1000],        },
        'zSubLeadingLeptonEta'        : {'xVariable': 'z2_eta',                         'xBinning': [500, -2.5, 2.5],        },
    }

    chargeBaseCut = 'z1_passMedium==1 && z2_passMedium==1 && z_deltaR>0.02 && z1_pt>25. && z2_pt>10.'
    OS = 'z1_charge!=z2_charge'
    SS = 'z1_charge==z2_charge'
    chargeOS = '{0} && {1}'.format(chargeBaseCut,OS)
    chargeSS = '{0} && {1}'.format(chargeBaseCut,SS)
    emZMassCut = 'fabs(z_mass-{1})<10.'.format(chargeBaseCut,ZMASS)
    chargeScaleFactor = 'z1_mediumScale*z2_mediumScale*genWeight*pileupWeight*triggerEfficiency'
    selectionParams['Charge'] = {
        'OS' : {'args': [chargeOS],        'kwargs': {'mcscalefactor': chargeScaleFactor}},
        'SS' : {'args': [chargeSS],        'kwargs': {'mcscalefactor': chargeScaleFactor}},
    }
    
    channelMap = {
        'ee': ['ee'],
        'mm': ['mm'],
    }
    projectionParams['Charge'] = {}
    for chan in channelMap:
        projectionParams['Charge'][chan] = channelMap[chan]
    histParams['Charge'].update(addChannels(deepcopy(histParams['Charge']),'channel',len(channelMap)))
