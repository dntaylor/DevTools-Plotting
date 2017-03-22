from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels, getLumi, getRunRange

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

genCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'

def buildWFakeRate(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['WFakeRate'] = {
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
        # l
        'wlMt'                        : {'xVariable': 'wl_mt',                          'xBinning': [500, 0, 500],           },
        'wlPt'                        : {'xVariable': 'wl_pt',                          'xBinning': [500, 0, 500],           },
        'lPt'                         : {'xVariable': 'l_pt',                           'xBinning': [500, 0, 500],           },
        'lEta'                        : {'xVariable': 'l_eta',                          'xBinning': [500, -2.5, 2.5],        },
        # m
        'wmMt'                        : {'xVariable': 'wm_mt',                          'xBinning': [500, 0, 500],           },
        'wmPt'                        : {'xVariable': 'wm_pt',                          'xBinning': [500, 0, 500],           },
        'mPt'                         : {'xVariable': 'm_pt',                           'xBinning': [500, 0, 500],           },
        'mEta'                        : {'xVariable': 'm_eta',                          'xBinning': [500, -2.5, 2.5],        },
    }

    #intLumi = getLumi()
    #for r in ['B','C','D','E','F','G','H']:
    #    run = 'Run2016{0}'.format(r)
    #    runLumi = getLumi(run=run)
    #    mcscale = '{0}/{1}'.format(runLumi,intLumi)
    #    runRange = getRunRange(run=run)
    #    datacut = 'run>={0} && run<={1}'.format(*runRange)
    #    histParams['WFakeRate']['wmMt_{0}'.format(run)] = {'xVariable': 'wm_mt', 'xBinning': [500,0,500], 'datacut': datacut, 'mcscale': mcscale}

    # setup the reco channels
    #channels = ['me','mm']
    channels = ['me','mm','mt']
    projectionParams['WFakeRate'] = {}
    for chan in channels:
        projectionParams['WFakeRate'][chan] = [chan]
    histParams['WFakeRate'].update(addChannels(deepcopy(histParams['WFakeRate']),'channel',len(channels)))

    frBaseCut = 'm_eta<2.1 && z_deltaR>0.02 && m_pt>25. && z_mass>12'
    frBaseCutLoose = '{0}'.format(frBaseCut)
    frBaseCutMedium = '{0} && l_passMedium==1'.format(frBaseCut)
    frBaseCutTight = '{0} && l_passTight==1'.format(frBaseCut)
    frScaleFactorLoose = 'm_tightScale*l_looseScale*genWeight*pileupWeight*triggerEfficiency'
    frScaleFactorMedium = 'm_tightScale*l_mediumScale*genWeight*pileupWeight*triggerEfficiency'
    frScaleFactorTight = 'm_tightScale*l_tightScale*genWeight*pileupWeight*triggerEfficiency'
    selectionParams['WFakeRate'] = {
        'loose'      : {'args': [frBaseCutLoose],                   'kwargs': {'mcscalefactor': frScaleFactorLoose, }},
        'medium'     : {'args': [frBaseCutMedium],                  'kwargs': {'mcscalefactor': frScaleFactorMedium,}},
        'tight'      : {'args': [frBaseCutTight],                   'kwargs': {'mcscalefactor': frScaleFactorTight, }},
    }
    
    subsels = {
        'SS'     : 'l_charge==m_charge',
        #'ZVeto'  : '(z_mass<50 || z_mass>120)',
        'ZVeto'  : '(z_mass<75 || z_mass>105)',
        'WMt'    : 'wm_mt>60. && met_pt>30.',
        #'full'   : '(z_mass<50 || z_mass>120) && wm_mt>60. && met_pt>30.  && l_charge==m_charge',
        'full'   : '(z_mass<75 || z_mass>105) && wm_mt>60. && met_pt>30.  && l_charge==m_charge',
    }
    
    for sel in ['loose','medium','tight']:
        for sub in subsels:
            name = '{0}/{1}'.format(sel,sub)
            selectionParams['WFakeRate'][name] = deepcopy(selectionParams['WFakeRate'][sel])
            args = selectionParams['WFakeRate'][name]['args']
            selectionParams['WFakeRate'][name]['args'][0] = ' && '.join([args[0],subsels[sub]])
    

    # special selections for samples
    # bins for LO: 0, 1, 2, 3, 4 bins (0 includes 5+)
    sampleCuts = {
        'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'  : '(numGenJets==0 || numGenJets>4)',
        'DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : 'numGenJets==1',
        'DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : 'numGenJets==2',
        'DY3JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : 'numGenJets==3',
        'DY4JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : 'numGenJets==4',
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
    sampleSelectionParams['WFakeRate'] = {}
    for sample,cut in sampleCuts.iteritems():
        sampleSelectionParams['WFakeRate'][sample] = deepcopy(selectionParams['WFakeRate'])
        for sel in selectionParams['WFakeRate'].keys():
            sampleSelectionParams['WFakeRate'][sample][sel]['args'][0] += ' && {0}'.format(cut)
