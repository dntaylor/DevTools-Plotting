from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

promptTauCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'
fakeTauCut = '({0}_genMatch==0 || ({0}_genMatch==1 && {0}_genDeltaR>0.1))'


def buildTau(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['Tau'] = {
        'count'                       : {'xVariable': '1',                                   'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'pt'                          : {'xVariable': 't_pt',                                'xBinning': [2000,0,2000],           },
        'eta'                         : {'xVariable': 't_eta',                               'xBinning': [600,-3.,3.],            },
        'isoMVAold'                   : {'xVariable': 't_byIsolationMVArun2v1DBoldDMwLTraw', 'xBinning': [1000,-1.,1.],           },
    }

    selectionParams['Tau'] = {
        'default/prompt' : {'args': [promptTauCut.format('t')], 'kwargs': {}},
        'default/fake'   : {'args': [fakeTauCut.format('t')],   'kwargs': {}},
    }
    
    sels = selectionParams['Tau'].keys()
    againstElectron = {
        'vloose': 't_againstElectronVLooseMVA6==1',
        'loose' : 't_againstElectronLooseMVA6==1',
        'medium': 't_againstElectronMediumMVA6==1',
        'tight' : 't_againstElectronTightMVA6==1',
        'vtight': 't_againstElectronVTightMVA6==1',
    }
    againstMuon = {
        'loose' : 't_againstMuonLoose3==1',
        'tight' : 't_againstMuonTight3==1',
    }
    oldId = 't_decayModeFinding==1'
    oldIsolation = {
        'vvloose': 't_byIsolationMVArun2v1DBoldDMwLTraw>-0.8',
        'vloose' : 't_byVLooseIsolationMVArun2v1DBoldDMwLT==1',
        'loose'  : 't_byLooseIsolationMVArun2v1DBoldDMwLT==1',
        'medium' : 't_byMediumIsolationMVArun2v1DBoldDMwLT==1',
        'tight'  : 't_byTightIsolationMVArun2v1DBoldDMwLT==1',
        'vtight' : 't_byVTightIsolationMVArun2v1DBoldDMwLT==1',
    }
    newId = 't_decayModeFindingNewDMs==1'
    newIsolation = {
        'vloose': 't_byVLooseIsolationMVArun2v1DBnewDMwLT==1',
        'loose' : 't_byLooseIsolationMVArun2v1DBnewDMwLT==1',
        'medium': 't_byMediumIsolationMVArun2v1DBnewDMwLT==1',
        'tight' : 't_byTightIsolationMVArun2v1DBnewDMwLT==1',
        'vtight': 't_byVTightIsolationMVArun2v1DBnewDMwLT==1',
    }
    idCuts = {}
    cutLists = [
        ('vloose','loose','vvloose'),
        ('vloose','loose','vloose'),
        ('vloose','loose','loose'),
        ('vloose','loose','tight'),
        ('vloose','loose','vtight'),
        ('tight','tight','vvloose'),
        ('tight','tight','vloose'),
        ('tight','tight','loose'),
        ('tight','tight','tight'),
        ('tight','tight','vtight'),
    ]
    for cl in cutLists:
        el,mu,iso = cl
        idCuts['old_{0}Electron_{1}Muon_{2}Isolation'.format(el,mu,iso)] = ' && '.join([oldId, againstElectron[el], againstMuon[mu], oldIsolation[iso]])
        #if iso!='vvloose': idCuts['new_{0}Electron_{1}Muon_{2}Isolation'.format(el,mu,iso)] = ' && '.join([newId, againstElectron[el], againstMuon[mu], newIsolation[iso]])
        idCuts['old_{0}Electron_{1}Muon_noIsolation'.format(el,mu)] = ' && '.join([oldId, againstElectron[el], againstMuon[mu]])
        #idCuts['new_{0}Electron_{1}Muon_noIsolation'.format(el,mu)] = ' && '.join([newId, againstElectron[el], againstMuon[mu]])
        if iso!='vtight': continue
        idCuts['old_{0}Electron_noMuon_{1}Isolation'.format(el,iso)] = ' && '.join([oldId, againstElectron[el], oldIsolation[iso]])
        #idCuts['new_{0}Electron_noMuon_{1}Isolation'.format(el,iso)] = ' && '.join([newId, againstElectron[el], newIsolation[iso]])
        idCuts['old_noElectron_{0}Muon_{1}Isolation'.format(el,mu,iso)] = ' && '.join([oldId, againstMuon[mu], oldIsolation[iso]])
        #idCuts['new_noElectron_{0}Muon_{1}Isolation'.format(el,mu,iso)] = ' && '.join([newId, againstMuon[mu], newIsolation[iso]])
    
    for sel in sels:
        for idName in idCuts:
            name = '{0}/{1}'.format(sel,idName)
            selectionParams['Tau'][name] = deepcopy(selectionParams['Tau'][sel])
            args = selectionParams['Tau'][name]['args']
            selectionParams['Tau'][name]['args'][0] = args[0] + ' && ' + idCuts[idName]
    
