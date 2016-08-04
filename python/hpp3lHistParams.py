from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels
from DevTools.Plotter.higgsUtilities import getChannels, getGenChannels, getSelections

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

genCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'

def buildHpp3l(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams,**kwargs):
    shift = kwargs.pop('shift','')
    countOnly = kwargs.pop('countOnly',False)

    histParams['Hpp3l'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],               },
        #'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': '1./pileupWeight'},
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [500, -3.14159, 3.14159],},
        # h++/h--
        'hppMass'                     : {'xVariable': 'hpp_mass',                       'xBinning': [1600, 0, 1600],         },
        'hppPt'                       : {'xVariable': 'hpp_pt',                         'xBinning': [1600, 0, 1600],         },
        #'hppEta'                      : {'xVariable': 'hpp_eta',                        'xBinning': [1000, -5, 5],           },
        'hppDeltaR'                   : {'xVariable': 'hpp_deltaR',                     'xBinning': [500, 0, 5],             },
        'hppLeadingLeptonPt'          : {'xVariable': 'hpp1_pt',                        'xBinning': [1000, 0, 1000],         },
        'hppLeadingLeptonEta'         : {'xVariable': 'hpp1_eta',                       'xBinning': [500, -2.5, 2.5],        },
        'hppSubLeadingLeptonPt'       : {'xVariable': 'hpp2_pt',                        'xBinning': [1000, 0, 1000],         },
        'hppSubLeadingLeptonEta'      : {'xVariable': 'hpp2_eta',                       'xBinning': [500, -2.5, 2.5],        },
        # h-/h+
        'hmMass'                      : {'xVariable': 'hm_mt',                          'xBinning': [1600, 0, 1600],         },
        'hmPt'                        : {'xVariable': 'hm_pt',                          'xBinning': [1600, 0, 1600],         },
        #'hmEta'                       : {'xVariable': 'hm_eta',                         'xBinning': [1000, -5, 5],           },
        'hmLeptonPt'                  : {'xVariable': 'hm1_pt',                         'xBinning': [1000, 0, 1000],         },
        'hmLeptonEta'                 : {'xVariable': 'hm1_eta',                        'xBinning': [500, -2.5, 2.5],        },
        # best z
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [500, 0, 500],           'selection': 'z_mass>0.',},
        'mllMinusMZ'                  : {'xVariable': 'fabs(z_mass-{0})'.format(ZMASS), 'xBinning': [200, 0, 200],           'selection': 'z_mass>0.',},
        'zPt'                         : {'xVariable': 'z_pt',                           'xBinning': [500, 0, 500],           'selection': 'z_mass>0.',},
        #'zEta'                        : {'xVariable': 'z_eta',                          'xBinning': [1000, -5, 5],           'selection': 'z_mass>0.',},
        #'zLeadingLeptonPt'            : {'xVariable': 'z1_pt',                          'xBinning': [1000, 0, 1000],         'selection': 'z_mass>0.',},
        #'zLeadingLeptonEta'           : {'xVariable': 'z1_eta',                         'xBinning': [500, -2.5, 2.5],        'selection': 'z_mass>0.',},
        #'zSubLeadingLeptonPt'         : {'xVariable': 'z2_pt',                          'xBinning': [1000, 0, 1000],         'selection': 'z_mass>0.',},
        #'zSubLeadingLeptonEta'        : {'xVariable': 'z2_eta',                         'xBinning': [500, -2.5, 2.5],        'selection': 'z_mass>0.',},
        # w
        'wMass'                       : {'xVariable': 'w_mt',                           'xBinning': [500, 0, 500],           'selection': 'z_mass>0.',},
        'wPt'                         : {'xVariable': 'w_pt',                           'xBinning': [500, 0, 500],           'selection': 'z_mass>0.',},
        #'wEta'                        : {'xVariable': 'w_eta',                          'xBinning': [1000, -5, 5],           'selection': 'z_mass>0.',},
        #'wLeptonPt'                   : {'xVariable': 'w1_pt',                          'xBinning': [1000, 0, 1000],         'selection': 'z_mass>0.',},
        #'wLeptonEta'                  : {'xVariable': 'w1_eta',                         'xBinning': [500, -2.5, 2.5],        'selection': 'z_mass>0.',},
        # event
        'mass'                        : {'xVariable': '3l_mass',                        'xBinning': [2000, 0, 2000],         },
        'st'                          : {'xVariable': 'hpp1_pt+hpp2_pt+hm1_pt',         'xBinning': [2000, 0, 2000],         },
        'nJets'                       : {'xVariable': 'numJetsTight30',                 'xBinning': [11, -0.5, 10.5],        },
        # gen truth
        #'hppLeadingLeptonGenMatch'    : {'xVariable': 'hpp1_genMatch',                  'xBinning': [2, 0, 2],               },
        #'hppLeadingLeptonGenDeltaR'   : {'xVariable': 'hpp1_genDeltaR',                 'xBinning': [1000, 0, 5],            },
        #'hppSubLeadingLeptonGenMatch' : {'xVariable': 'hpp2_genMatch',                  'xBinning': [2, 0, 2],               },
        #'hpmSubLeadingLeptonGenDeltaR': {'xVariable': 'hpp2_genDeltaR',                 'xBinning': [1000, 0, 5],            },
        #'hmLeptonGenMatch'            : {'xVariable': 'hm1_genMatch',                   'xBinning': [2, 0, 2],               },
        #'hmLeptonGenDeltaR'           : {'xVariable': 'hm1_genDeltaR',                  'xBinning': [1000, 0, 5],            },
    }

    masses = [200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500]
    
    # setup the reco channels
    channels = getChannels('Hpp3l')
    projectionParams['Hpp3l'] = {}
    allChans = []
    for chan in channels:
        projectionParams['Hpp3l'][chan] = channels[chan]
        allChans += channels[chan]
    histParams['Hpp3l'].update(addChannels(deepcopy(histParams['Hpp3l']),'channel',len(allChans)))
    
    leps = ['hpp1','hpp2','hm1']
    hpp3lBaseScaleFactor = '*'.join(['genWeight','pileupWeight','triggerEfficiency'])
    if shift=='trigUp': hpp4lBaseScaleFactor = '*'.join(['genWeight','pileupWeight','triggerEfficiencyUp'])
    if shift=='trigDown': hpp4lBaseScaleFactor = '*'.join(['genWeight','pileupWeight','triggerEfficiencyDown'])
    if shift=='puUp': hpp4lBaseScaleFactor = '*'.join(['genWeight','pileupWeightUp','triggerEfficiency'])
    if shift=='puDown': hpp4lBaseScaleFactor = '*'.join(['genWeight','pileupWeightDown','triggerEfficiency'])

    # setup base selections
    hpp3lBaseCut = '1'
    hpp3lLowMassControl = '{0} && hpp_mass<100'.format(hpp3lBaseCut)
    hpp3lScaleFactor = '*'.join(['{0}_mediumScale'.format(lep) for lep in leps]+[hpp3lBaseScaleFactor])
    if shift=='lepUp': hpp3lScaleFactor = '*'.join(['{0}_mediumScaleUp'.format(lep) for lep in leps]+[hpp3lBaseScaleFactor])
    if shift=='lepDown': hpp3lScaleFactor = '*'.join(['{0}_mediumScaleDown'.format(lep) for lep in leps]+[hpp3lBaseScaleFactor])
    
    # setup fakerate selections
    scaleMap = {
        'P' : '{0}_looseScale',
        'F' : '{0}_mediumScale',
    }
    if shift=='lepUp':
        scaleMap = {
            'P' : '{0}_looseScaleUp',
            'F' : '{0}_mediumScaleUp',
        }
    if shift=='lepDown':
        scaleMap = {
            'P' : '{0}_looseScaleDown',
            'F' : '{0}_mediumScaleDown',
        }

    fakeVal = '{0}_mediumFakeRate'
    if shift=='fakeUp': fakeVal = '{0}_mediumFakeRateUp'
    if shift=='fakeDown': fakeVal = '{0}_mediumFakeRateDown'
    
    hpp3lMCCut = ' && '.join([genCut.format(l) for l in leps])
    
    # build the cuts for each fake region
    hpp3lScaleFactorMap = {}
    hpp3lFakeScaleFactorMap = {}
    hpp3lCutMap = {}
    hpp3lFakeRegions = [''.join(x) for x in product('PF',repeat=3)]
    fakeModes = {
        0 : [],
        1 : [],
        2 : [],
        3 : [],
    }
    for region in hpp3lFakeRegions:
        fakeModes[region.count('F')] += [region]
        hpp3lScaleFactorMap[region] = '*'.join([scaleMap[region[x]].format(leps[x]) for x in range(3)])
        hpp3lFakeScaleFactorMap[region] = '*'.join(['({0}/(1-{0}))'.format(fakeVal.format(leps[x])) for x in range(3) if region[x]=='F'] + ['-1' if region.count('F')%2==0 and region.count('F')>0 else '1'])
        hpp3lCutMap[region] = '(' + ' && '.join(['{0}=={1}'.format('{0}_passMedium'.format(leps[x]),1 if region[x]=='P' else 0) for x in range(3)]) + ')'
    
    
    # the default selections
    selectionParams['Hpp3l'] = {
        'default'   : {'args': [hpp3lBaseCut + ' && ' + hpp3lCutMap['PPP']],                          'kwargs': {'mcscalefactor': hpp3lScaleFactor, 'countOnly': countOnly,}},
        'lowmass'   : {'args': [hpp3lLowMassControl + ' && ' + hpp3lCutMap['PPP']],                   'kwargs': {'mcscalefactor': hpp3lScaleFactor, 'countOnly': countOnly,}},
    }
    
    # setup working points
    cuts3l = sorted(['st','zveto','dr','mass','met'])
    for mass in masses:
        for hppTaus in range(3):
            # old
            #sideband = getSelections('Hpp3l',mass,nTaus=[hppTaus,0],cuts=[],invcuts=['mass'],mode='old')
            #massWindow = getSelections('Hpp3l',mass,nTaus=[hppTaus,0],cuts=['mass'],mode='old')
            #allSideband = getSelections('Hpp3l',mass,nTaus=[hppTaus,0],cuts=['st','zveto','met','dr'],invcuts=['mass'],mode='old')
            #allMassWindow = getSelections('Hpp3l',mass,nTaus=[hppTaus,0],cuts=['st','zveto','met','dr','mass'],mode='old')
            #selectionParams['Hpp3l']['old/sideband/{0}/hpp{1}'.format(mass,hppTaus,)] =      {'args': [hpp3lCutMap['PPP'] + ' && ' + sideband],      'kwargs': {'mcscalefactor': hpp3lScaleFactor, 'countOnly': True}}
            #selectionParams['Hpp3l']['old/massWindow/{0}/hpp{1}'.format(mass,hppTaus,)] =    {'args': [hpp3lCutMap['PPP'] + ' && ' + massWindow],    'kwargs': {'mcscalefactor': hpp3lScaleFactor, 'countOnly': True}}
            #selectionParams['Hpp3l']['old/allSideband/{0}/hpp{1}'.format(mass,hppTaus,)] =   {'args': [hpp3lCutMap['PPP'] + ' && ' + allSideband],   'kwargs': {'mcscalefactor': hpp3lScaleFactor, 'countOnly': True}}
            #selectionParams['Hpp3l']['old/allMassWindow/{0}/hpp{1}'.format(mass,hppTaus,)] = {'args': [hpp3lCutMap['PPP'] + ' && ' + allMassWindow], 'kwargs': {'mcscalefactor': hpp3lScaleFactor, 'countOnly': True}}
            # new
            sideband = getSelections('Hpp3l',mass,nTaus=[hppTaus,0],cuts=[],invcuts=['mass'],mode='new')
            massWindow = getSelections('Hpp3l',mass,nTaus=[hppTaus,0],cuts=['mass'],mode='new')
            allSideband = getSelections('Hpp3l',mass,nTaus=[hppTaus,0],cuts=['st','zveto','met','dr'],invcuts=['mass'],mode='new')
            allMassWindow = getSelections('Hpp3l',mass,nTaus=[hppTaus,0],cuts=['st','zveto','met','dr','mass'],mode='new')
            selectionParams['Hpp3l']['new/sideband/{0}/hpp{1}'.format(mass,hppTaus,)] =      {'args': [hpp3lCutMap['PPP'] + ' && ' + sideband],      'kwargs': {'mcscalefactor': hpp3lScaleFactor, 'countOnly': True}}
            selectionParams['Hpp3l']['new/massWindow/{0}/hpp{1}'.format(mass,hppTaus,)] =    {'args': [hpp3lCutMap['PPP'] + ' && ' + massWindow],    'kwargs': {'mcscalefactor': hpp3lScaleFactor, 'countOnly': True}}
            selectionParams['Hpp3l']['new/allSideband/{0}/hpp{1}'.format(mass,hppTaus,)] =   {'args': [hpp3lCutMap['PPP'] + ' && ' + allSideband],   'kwargs': {'mcscalefactor': hpp3lScaleFactor, 'countOnly': True}}
            selectionParams['Hpp3l']['new/allMassWindow/{0}/hpp{1}'.format(mass,hppTaus,)] = {'args': [hpp3lCutMap['PPP'] + ' && ' + allMassWindow], 'kwargs': {'mcscalefactor': hpp3lScaleFactor, 'countOnly': True}}
    
    # fake regions via modes
    # TODO: change to only add for 3 real leptons and data
    for nf in range(4):
        name = '{0}P{1}F'.format(3-nf,nf)
        name_regular = '{0}P{1}F_regular'.format(3-nf,nf)
        regionCut = '(' + ' || '.join([hpp3lCutMap[reg] for reg in fakeModes[nf]]) + ')'
        regionMCScaleFactor = '*'.join(['({0} ? {1}*{2}*{3}*{4} : 1)'.format(hpp3lCutMap[reg],hpp3lScaleFactorMap[reg],hpp3lFakeScaleFactorMap[reg],hpp3lBaseScaleFactor,'1' if reg=='PPP' else '-1') for reg in fakeModes[nf]])
        regionMCScaleFactor_regular = '*'.join(['({0} ? {1}*{2} : 1)'.format(hpp3lCutMap[reg],hpp3lScaleFactorMap[reg],hpp3lBaseScaleFactor) for reg in fakeModes[nf]])
        regionDataScaleFactor = '*'.join(['({0} ? {1} : 1)'.format(hpp3lCutMap[reg],hpp3lFakeScaleFactorMap[reg]) for reg in fakeModes[nf]])
        # fake scaled
        selectionParams['Hpp3l'][name] = {
            'args': [hpp3lBaseCut + ' && ' + regionCut],
            'kwargs': {
                'mccut': hpp3lMCCut,
                'mcscalefactor': regionMCScaleFactor,
                'datascalefactor': regionDataScaleFactor,
                'countOnly': countOnly,
            }
        }
        selectionParams['Hpp3l']['{0}/lowmass'.format(name)] = {
            'args': [hpp3lLowMassControl + ' && ' + regionCut],
            'kwargs': {
                'mccut': hpp3lMCCut,
                'mcscalefactor': regionMCScaleFactor,
                'datascalefactor': regionDataScaleFactor,
                'countOnly': countOnly,
            }
        }
        # regular for validation
        selectionParams['Hpp3l'][name_regular] = {
            'args': [hpp3lBaseCut + ' && ' + regionCut],
            'kwargs': {
                'mcscalefactor': regionMCScaleFactor_regular,
                'countOnly': countOnly,
            }
        }
        selectionParams['Hpp3l']['{0}/lowmass'.format(name_regular)] = {
            'args': [hpp3lLowMassControl + ' && ' + regionCut],
            'kwargs': {
                'mcscalefactor': regionMCScaleFactor_regular,
                'countOnly': countOnly,
            }
        }
        # setup working points
        cuts3l = sorted(['st','zveto','dr','mass','met'])
        for mass in masses:
            for hppTaus in range(3):
                # old
                #sideband = getSelections('Hpp3l',mass,nTaus=[hppTaus,0],cuts=[],invcuts=['mass'],mode='old')
                #massWindow = getSelections('Hpp3l',mass,nTaus=[hppTaus,0],cuts=['mass'],mode='old')
                #allSideband = getSelections('Hpp3l',mass,nTaus=[hppTaus,0],cuts=['st','zveto','met','dr'],invcuts=['mass'],mode='old')
                #allMassWindow = getSelections('Hpp3l',mass,nTaus=[hppTaus,0],cuts=['st','zveto','met','dr','mass'],mode='old')
                #selectionParams['Hpp3l']['old/sideband/{0}/hpp{1}'.format(mass,hppTaus,)] =      {'args': [hpp3lCutMap['PPP'] + ' && ' + sideband],      'kwargs': {'mcscalefactor': hpp3lScaleFactor, 'countOnly': True}}
                #selectionParams['Hpp3l']['old/massWindow/{0}/hpp{1}'.format(mass,hppTaus,)] =    {'args': [hpp3lCutMap['PPP'] + ' && ' + massWindow],    'kwargs': {'mcscalefactor': hpp3lScaleFactor, 'countOnly': True}}
                #selectionParams['Hpp3l']['old/allSideband/{0}/hpp{1}'.format(mass,hppTaus,)] =   {'args': [hpp3lCutMap['PPP'] + ' && ' + allSideband],   'kwargs': {'mcscalefactor': hpp3lScaleFactor, 'countOnly': True}}
                #selectionParams['Hpp3l']['old/allMassWindow/{0}/hpp{1}'.format(mass,hppTaus,)] = {'args': [hpp3lCutMap['PPP'] + ' && ' + allMassWindow], 'kwargs': {'mcscalefactor': hpp3lScaleFactor, 'countOnly': True}}
                # new
                sideband = getSelections('Hpp3l',mass,nTaus=[hppTaus,0],cuts=[],invcuts=['mass'],mode='new')
                massWindow = getSelections('Hpp3l',mass,nTaus=[hppTaus,0],cuts=['mass'],mode='new')
                allSideband = getSelections('Hpp3l',mass,nTaus=[hppTaus,0],cuts=['st','zveto','met','dr'],invcuts=['mass'],mode='new')
                allMassWindow = getSelections('Hpp3l',mass,nTaus=[hppTaus,0],cuts=['st','zveto','met','dr','mass'],mode='new')
                selectionParams['Hpp3l']['{2}/new/sideband/{0}/hpp{1}'.format(mass,hppTaus,name)] =      {
                    'args': [hpp3lCutMap['PPP'] + ' && ' + sideband],      
                    'kwargs': {
                        'mcscalefactor': hpp3lScaleFactor, 
                        'countOnly': True,
                    },
                }
                selectionParams['Hpp3l']['{2}/new/massWindow/{0}/hpp{1}'.format(mass,hppTaus,name)] =    {
                    'args': [hpp3lCutMap['PPP'] + ' && ' + massWindow],    
                    'kwargs': {
                        'mcscalefactor': hpp3lScaleFactor, 
                        'countOnly': True,
                    },
                }
                selectionParams['Hpp3l']['{2}/new/allSideband/{0}/hpp{1}'.format(mass,hppTaus,name)] =   {
                    'args': [hpp3lCutMap['PPP'] + ' && ' + allSideband],   
                    'kwargs': {
                        'mcscalefactor': hpp3lScaleFactor, 
                        'countOnly': True,
                    },
                }
                selectionParams['Hpp3l']['{2}/new/allMassWindow/{0}/hpp{1}'.format(mass,hppTaus,name)] = {
                    'args': [hpp3lCutMap['PPP'] + ' && ' + allMassWindow], 
                    'kwargs': {
                        'mcscalefactor': hpp3lScaleFactor, 
                        'countOnly': True,
                    },
                }

    # setup gen channel selections
    genChans = getGenChannels('Hpp3l')
    genChannelsPP = genChans['PP']
    genChannelsAP = genChans['AP']
    
    sampleHistParams['Hpp3l'] = {}
    sampleProjectionParams['Hpp3l'] = {}
    sampleSelectionParams['Hpp3l'] = {}
    for mass in masses:
        # pp
        sampleName = 'HPlusPlusHMinusMinusHTo4L_M-{0}_13TeV-pythia8'.format(mass)
        if version=='80X': sampleName = 'HPlusPlusHMinusMinusHTo4L_M-{0}_TuneCUETP8M1_13TeV_pythia8'.format(mass)
        sampleHistParams['Hpp3l'][sampleName] = addChannels(deepcopy(histParams['Hpp3l']),'genChannel',len(genChannelsPP))
        sampleProjectionParams['Hpp3l'][sampleName] = {}
        for genChan in genChannelsPP:
            sampleProjectionParams['Hpp3l'][sampleName]['gen_{0}'.format(genChan)] = [genChan]
        #sampleSelectionParams['Hpp3l'][sampleName] = deepcopy(selectionParams['Hpp3l'])
        #for sel in selectionParams['Hpp3l']:
        #    if sel.split('/')[0] in ['2P1F','1P2F','0P3F']:
        #        sampleSelectionParams['Hpp3l'][sampleName][sel] = {}
        #    if str(mass) in sel.split('/'):
        #        sampleSelectionParams['Hpp3l'][sampleName][sel] = {}
        # ap
        sampleName = 'HPlusPlusHMinusHTo3L_M-{0}_TuneCUETP8M1_13TeV_calchep-pythia8'.format(mass)
        sampleHistParams['Hpp3l'][sampleName] = addChannels(deepcopy(histParams['Hpp3l']),'genChannel',len(genChannelsAP))
        sampleProjectionParams['Hpp3l'][sampleName] = {}
        for genChan in genChannelsAP:
            sampleProjectionParams['Hpp3l'][sampleName]['gen_{0}'.format(genChan)] = [genChan]
        #sampleSelectionParams['Hpp3l'][sampleName] = deepcopy(selectionParams['Hpp3l'])
        #for sel in selectionParams['Hpp3l']:
        #    if sel.split('/')[0] in ['2P1F','1P2F','0P3F']:
        #        sampleSelectionParams['Hpp3l'][sampleName][sel] = {}
        #    if str(mass) in sel.split('/'):
        #        sampleSelectionParams['Hpp3l'][sampleName][sel] = {}
    
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
        sampleSelectionParams['Hpp3l'][sample] = deepcopy(selectionParams['Hpp3l'])
        for sel in selectionParams['Hpp3l'].keys():
            sampleSelectionParams['Hpp3l'][sample][sel]['args'][0] += ' && {0}'.format(cut)



