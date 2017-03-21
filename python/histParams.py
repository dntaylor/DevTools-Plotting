# histParams.py
'''
A map of histogram params.
'''
from copy import deepcopy

from electronHistParams import buildElectron
from muonHistParams import buildMuon
from tauHistParams import buildTau
from wTauFakeRateHistParams import buildWTauFakeRate
from wFakeRateHistParams import buildWFakeRate
from zFakeRateHistParams import buildZFakeRate
from dijetFakeRateHistParams import buildDijetFakeRate
from tauChargeHistParams import buildTauCharge
from chargeHistParams import buildCharge
from dyHistParams import buildDY
from wzHistParams import buildWZ
from zzHistParams import buildZZ
from hpp4lHistParams import buildHpp4l
from hpp3lHistParams import buildHpp3l
from threeLeptonHistParams import buildThreeLepton
from triggerCountHistParams import buildTriggerCount

cachedParams = {}

def buildHistParams(analysis,**kwargs):

    key = analysis
    for arg,val in kwargs.iteritems():
        key += str(arg)+str(val)
    if key in cachedParams: return cachedParams[key]

    #############
    ### hists ###
    #############
    histParams = {}
    sampleHistParams = {}
    
    ###################
    ### Projections ###
    ###################
    projectionParams = {
        'common' : {
            'all' : [], # empty list defaults to sum all channels
        },
    }
    sampleProjectionParams = {}
    
    ##################
    ### selections ###
    ##################
    selectionParams = {}
    sampleSelectionParams = {}
    
    ############################
    ### Build all parameters ###
    ############################
    if analysis=='Electron':      buildElectron(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams)
    if analysis=='Muon':          buildMuon(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams)
    if analysis=='Tau':           buildTau(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams)
    if analysis=='WTauFakeRate':  buildWTauFakeRate(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams)
    if analysis=='WFakeRate':     buildWFakeRate(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams)
    if analysis=='ZFakeRate':     buildZFakeRate(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams)
    if analysis=='DijetFakeRate': buildDijetFakeRate(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams)
    if analysis=='TauCharge':     buildTauCharge(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams)
    if analysis=='Charge':        buildCharge(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams)
    if analysis=='DY':            buildDY(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams)
    if analysis=='WZ':            buildWZ(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams)
    if analysis=='ZZ':            buildZZ(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams)
    if analysis=='Hpp4l':         buildHpp4l(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams,**kwargs)
    if analysis=='Hpp3l':         buildHpp3l(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams,**kwargs)
    if analysis=='ThreeLepton':   buildThreeLepton(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams,**kwargs)
    if analysis=='TriggerCount':  buildTriggerCount(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams)

    cachedParams[key] = (selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams)
    return cachedParams[key]


#############################
### functions to retrieve ###
#############################
def getHistParams(analysis,sample='',**kwargs):
    selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams = buildHistParams(analysis,**kwargs)
    params = {}
    if analysis in histParams:
        params.update(histParams[analysis])
    if analysis in sampleHistParams:
        if sample in sampleHistParams[analysis]:
            params.update(sampleHistParams[analysis][sample])
    return params

def getHistSelections(analysis,sample='',**kwargs):
    selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams = buildHistParams(analysis,**kwargs)
    params = {}
    if analysis in selectionParams:
        params.update(selectionParams[analysis])
    if analysis in sampleSelectionParams:
        if sample in sampleSelectionParams[analysis]:
            params.update(sampleSelectionParams[analysis][sample])
    return params

def getProjectionParams(analysis,sample='',**kwargs):
    selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams = buildHistParams(analysis,**kwargs)
    params = deepcopy(projectionParams['common'])
    if analysis in projectionParams:
        params.update(projectionParams[analysis])
    if analysis in sampleProjectionParams:
        if sample in sampleProjectionParams[analysis]:
            params.update(sampleProjectionParams[analysis][sample])
    return params
