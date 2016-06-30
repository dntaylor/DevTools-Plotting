from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

promptCut = '{0}_genMatch==1 && {0}_genIsPrompt==1 && {0}_genDeltaR<0.1'
fakeCut = '({0}_genMatch==0 || ({0}_genMatch==1 && {0}_genIsFromHadron && {0}_genDeltaR<0.1))'

def buildMuon(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['Muon'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'pt'                          : {'xVariable': 'm_pt',                           'xBinning': [2000,0,2000],           },
        'eta'                         : {'xVariable': 'm_eta',                          'xBinning': [600,-3.,3.],            },
    }

    selectionParams['Muon'] = {
        'default/prompt' : {'args': [promptCut.format('m')], 'kwargs': {}},
        'default/fake'   : {'args': [fakeCut.format('m')],   'kwargs': {}},
    }
    
    sels = selectionParams['Muon'].keys()
    idCuts = {
        'isLooseMuon_looseIso'  : 'm_isLooseMuon==1 && m_isolation<0.25',
        'isMediumMuon_looseIso' : 'm_isMediumMuon==1 && m_isolation<0.25',
        'isMediumMuon_tightIso' : 'm_isMediumMuon==1 && m_isolation<0.15',
        'isTightMuon_tightIso'  : 'm_isTightMuon==1 && m_isolation<0.15',
        'isHighPtMuon_tightIso' : 'm_isHighPtMuon==1 && m_isolation<0.15',
        'wzLooseMuon'           : 'm_isMediumMuon==1 && m_trackRelIso<0.4 && m_isolation<0.4',
        'wzMediumMuon'          : 'm_isMediumMuon==1 && m_trackRelIso<0.4 && m_isolation<0.15 && m_dz<0.1 && (m_pt<20 ? m_dxy<0.01 : m_dxy<0.02)',
    }
    for sel in sels:
        for idName in idCuts:
            name = '{0}/{1}'.format(sel,idName)
            selectionParams['Muon'][name] = deepcopy(selectionParams['Muon'][sel])
            args = selectionParams['Muon'][name]['args']
            selectionParams['Muon'][name]['args'][0] = args[0] + ' && ' + idCuts[idName]

