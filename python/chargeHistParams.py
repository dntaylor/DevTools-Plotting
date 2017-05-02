from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

genCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'

def buildCharge(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['Charge'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        #'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],               },
        #'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': '1./pileupWeight'},
        #'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        #'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [500, -3.14159, 3.14159],},
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [500, 0, 500],          },
        #'mllMinusMZ'                  : {'xVariable': 'fabs(z_mass-{0})'.format(ZMASS), 'xBinning': [2000, 0, 200],          },
        #'zPt'                         : {'xVariable': 'z_pt',                           'xBinning': [5000, 0, 500],          },
        #'zEta'                        : {'xVariable': 'z_eta',                          'xBinning': [1000, -5, 5],           },
        #'zDeltaR'                     : {'xVariable': 'z_deltaR',                       'xBinning': [500, 0, 5],             },
        'zLeadingLeptonPt'            : {'xVariable': 'z1_pt',                          'xBinning': [1000, 0, 1000],        },
        'zLeadingLeptonEta'           : {'xVariable': 'z1_eta',                         'xBinning': [50, -2.5, 2.5],        },
        'zSubLeadingLeptonPt'         : {'xVariable': 'z2_pt',                          'xBinning': [1000, 0, 1000],        },
        'zSubLeadingLeptonEta'        : {'xVariable': 'z2_eta',                         'xBinning': [50, -2.5, 2.5],        },
    }

    chargeBaseCut = 'z1_passMedium==1 && z2_passMedium==1 && z_deltaR>0.02 && z1_pt>30. && z2_pt>15.'
    emZMassCut = 'fabs(z_mass-{0})<10.'.format(ZMASS)
    OS = 'z1_charge!=z2_charge'
    SS = 'z1_charge==z2_charge'
    genDiff1 = 'z1_charge!=z1_genCharge'
    genDiff2 = 'z2_charge!=z2_genCharge'
    chargeOS = '{0} && {1} && {2}'.format(chargeBaseCut,emZMassCut,OS)
    chargeSS = '{0} && {1} && {2}'.format(chargeBaseCut,emZMassCut,SS)
    bb = 'fabs(z1_eta)<1.479 && fabs(z2_eta)<1.479'
    ee = 'fabs(z1_eta)>1.479 && fabs(z2_eta)>1.479'
    chargeScaleFactor = 'z1_mediumScale*z2_mediumScale*genWeight*pileupWeight*triggerEfficiency'
    selectionParams['Charge'] = {
        'OS' : {'args': [chargeOS],        'kwargs': {'mcscalefactor': chargeScaleFactor}},
        'SS' : {'args': [chargeSS],        'kwargs': {'mcscalefactor': chargeScaleFactor}},
        'OSBB' : {'args': [chargeOS + ' && ' + bb],        'kwargs': {'mcscalefactor': chargeScaleFactor}},
        'SSBB' : {'args': [chargeSS + ' && ' + bb],        'kwargs': {'mcscalefactor': chargeScaleFactor}},
        'OSEE' : {'args': [chargeOS + ' && ' + ee],        'kwargs': {'mcscalefactor': chargeScaleFactor}},
        'SSEE' : {'args': [chargeSS + ' && ' + ee],        'kwargs': {'mcscalefactor': chargeScaleFactor}},
        'SS1': {'args': [chargeSS],        'kwargs': {'mcscalefactor': chargeScaleFactor, 'mccut': genDiff1}},
        'SS2': {'args': [chargeSS],        'kwargs': {'mcscalefactor': chargeScaleFactor, 'mccut': genDiff2}},
    }
    
    channelMap = {
        'ee': ['ee'],
        'mm': ['mm'],
    }
    projectionParams['Charge'] = {}
    for chan in channelMap:
        projectionParams['Charge'][chan] = channelMap[chan]
    histParams['Charge'].update(addChannels(deepcopy(histParams['Charge']),'channel',len(channelMap)))

