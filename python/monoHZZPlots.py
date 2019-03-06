import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.Plotter import Plotter
from DevTools.Utilities.utilities import ZMASS, getCMSSWVersion
from copy import deepcopy
import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

version = getCMSSWVersion()

blind = True
doMC = False
doRegions = True
doDatadriven = True
do3P1F = True

plotter = Plotter('MonoHZZ',new=True)

#########################
### Define categories ###
#########################

sigMap = {
    'ZX'  : [
            'DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            'DYJetsToLL_M-10to50_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            'ttWJets_TuneCP5_13TeV_madgraphMLM_pythia8',
            'ttZJets_TuneCP5_13TeV_madgraphMLM_pythia8',
            'TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            'WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8',
            'WWZ_4F_TuneCP5_13TeV-amcatnlo-pythia8',
            'WZG_TuneCP5_13TeV-amcatnlo-pythia8',
            'WZZ_TuneCP5_13TeV-amcatnlo-pythia8',
            'ZZZ_TuneCP5_13TeV-amcatnlo-pythia8',
            'WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            #'WZTo3LNu_13TeV-powheg-pythia8',
            'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            'WWTo2L2Nu_NNPDF31_TuneCP5_13TeV-powheg-pythia8',
            ],
    'Z'   : [
            'DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            'DYJetsToLL_M-10to50_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            ],
    'TT'  : [
            #'TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
            #'TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8',
            #'TT_DiLept_TuneCP5_13TeV-amcatnlo-pythia8',
            'TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            ],
    'WW' : [
            'WWTo2L2Nu_NNPDF31_TuneCP5_13TeV-powheg-pythia8',
            ],
    'WZ' : [
            'WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            #'WZTo3LNu_13TeV-powheg-pythia8',
            'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            ],
    'ZZ' : [
            'ZZTo4L_13TeV_powheg_pythia8',
            'ZZTo2L2Nu_13TeV_powheg_pythia8',
            #'ZZTo2L2Q_13TeV_powheg_pythia8',
            'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            'GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo2e2tau_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8',
            ],
    'qqZZ' : [
            'ZZTo4L_13TeV_powheg_pythia8',
            'ZZTo2L2Nu_13TeV_powheg_pythia8',
            #'ZZTo2L2Q_13TeV_powheg_pythia8',
            'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            ],
    'ggZZ' : [
            'GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo2e2tau_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8',
            ],
    'TTV' : [
            'ttWJets_TuneCP5_13TeV_madgraphMLM_pythia8',
            'ttZJets_TuneCP5_13TeV_madgraphMLM_pythia8',
            ],
    'VVV' : [
            'WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8',
            'WWZ_4F_TuneCP5_13TeV-amcatnlo-pythia8',
            'WZG_TuneCP5_13TeV-amcatnlo-pythia8',
            'WZZ_TuneCP5_13TeV-amcatnlo-pythia8',
            'ZZZ_TuneCP5_13TeV-amcatnlo-pythia8',
            ],
    'H'   : [
            'GluGluHToZZTo4L_M125_13TeV_powheg2_JHUGenV7011_pythia8',
            'VBF_HToZZTo4L_M125_13TeV_powheg2_JHUGenV7011_pythia8',
            'WminusH_HToZZTo4L_M125_13TeV_powheg2-minlo-HWJ_JHUGenV7011_pythia8',
            'WplusH_HToZZTo4L_M125_13TeV_powheg2-minlo-HWJ_JHUGenV7011_pythia8',
            'ttH_HToZZ_4LFilter_M125_13TeV_powheg2_JHUGenV7011_pythia8',
            'ZH_HToZZ_4LFilter_M125_13TeV_powheg2-minlo-HZJ_JHUGenV7011_pythia8',
            ],
    'data' : [
            'DoubleMuon',
            'DoubleEG',
            'MuonEG',
            'SingleMuon',
            'SingleElectron',
            ],
}

samples = ['ggZZ','qqZZ','H']
samples3P1F = ['WZ','ggZZ','qqZZ','H']
allsamples = ['TT','TTV','Z','WZ','VVV','ggZZ','qqZZ','H']
#allsamples = ['ZX','ggZZ','qqZZ','H']
ddsamples = ['data'] + samples
sigMap['datadriven'] = []
for s in ddsamples: sigMap['datadriven'] += sigMap[s]

selections = ['default','4P0F','CR_SS','3P1F','2P2F']
regions = ['']
if doRegions: regions += ['hzz4l','z4l','zz4l']

channels = ['eeee','eemm','mmmm']
channelMap = {'eeee': ['eeee'], 'eemm': ['eemm','mmee'], 'mmmm': ['mmmm']}

########################
### plot definitions ###
########################
plots = {
    # h
    'hMass'                 : {'xaxis': 'm_{4l} (GeV)', 'yaxis': 'Events / 2 GeV', 'numcol': 1, 'lumipos': 11, 'legendpos':23, 'rebin': range(70,172,2),},# 'logx': True,},
    # z cand
    'z1Mass'                : {'xaxis': 'm_{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 2 GeV', 'rebin': range(40,122,2), 'numcol': 1, 'legendpos':13,},# 'yscale': 1.5,},
    'z2Mass'                : {'xaxis': 'm_{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 2 GeV', 'rebin': range(12,122,2), 'numcol': 1, 'legendpos':13,},# 'yscale': 1.5,},
    # event
    #'numVertices'           : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': range(0,300,5), 'numcol': 1, 'legendpos':34,  'logy': True, 'overflow': True, 'ymin': 1e-2,},
}

alt_plots = {
    'hMass' : {
        'hMass_full': {'yaxis': 'Events / 3 GeV', 'rebin': range(72,1002,3), 'logx': True,},
    },
}

blind_cust = {
    'hMass' : {'blinder': [116,130],},
    'z2Mass': {'blinder': [12,60],},
    'met'   : {'blinder': [50,300],},
}


###############
### Helpers ###
###############
def plotChannels(plotter,plotname,savename,**kwargs):
    kwargs = deepcopy(kwargs)
    plotter.plot(plotname,savename,**kwargs)
    if isinstance(plotname,basestring): plotname = [plotname]
    savesplit = savename.split('/')
    for chan in channels:
        if isinstance(plotname,dict):
            plotnames = {}
            for s in plotname:
                plotnames[s] = []
                for p in plotname[s]:
                    ps = p.split('/')
                    plotnames[s] += ['/'.join(ps[:-1]+[c]+[ps[-1]]) for c in channelMap[chan]]
        else:
            plotnames = []
            for p in plotname:
                ps = p.split('/')
                plotnames += ['/'.join(ps[:-1]+[c]+[ps[-1]]) for c in channelMap[chan]]
        savename = '/'.join(savesplit[:-1]+[chan]+[savesplit[-1]])
        plotter.plot(plotnames,savename,**kwargs)

def getDatadrivenPlot(*plotnames):
    histMap = {}
    for s in samples + ['data','ZX']: histMap[s] = []
    for plot in plotnames:
        plotdirs = plot.split('/')
        for s in samples + ['data']: histMap[s] += ['/'.join(['4P0F']+plotdirs)]
        histMap['ZX'] += ['/'.join(['for4P0F',reg]+plotdirs) for reg in ['3P1F','2P2F']]
    return histMap

def get3P1FPlot(*plotnames):
    histMap = {}
    for s in samples3P1F + ['data','ZX']: histMap[s] = []
    for plot in plotnames:
        plotdirs = plot.split('/')
        for s in samples3P1F + ['data']: histMap[s] += ['/'.join(['3P1F']+plotdirs)]
        histMap['ZX'] += ['/'.join(['for3P1F','2P2F']+plotdirs)]
    return histMap

############################
### MC based BG estimate ###
############################
if doMC:
    for sel in selections:
        for region in regions:
            plotter.clearHistograms()
    
            thisblind = blind and sel in ['4P0F'] and region in ['','hzz4l']
    
            for s in ['ZX']+samples:
                plotter.addHistogramToStack(s,sigMap[s])
            
            if not thisblind: plotter.addHistogram('data',sigMap['data'])
    
            for plot in plots:
                kwargs = deepcopy(plots[plot])
                plotname = '{}/{}/{}'.format(sel,region,plot) if region else '{}/{}'.format(sel,plot)
                savename = '{}/{}/mc/{}'.format(sel,region,plot) if region else '{}/mc/{}'.format(sel,plot)
                plotChannels(plotter,plotname,savename,**kwargs)
            
                for alt in alt_plots.get(plot,[]):
                    kwargs = deepcopy(plots[plot])
                    kwargs.update(alt_plots[plot][alt])
                    savename = '{}/{}/mc/{}'.format(sel,region,alt) if region else '{}/mc/{}'.format(sel,alt)
                    plotChannels(plotter,plotname,savename,**kwargs)
            
            if thisblind:
                plotter.addHistogram('data',sigMap['data'])
    
                for plot in blind_cust:
                    kwargs = deepcopy(plots[plot])
                    kwargs.update(blind_cust[plot])
                    plotname = '{}/{}/{}'.format(sel,region,plot) if region else '{}/{}'.format(sel,plot)
                    savename = '{}/{}/mc/{}_blinder'.format(sel,region,plot) if region else '{}/mc/{}_blinder'.format(sel,plot)
                    plotChannels(plotter,plotname,savename,**kwargs)
                
                    for alt in alt_plots.get(plot,[]):
                        kwargs = deepcopy(plots[plot])
                        kwargs.update(alt_plots[plot][alt])
                        kwargs.update(blind_cust[plot])
                        savename = '{}/{}/mc/{}_blinder'.format(sel,region,alt) if region else '{}/mc/{}_blinder'.format(sel,alt)
                        plotChannels(plotter,plotname,savename,**kwargs)
            

if doDatadriven:
    for region in regions:
        plotter.clearHistograms()
        
        thisblind = blind and region in ['','hzz4l']

        plotter.addHistogramToStack('ZX',sigMap['datadriven'])
        
        for s in samples:
            plotter.addHistogramToStack(s,sigMap[s])
        
        if not thisblind: plotter.addHistogram('data',sigMap['data'])
        
        for plot in plots:
            kwargs = deepcopy(plots[plot])
            plotnames = getDatadrivenPlot('{}/{}'.format(region,plot) if region else plot)
            savename = '{}/{}/datadriven/{}'.format('4P0F',region,plot) if region else '{}/datadriven/{}'.format('4P0F',plot)
            plotChannels(plotter,plotnames,savename,**kwargs)
        
            for alt in alt_plots.get(plot,[]):
                kwargs = deepcopy(plots[plot])
                kwargs.update(alt_plots[plot][alt])
                savename = '{}/{}/datadriven/{}'.format('4P0F',region,alt) if region else '{}/datadriven/{}'.format('4P0F',alt)
                plotChannels(plotter,plotnames,savename,**kwargs)
        
        if thisblind:
            plotter.addHistogram('data',sigMap['data'])
        
            for plot in blind_cust:
                kwargs = deepcopy(plots[plot])
                kwargs.update(blind_cust[plot])
                plotnames = getDatadrivenPlot('{}/{}'.format(region,plot) if region else plot)
                savename = '{}/{}/datadriven/{}_blinder'.format('4P0F',region,plot) if region else '{}/datadriven/{}_blinder'.format('4P0F',plot)
                plotChannels(plotter,plotnames,savename,**kwargs)
            
                for alt in alt_plots.get(plot,[]):
                    kwargs = deepcopy(plots[plot])
                    kwargs.update(alt_plots[plot][alt])
                    kwargs.update(blind_cust[plot])
                    savename = '{}/{}/datadriven/{}_blinder'.format('4P0F',region,alt) if region else '{}/datadriven/{}_blinder'.format('4P0F',alt)
                    plotChannels(plotter,plotnames,savename,**kwargs)
    

if do3P1F:
    for region in regions:
        plotter.clearHistograms()
        
        plotter.addHistogramToStack('ZX',sigMap['datadriven'])
        
        for s in samples3P1F:
            plotter.addHistogramToStack(s,sigMap[s])
        
        plotter.addHistogram('data',sigMap['data'])
        
        for plot in plots:
            kwargs = deepcopy(plots[plot])
            plotnames = get3P1FPlot('{}/{}'.format(region,plot) if region else plot)
            savename = '{}/{}/datadriven/{}'.format('3P1F',region,plot) if region else '{}/datadriven/{}'.format('3P1F',plot)
            plotChannels(plotter,plotnames,savename,**kwargs)
        
            for alt in alt_plots.get(plot,[]):
                kwargs = deepcopy(plots[plot])
                kwargs.update(alt_plots[plot][alt])
                savename = '{}/{}/datadriven/{}'.format('3P1F',region,alt) if region else '{}/datadriven/{}'.format('3P1F',alt)
                plotChannels(plotter,plotnames,savename,**kwargs)
        
