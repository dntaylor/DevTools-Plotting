from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

promptCut = '{0}_genMatch==1 && {0}_genIsPrompt==1 && {0}_genDeltaR<0.1'
fakeCut = '({0}_genMatch==0 || ({0}_genMatch==1 && {0}_genIsFromHadron && {0}_genDeltaR<0.1))'
eBarrelCut = 'fabs({0}_eta)<1.479'
eEndcapCut = 'fabs({0}_eta)>1.479'

def buildElectron(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['Electron'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'pt'                          : {'xVariable': 'e_pt',                           'xBinning': [2000,0,2000],           },
        'eta'                         : {'xVariable': 'e_eta',                          'xBinning': [600,-3.,3.],            },
    }

    selectionParams['Electron'] = {
        'default/prompt' : {'args': [promptCut.format('e')],                                       'kwargs': {}},
        'default/fake'   : {'args': [fakeCut.format('e')],                                         'kwargs': {}},
        #'barrel/prompt'  : {'args': [' && '.join([promptCut.format('e'),eBarrelCut.format('e')])], 'kwargs': {}},
        #'barrel/fake'    : {'args': [' && '.join([fakeCut.format('e'),eBarrelCut.format('e')])],   'kwargs': {}},
        #'endcap/prompt'  : {'args': [' && '.join([promptCut.format('e'),eEndcapCut.format('e')])], 'kwargs': {}},
        #'edncap/fake'    : {'args': [' && '.join([fakeCut.format('e'),eEndcapCut.format('e')])],   'kwargs': {}},
    }
    
    sels = selectionParams['Electron'].keys()
    idCuts = {
        'cutBasedVeto'   : 'e_cutBasedVeto==1',
        'cutBasedLoose'  : 'e_cutBasedLoose==1',
        'cutBasedMedium' : 'e_cutBasedMedium==1',
        'cutBasedTight'  : 'e_cutBasedTight==1',
        'wwLoose'        : 'e_wwLoose==1',
        'heepV60'        : 'e_heepV60==1',
        'NonTrigWP80'    : 'e_mvaNonTrigWP80==1',
        'NonTrigWP90'    : 'e_mvaNonTrigWP90==1',
        'TrigPre'        : 'e_mvaTrigPre==1',
        'TrigWP80'       : 'e_mvaTrigPre==1 && e_mvaTrigWP80==1',
        'TrigWP90'       : 'e_mvaTrigPre==1 && e_mvaTrigWP90==1',
    }
    for sel in sels:
        for idName in idCuts:
            name = '{0}/{1}'.format(sel,idName)
            selectionParams['Electron'][name] = deepcopy(selectionParams['Electron'][sel])
            args = selectionParams['Electron'][name]['args']
            selectionParams['Electron'][name]['args'][0] = args[0] + ' && ' + idCuts[idName]

