import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.Plotter import Plotter
from DevTools.Plotter.higgsUtilities import getChannels, getChannelLabels, getCategories, getCategoryLabels, getSubCategories, getSubCategoryLabels
from copy import deepcopy
import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

blind = True

hpp4lPlotter = Plotter('Hpp4l')

#########################
### Define categories ###
#########################

cats = getCategories('Hpp4l')
catLabels = getCategoryLabels('Hpp4l')
subCatChannels = getSubCategories('Hpp4l')
subCatLabels = getSubCategoryLabels('Hpp4l')
chans = getChannels('Hpp4l')
chanLabels = getChannelLabels('Hpp4l')

sigMap = {
    'WZ'  : [
             'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8',
             'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
             'WZTo1L3Nu_13TeV_amcatnloFXFX_madspin_pythia8',
             'WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            ],
    'ZZ'  : [
             'ZZTo4L_13TeV_powheg_pythia8',
             'GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8',
             'ZZTo2L2Nu_13TeV_powheg_pythia8',
             'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            ],
    'VVV' : [
             'WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
             'WWG_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
            ],
    'VH'  : [
             'WH_HToBB_WToLNu_M125_13TeV_amcatnloFXFX_madspin_pythia8',
             'ZH_HToBB_ZToLL_M125_13TeV_amcatnloFXFX_madspin_pythia8',
             'ZH_HToBB_ZToNuNu_M125_13TeV_amcatnloFXFX_madspin_pythia8',
             'ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8',
             'ZH_HToGG_ZToAll_M125_13TeV_powheg_pythia8',
             'ZH_HToZG_ZToAll_M-125_13TeV_powheg_pythia8',
             'ZH_HToZZ_4LFilter_M125_13TeV_powheg2-minlo-HZJ_JHUgenV6_pythia8',
            ],
    'TTV' : [
             'ttWJets_13TeV_madgraphMLM',
             'ttZJets_13TeV_madgraphMLM',
             'ttH_M125_13TeV_powheg_pythia8',
             'tZq_ll_4f_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
             'tZq_nunu_4f_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
            ],
    'WW'  : [
             'WWTo2L2Nu_13TeV-powheg',
             'WWToLNuQQ_13TeV-powheg',
            ],
    'W'   : [
             'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
            ],
    'Z'   : [
             'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
            ],
    'TT'  : [
             'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            ],
    'T'   : [
             'ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
             #'ST_t-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
             'ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
             'ST_t-channel_top_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
             'ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
             'ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
            ],
    'QCD' : [
             'QCD_Pt_5to10_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_10to15_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_15to30_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_30to50_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_50to80_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_80to120_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_120to170_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_170to300_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_300to470_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_470to600_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_600to800_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_800to1000_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_1000to1400_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_1400to1800_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_2400to3200_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_3200toInf_TuneCUETP8M1_13TeV_pythia8',
            ],
    'data': [
             'DoubleMuon',
             'DoubleEG',
             'MuonEG',
             'SingleMuon',
             'SingleElectron',
            ],
    'HppHmm200GeV' : ['HPlusPlusHMinusMinusHTo4L_M-200_13TeV-pythia8'],
    'HppHmm300GeV' : ['HPlusPlusHMinusMinusHTo4L_M-300_13TeV-pythia8'],
    'HppHmm400GeV' : ['HPlusPlusHMinusMinusHTo4L_M-400_13TeV-pythia8'],
    'HppHmm500GeV' : ['HPlusPlusHMinusMinusHTo4L_M-500_13TeV-pythia8'],
    'HppHmm600GeV' : ['HPlusPlusHMinusMinusHTo4L_M-600_13TeV-pythia8'],
    'HppHmm700GeV' : ['HPlusPlusHMinusMinusHTo4L_M-700_13TeV-pythia8'],
    'HppHmm800GeV' : ['HPlusPlusHMinusMinusHTo4L_M-800_13TeV-pythia8'],
    'HppHmm900GeV' : ['HPlusPlusHMinusMinusHTo4L_M-900_13TeV-pythia8'],
    'HppHmm1000GeV': ['HPlusPlusHMinusMinusHTo4L_M-1000_13TeV-pythia8'],
}

samples = ['W','T','TT','TTV','Z','WW','VH','WZ','VVV','ZZ']

for s in samples:
    hpp4lPlotter.addHistogramToStack(s,sigMap[s])

hpp4lPlotter.addHistogram('HppHmm500GeV',sigMap['HppHmm500GeV'],signal=True)#,scale=10)

if not blind:
    hpp4lPlotter.addHistogram('data',sigMap['data'])

# per channel counts
countVars = ['default/count'] + ['default/{0}/count'.format(chan) for chan in chans]
countLabels = ['Total'] + chanLabels
savename = 'individualChannels'
hpp4lPlotter.plotCounts(countVars,countLabels,savename,numcol=3,logy=1,legendpos=34,yscale=10)

# per category counts
countVars = ['default/count']
for cat in cats:
    tempCountVars = []
    for subcat in subCatChannels[cat]:
        tempCountVars += ['default/{0}/count'.format(chan) for chan in subCatChannels[cat][subcat]]
    countVars += [tempCountVars]
countLabels = ['Total'] + catLabels
savename = 'individualCategories'
hpp4lPlotter.plotCounts(countVars,countLabels,savename,numcol=3,logy=1,legendpos=34,yscale=10)

# per subcategory counts
countVars = ['default/count']
for cat in cats:
    for subCat in sorted(subCatChannels[cat]):
        countVars += [['default/{0}/count'.format(chan) for chan in subCatChannels[cat][subCat]]]
countLabels = ['Total'] + subCatLabels
savename = 'individualSubCategories'
hpp4lPlotter.plotCounts(countVars,countLabels,savename,numcol=3,logy=1,legendpos=34,yscale=10,ymin=0.001)



plots = {
    # hpp
    'hppMass'               : {'xaxis': 'm_{l^{+}l^{+}} (GeV)', 'yaxis': 'Events / 20 GeV', 'numcol': 2, 'lumipos': 33, 'rebin': 20, 'logy': True},
    'hppPt'                 : {'xaxis': 'p_{T}^{l^{+}l^{+}} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 20},
    'hppDeltaR'             : {'xaxis': '#DeltaR(l^{+}l^{+})', 'yaxis': 'Events', 'rebin': 25},
    'hppLeadingLeptonPt'    : {'xaxis': 'p_{T}^{#Phi_{lead}^{++}} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 20},
    'hppSubLeadingLeptonPt' : {'xaxis': 'p_{T}^{#Phi_{sublead}^{++}} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 20},
    # hmm
    'hmmMass'               : {'xaxis': 'm_{l^{-}l^{-}} (GeV)', 'yaxis': 'Events / 20 GeV', 'numcol': 2, 'lumipos': 33, 'rebin': 20, 'logy': True},
    'hmmPt'                 : {'xaxis': 'p_{T}^{l^{-}l^{-}} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 20},
    'hmmDeltaR'             : {'xaxis': '#DeltaR(l^{-}l^{-})', 'yaxis': 'Events', 'rebin': 25},
    'hmmLeadingLeptonPt'    : {'xaxis': 'p_{T}^{#Phi_{lead}^{--}} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 20},
    'hmmSubLeadingLeptonPt' : {'xaxis': 'p_{T}^{#Phi_{sublead}^{--}} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 20},
    # z cand
    'zMass'                 : {'xaxis': 'm_{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 10 GeV', 'rebin': 10},
    'mllMinusMZ'            : {'xaxis': '|m_{l^{+}l^{-}}-m_{Z}| (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 5},
    # event
    'numVertices'           : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 20},
    'mass'                  : {'xaxis': 'm_{4l} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 20},
    'st'                    : {'xaxis': '#Sigma p_{T}^{l} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 20},
}

# signal region
for plot in plots:
    plotname = 'default/{0}'.format(plot)
    hpp4lPlotter.plot(plotname,plot,**plots[plot])
    for cat in cats:
        plotnames = []
        for subcat in subCatChannels[cat]:
            plotnames += ['default/{0}/{1}'.format(chan,plot) for chan in subCatChannels[cat][subcat]]
        savename = '{0}/{1}'.format(cat,plot)
        hpp4lPlotter.plot(plotnames,savename,**plots[plot])

#rocplots = {
#    'st' : {'legendpos':34,'numcol':3,'invert':False},
#}
#
#for plot,kwargs in rocplots.iteritems():
#    sig = {'HppHmm500GeV':'default/{0}'.format(plot)}
#    bg = {}
#    for s in samples:
#        bg[s] = 'default/{0}'.format(plot)
#    hpp4lPlotter.plotROC(sig, bg, 'roc_{0}'.format(plot), **kwargs)


if blind:
    hpp4lPlotter.addHistogram('data',sigMap['data'])


# partially blinded plots
if blind:
    blinders = {
        'hppMass': [100,1200],
        'hmmMass': [100,1200],
    }
    
    for plot in blinders:
        plotname = 'default/{0}'.format(plot)
        savename = '{0}_blinder'.format(plot)
        hpp4lPlotter.plot(plotname,savename,blinder=blinders[plot],**plots[plot])
        for cat in cats:
            plotnames = []
            for subcat in subCatChannels[cat]:
                plotnames += ['default/{0}/{1}'.format(chan,plot) for chan in subCatChannels[cat][subcat]]
            savename = '{0}/{1}_blinder'.format(cat,plot)
            hpp4lPlotter.plot(plotnames,savename,blinder=blinders[plot],**plots[plot])


# low mass control
hpp4lPlotter.clearHistograms()

for s in samples:
    hpp4lPlotter.addHistogramToStack(s,sigMap[s])
hpp4lPlotter.addHistogram('data',sigMap['data'])

# per channel counts
countVars = ['lowmass/count'] + ['lowmass/{0}/count'.format(chan) for chan in chans]
countLabels = ['Total'] + chanLabels
savename = 'lowmass/individualChannels'
hpp4lPlotter.plotCounts(countVars,countLabels,savename,numcol=2)

# per category counts
countVars = ['lowmass/count']
for cat in cats:
    tempCountVars = []
    for subcat in subCatChannels[cat]:
        tempCountVars += ['lowmass/{0}/count'.format(chan) for chan in subCatChannels[cat][subcat]]
    countVars += [tempCountVars]
countLabels = ['Total'] + catLabels
savename = 'lowmass/individualCategories'
hpp4lPlotter.plotCounts(countVars,countLabels,savename,numcol=3,logy=1,legendpos=34,yscale=10)

# per subcategory counts
countVars = ['lowmass/count']
for cat in cats:
    for subCat in sorted(subCatChannels[cat]):
        countVars += [['lowmass/{0}/count'.format(chan) for chan in subCatChannels[cat][subCat]]]
countLabels = ['Total'] + subCatLabels
savename = 'lowmass/individualSubCategories'
hpp4lPlotter.plotCounts(countVars,countLabels,savename,numcol=3,logy=1,legendpos=34,ymax=1e4,ymin=0.001)



lowmass_cust = {
    # hpp
    'hppMass'              : {'rangex': [0,300], 'logy': False},
    'hppPt'                : {'rangex': [0,300]},
    'hppLeadingLeptonPt'   : {'rangex': [0,300]},
    'hppSubLeadingLeptonPt': {'rangex': [0,300]},
    # hmm
    'hmmMass'              : {'rangex': [0,300], 'logy': False},
    'hmmPt'                : {'rangex': [0,300]},
    'hmmLeadingLeptonPt'   : {'rangex': [0,300]},
    'hmmSubLeadingLeptonPt': {'rangex': [0,300]},
    # z
    'zMass'                : {'rangex': [60,120]},
    'mllMinusMZ'           : {'rangex': [0,60]},
    # event
    'met'                  : {'rangex': [0,200]},
    'mass'                 : {'rangex': [0,600], 'rebin':25, 'xaxis': 'Events / 25 GeV'},
    'st'                   : {'rangex': [0,400], 'rebin':25, 'xaxis': 'Events / 25 GeV'},
}

for plot in plots:
    plotname = 'lowmass/{0}'.format(plot)
    kwargs = deepcopy(plots[plot])
    if plot in lowmass_cust: kwargs.update(lowmass_cust[plot])
    hpp4lPlotter.plot(plotname,plotname,**kwargs)
    for cat in cats:
        plotnames = []
        for subcat in subCatChannels[cat]:
            plotnames += ['lowmass/{0}/{1}'.format(chan,plot) for chan in subCatChannels[cat][subcat]]
        savename = 'lowmass/{0}/{1}'.format(cat,plot)
        hpp4lPlotter.plot(plotnames,savename,**kwargs)


# normalized plots
hpp4lPlotter.clearHistograms()

samples = ['TT','TTV','Z','WW','WZ','VVV','ZZ']
allSamplesDict = {'BG':[]}

for s in samples:
    allSamplesDict['BG'] += sigMap[s]

hpp4lPlotter.addHistogram('BG',allSamplesDict['BG'])
hpp4lPlotter.addHistogram('HppHmm500GeV',sigMap['HppHmm500GeV'],signal=True)

norm_cust = {
    # hpp
    'hppMass'               : {'yaxis': 'Unit normalized', 'logy':0, 'rebin': 1},
    'hppPt'                 : {'yaxis': 'Unit normalized', 'rebin': 20, 'numcol': 2},
    'hppDeltaR'             : {'yaxis': 'Unit normalized', 'rebin': 10},
    'hppLeadingLeptonPt'    : {'yaxis': 'Unit normalized', 'rebin': 5},
    'hppSubLeadingLeptonPt' : {'yaxis': 'Unit normalized', 'rebin': 5},
    # hmm
    'hmmMass'               : {'yaxis': 'Unit normalized', 'logy':0, 'rebin': 1},
    'hmmPt'                 : {'yaxis': 'Unit normalized', 'rebin': 20, 'numcol': 2},
    'hmmDeltaR'             : {'yaxis': 'Unit normalized', 'rebin': 10},
    'hmmLeadingLeptonPt'    : {'yaxis': 'Unit normalized', 'rebin': 5},
    'hmmSubLeadingLeptonPt' : {'yaxis': 'Unit normalized', 'rebin': 5},
    # z
    'zMass'                 : {'yaxis': 'Unit normalized', 'rebin': 20, 'numcol': 2},
    'mllMinusMZ'            : {'yaxis': 'Unit normalized', 'rebin': 1},
    # event
    'met'                   : {'yaxis': 'Unit normalized', 'rebin': 1},
    'numVertices'           : {'yaxis': 'Unit normalized'},
    'mass'                  : {'yaxis': 'Unit normalized', 'rebin': 10},
    'st'                    : {'yaxis': 'Unit normalized', 'rebin': 10},
}

for plot in plots:
    plotname = 'default/{0}'.format(plot)
    savename = 'normalized/{0}'.format(plot)
    kwargs = deepcopy(plots[plot])
    if plot in norm_cust: kwargs.update(norm_cust[plot])
    hpp4lPlotter.plotNormalized(plotname,savename,**kwargs)
    for cat in cats:
        plotnames = []
        for subcat in subCatChannels[cat]:
            plotnames += ['default/{0}/{1}'.format(chan,plot) for chan in subCatChannels[cat][subcat]]
        savename = 'normalized/{0}/{1}'.format(cat,plot)
        hpp4lPlotter.plotNormalized(plotnames,savename,**kwargs)

# all signal on one plot
hpp4lPlotter.clearHistograms()

sigColors = {
    200 : ROOT.TColor.GetColor('#000000'),
    300 : ROOT.TColor.GetColor('#330000'),
    400 : ROOT.TColor.GetColor('#660000'),
    500 : ROOT.TColor.GetColor('#800000'),
    600 : ROOT.TColor.GetColor('#990000'),
    700 : ROOT.TColor.GetColor('#B20000'),
    800 : ROOT.TColor.GetColor('#CC0000'),
    900 : ROOT.TColor.GetColor('#FF0000'),
    1000: ROOT.TColor.GetColor('#FF3333'),
    1100: ROOT.TColor.GetColor('#FF6666'),
    1200: ROOT.TColor.GetColor('#FF8080'),
    1300: ROOT.TColor.GetColor('#FF9999'),
    1400: ROOT.TColor.GetColor('#FFB2B2'),
    1500: ROOT.TColor.GetColor('#FFCCCC'),
}

#masses = [200,300,400,500,600,700,800,900,1000]
masses = [200,400,600,800,1000]
for mass in masses:
    hpp4lPlotter.addHistogram('HppHmm{0}GeV'.format(mass),sigMap['HppHmm{0}GeV'.format(mass)],signal=True,style={'linecolor': sigColors[mass]})

catRebin = {
    'I'  : 1,
    'II' : 5,
    'III': 10,
    'IV' : 10,
    'V'  : 20,
    'VI' : 50,
}

genRebin = {
    'ee' : 1,
    'em' : 1,
    'et' : 5,
    'mm' : 1,
    'mt' : 5,
    'tt' : 10,
}

genDecayMap = {
    'ee' : ['ee'],
    'em' : ['em'],
    'et' : ['ee','em','et'],
    'mm' : ['mm'],
    'mt' : ['em','mm','mt'],
    'tt' : ['ee','em','et','mm','mt','tt'],
}

for plot in norm_cust:
    plotname = 'default/{0}'.format(plot)
    savename = 'signal/{0}'.format(plot)
    kwargs = deepcopy(plots[plot])
    if plot in norm_cust: kwargs.update(norm_cust[plot])
    hpp4lPlotter.plotNormalized(plotname,savename,**kwargs)
    for cat in cats:
        plotnames = []
        for subcat in subCatChannels[cat]:
            plotnames += ['default/{0}/{1}'.format(chan,plot) for chan in subCatChannels[cat][subcat]]
        savename = 'signal/{0}/{1}'.format(cat,plot)
        catkwargs = deepcopy(kwargs)
        if cat in catRebin and 'rebin' in catkwargs and plot in ['hppMass','hmmMass']: catkwargs['rebin'] = catkwargs['rebin'] * catRebin[cat]
        hpp4lPlotter.plotNormalized(plotnames,savename,**catkwargs)
    if 'hpp' in plot: # plot just the channels of the type
        for higgsChan in ['ee','em','et','mm','mt','tt']:
            # reco
            plotnames = ['default/{0}/{1}'.format(chan,plot) for chan in chans if chan[:2]==higgsChan] + ['default/{0}/{1}'.format(chan,plot.replace('hpp','hmm')) for chan in chans if chan[2:]==higgsChan]
            savename = 'signal/{0}/{1}'.format(higgsChan,plot)
            genkwargs = deepcopy(kwargs)
            if higgsChan in genRebin and 'rebin' in genkwargs and plot in ['hppMass','hmmMass']: genkwargs['rebin'] = genkwargs['rebin'] * genRebin[higgsChan]
            hpp4lPlotter.plotNormalized(plotnames,savename,**genkwargs)
            # and the gen truth
            plotnames = []
            for gen in chans:
                for reco in chans:
                    if reco[:2] in genDecayMap[gen[:2]] and reco[2:] in genDecayMap[gen[2:]] and gen[:2]==higgsChan:
                        plotnames += ['default/{0}/gen_{1}/{2}'.format(reco,gen,plot)] 
                    #if reco[:2] in genDecayMap[gen[:2]] and reco[2:] in genDecayMap[gen[2:]] and gen[2:]==higgsChan:
                    #    plotnames += ['default/{0}/gen_{1}/{2}'.format(reco,gen,plot.replace('hpp','hmm'))] 
            if plotnames:
                savename = 'signal/{0}/{1}_genMatched'.format(higgsChan,plot)
                hpp4lPlotter.plotNormalized(plotnames,savename,**genkwargs)
