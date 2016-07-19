from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

genCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'

def buildDY(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['DY'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],               },
        'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': '1./pileupWeight'},
        'numVertices_65000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_65000/pileupWeight'},
        'numVertices_66000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_66000/pileupWeight'},
        'numVertices_67000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_67000/pileupWeight'},
        'numVertices_68000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_68000/pileupWeight'},
        'numVertices_69000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_69000/pileupWeight'},
        'numVertices_70000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_70000/pileupWeight'},
        'numVertices_71000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_71000/pileupWeight'},
        'numVertices_72000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_72000/pileupWeight'},
        'numVertices_73000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_73000/pileupWeight'},
        'numVertices_74000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_74000/pileupWeight'},
        'numVertices_75000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_75000/pileupWeight'},
        'numVertices_76000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_76000/pileupWeight'},
        'numVertices_77000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_77000/pileupWeight'},
        'numVertices_78000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_78000/pileupWeight'},
        'numVertices_79000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_79000/pileupWeight'},
        'numVertices_80000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_80000/pileupWeight'},
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
        'nJets'                       : {'xVariable': 'numJetsTight30',                 'xBinning': [11, -0.5, 10.5],        },
    }

    dyBaseCut = 'z1_passMedium==1 && z2_passMedium==1 && z_deltaR>0.02 && z_mass>12. && z1_pt>25. && z2_pt>20. && z_mass>50.'
    dyScaleFactor = 'z1_mediumScale*z2_mediumScale*genWeight*pileupWeight*triggerEfficiency'
    
    bbCut = 'fabs(z1_eta)<1.479 && fabs(z2_eta)<1.479'
    ebCut = '((fabs(z1_eta)<1.479 && fabs(z2_eta)>1.479) || (fabs(z1_eta)>1.479 && fabs(z2_eta)<1.479))'
    eeCut = 'fabs(z1_eta)>1.479 && fabs(z2_eta)>1.479'
    
    selectionParams['DY'] = {
        'default' : {'args': [dyBaseCut],              'kwargs': {'mcscalefactor': dyScaleFactor}},
        'bbCut'   : {'args': [dyBaseCut+' && '+bbCut], 'kwargs': {'mcscalefactor': dyScaleFactor}},
        'ebCut'   : {'args': [dyBaseCut+' && '+ebCut], 'kwargs': {'mcscalefactor': dyScaleFactor}},
        'eeCut'   : {'args': [dyBaseCut+' && '+eeCut], 'kwargs': {'mcscalefactor': dyScaleFactor}},
    }
    
    channels = ['ee','mm']
    projectionParams['DY'] = {}
    for chan in channels:
        projectionParams['DY'][chan] = [chan]
    histParams['DY'].update(addChannels(deepcopy(histParams['DY']),'channel',len(channels)))

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
    sampleSelectionParams['DY'] = {}
    for sample,cut in sampleCuts.iteritems():
        sampleSelectionParams['DY'][sample] = deepcopy(selectionParams['DY'])
        for sel in selectionParams['DY'].keys():
            sampleSelectionParams['DY'][sample][sel]['args'][0] += ' && {0}'.format(cut)

