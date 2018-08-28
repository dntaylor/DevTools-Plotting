import argparse
import logging
import os
import sys
import json
import pickle
import operator
import array

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from DevTools.Utilities.utilities import *
import DevTools.Plotter.CMS_lumi as CMS_lumi
import DevTools.Plotter.tdrstyle as tdrstyle

ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 2001;")
tdrstyle.setTDRStyle()
#ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetPalette(ROOT.kBird)

ROOT.gStyle.SetStatX(0.77)
ROOT.gStyle.SetStatY(0.26)

variable = 'met'
fit = False

savenameKey = 'optimize_{0}_{1}_{2}_{3}'

funcMap = {
    'asimov': asimovSignificance,
    'pois': poissonSignificance,
    'asimovErr': asimovSignificanceWithError,
    'poisErr': poissonSignificanceWithError,
}

labelMap = {
    'asimov': 'Asimov Significance',
    'pois': 'Poisson Significance',
    'asimovErr': 'Asimov Significance',
    'poisErr': 'Poisson Significance',
}

varLabelMap = {
    'st': 'S_{T} (GeV)',
    'zveto': '|m_{Z}-m_{ll}|',
    'dr': '#Delta R(l^{#pm}l^{#pm})',
    'met': 'E_{T}^{miss}',
}

prevFit = {
    'Hpp3l': {
        0: {
            'st': ['0.99*x-35'],
            'zveto': ['10'],
            'dr': ['6'],
            'met': ['0'],
        },
        1: {
            'st': ['1.15*x+2'],
            'zveto': ['20'],
            'dr': ['3.2'],
            'met': ['20'],
        },
        2: {
            'st': ['0.98*x+91'],
            'zveto': ['25'],
            'dr': ['x/380.+1.86','x/750+2.37'],
            'met': ['50'],
        },
    },
    'Hpp4l': {
        0: {
            'st': ['1.23*x+54'],
            'zveto': ['0'],
            'dr': ['6'],
        },
        1: {
            'st': ['0.88*x+73'],
            'zveto': ['0'],
            'dr': ['6'],
        },
        2: {
            'st': ['0.46*x+108'],
            'zveto': ['25'],
            'dr': ['x/1400.+2.43'],
        },
    },
}

fitRange = {
    'Hpp3l': {
        0: [200,1000],
        1: [200,500],
        2: [200,500],
    },
    'Hpp4l': {
        0: [200,600],
        1: [200,800],
        2: [200,800],
    },
}

modes = {
    0: ['ee100','em100','mm100'],
    1: ['et100','mt100'],
    2: ['tt100'],
}

for analysis in ['Hpp3l','Hpp4l']:
    if variable=='met' and analysis=='Hpp4l': continue
    for numTau in range(3):
        for metric in ['asimovErr','poisErr','pois']:
            savename = savenameKey.format(analysis,metric,variable,numTau)
        
            
            canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
            canvas.SetRightMargin(0.2) # for Z axis
            
            values = readResults(analysis,'optimization_{0}'.format(variable))
            
            masses = [200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500]
            if analysis=='Hpp4l': masses = [200,300,400,500,600,700,900,1000,1100,1200,1300,1400,1500] # TEMP1!!
            
            optVars = {
                'st':    [x*20 for x in range(4,100)],
                'zveto': [x*5 for x in range(25)],
                'dr':    [1.5+x*0.1 for x in range(50)],
                'met':   [x*5 for x in range(40)],
            
            }
            
            diff = abs(optVars[variable][0]-optVars[variable][1])
            
            hist = ROOT.TH2D(variable,variable,len(masses),masses[0]-50,masses[-1]+50,len(optVars[variable]),optVars[variable][0]-diff/2.,optVars[variable][-1]+diff/2.)
            
            maxLoc = {}
            maxVal = {}
            relDiff = 0.05
            down = {}
            up = {}
            median = {}
            for mass in masses:
                metricVals = {}
                for optVal in optVars[variable]:
                    bg = sumWithError(*[values[mode][mass][variable]['bg'][optVal] for mode in modes[numTau]])
                    sig = sumWithError(*[values[mode][mass][variable]['sig'][optVal] for mode in modes[numTau]])
                    metricVals[optVal] = funcMap[metric](sig,bg)
                    b = hist.FindBin(mass,optVal)
                    hist.SetBinContent(b,metricVals[optVal])
                maxLoc[mass] = max(metricVals.iteritems(), key=operator.itemgetter(1))[0]
                maxVal[mass] = metricVals[maxLoc[mass]]
            
                down[mass] = min([loc for loc in metricVals if metricVals[loc]>(1-relDiff)*maxVal[mass]]+[9999])
                up[mass] = max([loc for loc in metricVals if metricVals[loc]>(1-relDiff)*maxVal[mass]]+[0])
                median[mass] = (up[mass]-down[mass])/2+down[mass]
            
            hist.GetXaxis().SetTitle('#Phi^{++} Mass (GeV)')
            hist.GetYaxis().SetTitle(varLabelMap[variable])
            hist.GetZaxis().SetTitle(labelMap[metric])
            hist.Draw('colz')
            
            maxVals = ROOT.TGraph(len(masses),array.array('d',masses),array.array('d',[maxLoc[m] for m in masses]))
            maxVals.SetMarkerStyle(20)
            maxVals.SetFillStyle(0)
            maxVals.Draw('p same')
            
            upVals = ROOT.TGraph(len(masses),array.array('d',masses),array.array('d',[up[m] for m in masses]))
            upVals.SetMarkerStyle(0)
            upVals.SetFillStyle(0)
            upVals.SetLineStyle(7)
            upVals.Draw('same')
            
            downVals = ROOT.TGraph(len(masses),array.array('d',masses),array.array('d',[down[m] for m in masses]))
            downVals.SetMarkerStyle(0)
            downVals.SetFillStyle(0)
            downVals.SetLineStyle(7)
            #if fit: downVals.Fit('pol1','','',*fitRange[analysis][numTau])
            downVals.Draw('same')
            
            medianVals = ROOT.TGraph(
                len(masses),
                array.array('d',masses),
                array.array('d',[median[m] for m in masses]),
            )
            #medianVals = ROOT.TGraphAsymmErrors(
            #    len(masses),
            #    array.array('d',masses),
            #    array.array('d',[median[m] for m in masses]),
            #    array.array('d',[0]*len(masses)),
            #    array.array('d',[0]*len(masses)),
            #    array.array('d',[median[m]-down[m] for m in masses]),
            #    array.array('d',[up[m]-median[m] for m in masses]),
            #)
            medianVals.SetMarkerStyle(0)
            medianVals.SetFillStyle(0)
            if fit: medianVals.Fit('pol1','','',*fitRange[analysis][numTau])
            medianVals.Draw('same')
            
            #hint = ROOT.TH1D("hint","Fitted .95 conf.band", 100, 150, 1050);
            #ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(hint)
            #hint.SetStats(ROOT.kFALSE)
            #hint.SetMarkerStyle(0)
            #hint.SetFillColor(2)
            #hint.SetFillStyle(3005)
            #hint.Draw("e3 same")
        
            #prevs = []
            #for f in prevFit[analysis][numTau][variable]:
            #    prev = ROOT.TF1('prev_{0}'.format(f),f,masses[0],masses[-1])
            #    prev.SetLineColor(ROOT.kGreen)
            #    prev.SetLineWidth(2)
            #    prev.Draw("lsame")
            #    prevs += [prev]
            
            canvas.Print('{0}.png'.format(savename))
