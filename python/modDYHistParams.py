from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

genCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'

def buildModDY(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['ModDY'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [500, -3.14159, 3.14159],},
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [5000, 0, 500],          },
        'zPt'                         : {'xVariable': 'z_pt',                           'xBinning': [5000, 0, 500],          },
        'zLeadingLeptonPt'            : {'xVariable': 'z1_pt',                          'xBinning': [10000, 0, 1000],        },
        'zLeadingLeptonEta'           : {'xVariable': 'z1_eta',                         'xBinning': [500, -2.5, 2.5],        },
        'zSubLeadingLeptonPt'         : {'xVariable': 'z2_pt',                          'xBinning': [10000, 0, 1000],        },
        'zSubLeadingLeptonEta'        : {'xVariable': 'z2_eta',                         'xBinning': [500, -2.5, 2.5],        },
    }

    dyBaseCut = 'z1_passMedium==1 && z2_passMedium==1 && z_deltaR>0.02 && z_mass>60. && z1_pt>26. && z2_pt>20. && z_mass<120. && 1'
    dyScaleFactor = 'z1_mediumScale*z2_mediumScale*genWeight*pileupWeight*triggerEfficiency'
    
    selectionParams['ModDY'] = {
        'default' : {'args': [dyBaseCut],              'kwargs': {'mcscalefactor': dyScaleFactor}},
    }
    

    sampleScales = {
        'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8' : 'zPtWeight', 
        'DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8': 'zPtWeight', 
        'DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8': 'zPtWeight', 
        'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : 'zPtWeight', 
        'DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'zPtWeight', 
        'DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'zPtWeight', 
        'DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'zPtWeight', 
        'DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'zPtWeight', 
        'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'     : 'zPtWeight', 
    }

    sampleSelectionParams['ModDY'] = {}
    for sample,scale in sampleScales.iteritems():
        sampleSelectionParams['ModDY'][sample] = deepcopy(selectionParams['ModDY'])
        for sel in selectionParams['ModDY'].keys():
            sampleSelectionParams['ModDY'][sample][sel]['kwargs']['mcscalefactor'] = '{}*{}'.format(dyScaleFactor,scale)
