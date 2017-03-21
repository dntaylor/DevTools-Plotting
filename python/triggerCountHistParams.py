from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels, getLumi, getRunRange

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

def buildTriggerCount(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['TriggerCount'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
    }

    triggers = [
        'pass_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ',
        'pass_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ',
        'pass_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ',
        'pass_IsoMu24',
        'pass_IsoTkMu24',
        'pass_Ele27_WPTight_Gsf',
        'pass_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL',
        'pass_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL',
        'pass_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ',
        'pass_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ',
        'pass_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg',
    ]
    for trigger in triggers:
        histParams['TriggerCount'][trigger] = {'xVariable': trigger, 'xBinning': [2,0,2], }

    selectionParams['TriggerCount'] = {
        'all'      : {'args': ['1'],                   'kwargs': {'mcscalefactor': '1', }},
    }
    
    intLumi = getLumi()
    for r in ['B','C','D','E','F','G','H']:
        run = 'Run2016{0}'.format(r)
        runLumi = getLumi(run=run)
        mcscale = '{0}/{1}'.format(runLumi,intLumi)
        runRange = getRunRange(run=run)
        datacut = 'run>={0} && run<={1}'.format(*runRange)
        selectionParams['TriggerCount'][run] = {'args': [datacut], 'kwargs': {'mcscalefactor': mcscale}}

