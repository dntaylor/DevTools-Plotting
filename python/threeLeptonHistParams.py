from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

def buildThreeLepton(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams,**kwargs):
    shift = kwargs.pop('shift','')
    countOnly = kwargs.pop('countOnly',False)

    histParams['ThreeLepton'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        # electron
        'e1Pt'                        : {'xVariable': 'e1_pt',                          'xBinning': [1000, 0, 1000],         'selection': 'e1_pt>0',},
        'e1Eta'                       : {'xVariable': 'e1_eta',                         'xBinning': [500, -2.5, 2.5],        'selection': 'e1_pt>0',},
        'e2Pt'                        : {'xVariable': 'e2_pt',                          'xBinning': [1000, 0, 1000],         'selection': 'e2_pt>0',},
        'e2Eta'                       : {'xVariable': 'e2_eta',                         'xBinning': [500, -2.5, 2.5],        'selection': 'e2_pt>0',},
        'e3Pt'                        : {'xVariable': 'e3_pt',                          'xBinning': [1000, 0, 1000],         'selection': 'e3_pt>0',},
        'e3Eta'                       : {'xVariable': 'e3_eta',                         'xBinning': [500, -2.5, 2.5],        'selection': 'e3_pt>0',},
        # muon
        'm1Pt'                        : {'xVariable': 'm1_pt',                          'xBinning': [1000, 0, 1000],         'selection': 'm1_pt>0',},
        'm1Eta'                       : {'xVariable': 'm1_eta',                         'xBinning': [500, -2.5, 2.5],        'selection': 'm1_pt>0',},
        'm2Pt'                        : {'xVariable': 'm2_pt',                          'xBinning': [1000, 0, 1000],         'selection': 'm2_pt>0',},
        'm2Eta'                       : {'xVariable': 'm2_eta',                         'xBinning': [500, -2.5, 2.5],        'selection': 'm2_pt>0',},
        'm3Pt'                        : {'xVariable': 'm3_pt',                          'xBinning': [1000, 0, 1000],         'selection': 'm3_pt>0',},
        'm3Eta'                       : {'xVariable': 'm3_eta',                         'xBinning': [500, -2.5, 2.5],        'selection': 'm3_pt>0',},
    }

    
    # setup the reco channels
    projectionParams['ThreeLepton'] = {}
    
    leps = ['e1','e2','e3','m1','m2','m3']
    baseScaleFactor = '*'.join(['genWeight','pileupWeight','triggerEfficiency'])
    scaleFactors = {
        '0e3m' : '*'.join(['{0}_mediumScale'.format(l) for l in ['m1','m2','m3']]),
        '1e2m' : '*'.join(['{0}_mediumScale'.format(l) for l in ['e1','m1','m2']]),
        '2e1m' : '*'.join(['{0}_mediumScale'.format(l) for l in ['e1','e2','m1']]),
        '3e0m' : '*'.join(['{0}_mediumScale'.format(l) for l in ['e1','e2','e3']]),
    }
    
    
    # the default selections
    selectionParams['ThreeLepton'] = {
        '0e3m'   : {'args': ['m3_pt>0'],            'kwargs': {'mcscalefactor': baseScaleFactor + '*' + scaleFactors['0e3m'], 'countOnly': countOnly,}},
        '1e2m'   : {'args': ['e1_pt>0 && m2_pt>0'], 'kwargs': {'mcscalefactor': baseScaleFactor + '*' + scaleFactors['1e2m'], 'countOnly': countOnly,}},
        '2e1m'   : {'args': ['e2_pt>0 && m1_pt>0'], 'kwargs': {'mcscalefactor': baseScaleFactor + '*' + scaleFactors['2e1m'], 'countOnly': countOnly,}},
        '3e0m'   : {'args': ['e3_pt>0'],            'kwargs': {'mcscalefactor': baseScaleFactor + '*' + scaleFactors['3e0m'], 'countOnly': countOnly,}},
    }
    
    
    sampleHistParams['ThreeLepton'] = {}
    sampleProjectionParams['ThreeLepton'] = {}
    sampleSelectionParams['ThreeLepton'] = {}
    
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
    for sample,cut in sampleCuts.iteritems():
        sampleSelectionParams['ThreeLepton'][sample] = deepcopy(selectionParams['ThreeLepton'])
        for sel in selectionParams['ThreeLepton'].keys():
            sampleSelectionParams['ThreeLepton'][sample][sel]['args'][0] += ' && {0}'.format(cut)


    # speacial scales for individual samples
    sampleScales = {
        'ZZTo4L_13TeV_powheg_pythia8'       : 'qqZZkfactor/1.1',
        'ZZTo4L_13TeV-amcatnloFXFX-pythia8' : 'qqZZkfactor/1.1',
    }
    for sample,scale in sampleScales.iteritems():
        sampleSelectionParams['ThreeLepton'][sample] = deepcopy(selectionParams['ThreeLepton'])
        for sel in selectionParams['ThreeLepton'].keys():
            sampleSelectionParams['ThreeLepton'][sample][sel]['kwargs']['mcscalefactor'] = '*'.join([sampleSelectionParams['ThreeLepton'][sample][sel]['kwargs']['mcscalefactor'],scale])

