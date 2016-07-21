import os
import sys
import logging
import math
from array import array
from collections import OrderedDict

import ROOT

from DevTools.Plotter.PlotterBase import PlotterBase
from DevTools.Plotter.utilities import python_mkdir, getLumi
from DevTools.Plotter.style import getStyle
import DevTools.Plotter.CMS_lumi as CMS_lumi
import DevTools.Plotter.tdrstyle as tdrstyle

ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")
tdrstyle.setTDRStyle()
ROOT.gStyle.SetPalette(1)

class LimitPlotter(PlotterBase):
    '''Basic limit plotter utilities'''

    def __init__(self,**kwargs):
        '''Initialize the plotter'''
        super(LimitPlotter, self).__init__('Limits',**kwargs)
        # initialize stuff

    def _readLimit(self,filename):
        '''Read limits from file, must be one line of the form:
               "exp0.025 exp0.16 exp0.5 exp0.84 exp0.975 obs"'''
        with open(filename) as f:
           content = f.readlines()
        limitString = content[0].rstrip()
        limvals = [float(x) for x in limitString.split()]
        if len(limvals)!=6:
            logging.warning('No limit found in {0}'.format(filename))
            limvals = [0.]*6
        return limvals

    def _readLimits(self,xvals,filenames):
        limits = {}
        if len(xvals)!=len(filenames):
            logging.error('Mismatch betwen length of xvals ({0}) and length of filenames ({1}).'.format(len(xvals),len(filenames)))
            return limits
        for x,filename in zip(xvals,filenames):
            limits[x] = self._readLimit(filename)
        return limits

    def plotLimit(self,xvals,filenames,savename,**kwargs):
        '''Plot limits'''
        xaxis = kwargs.pop('xaxis','#Phi^{++} Mass (GeV)')
        yaxis = kwargs.pop('yaxis','95% CLs Upper Limit on #sigma/#sigma_{model}')
        blind = kwargs.pop('blind',True)
        lumipos = kwargs.pop('lumipos',11)
        isprelim = kwargs.pop('isprelim',True)
        legendpos = kwargs.pop('legendpos',31)
        numcol = kwargs.pop('numcol',1)

        logging.info('Plotting {0}'.format(savename))

        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        canvas.SetLogy(1)

        limits = self._readLimits(xvals,filenames)
        if not limits: return

        n = len(xvals)
        twoSigma = ROOT.TGraph(2*n)
        oneSigma = ROOT.TGraph(2*n)
        expected = ROOT.TGraph(n)
        observed = ROOT.TGraph(n)
        twoSigma_low = ROOT.TGraph(n)
        twoSigma_high = ROOT.TGraph(n)
        oneSigma_low = ROOT.TGraph(n)
        oneSigma_high = ROOT.TGraph(n)

        for i in range(len(xvals)):
            twoSigma.SetPoint(i,      xvals[i],     limits[xvals[i]][0]) # 0.025
            oneSigma.SetPoint(i,      xvals[i],     limits[xvals[i]][1]) # 0.16
            expected.SetPoint(i,      xvals[i],     limits[xvals[i]][2]) # 0.5
            oneSigma.SetPoint(n+i,    xvals[n-i-1], limits[xvals[n-i-1]][3]) # 0.84
            twoSigma.SetPoint(n+i,    xvals[n-i-1], limits[xvals[n-i-1]][4]) # 0.975
            observed.SetPoint(i,      xvals[i],     limits[xvals[i]][5]) # obs
            twoSigma_high.SetPoint(i,  xvals[i],    limits[xvals[i]][0]) # 0.025
            oneSigma_high.SetPoint(i,  xvals[i],    limits[xvals[i]][1]) # 0.16
            oneSigma_low.SetPoint(i, xvals[n-i-1],  limits[xvals[n-i-1]][3]) # 0.84
            twoSigma_low.SetPoint(i, xvals[n-i-1],  limits[xvals[n-i-1]][4]) # 0.975

        twoSigma.SetFillColor(ROOT.kYellow)
        twoSigma.SetLineColor(ROOT.kYellow)
        twoSigma.SetMarkerStyle(0)
        oneSigma.SetFillColor(ROOT.kSpring)
        oneSigma.SetLineColor(ROOT.kSpring)
        oneSigma.SetMarkerStyle(0)
        expected.SetLineStyle(7)
        expected.SetMarkerStyle(0)
        expected.SetFillStyle(0)
        observed.SetMarkerStyle(0)
        observed.SetFillStyle(0)

        expected.GetXaxis().SetLimits(xvals[0],xvals[-1])
        expected.GetXaxis().SetTitle(xaxis)
        expected.GetYaxis().SetTitle(yaxis)

        expected.Draw()
        twoSigma.Draw('f')
        oneSigma.Draw('f')
        expected.Draw('same')
        ROOT.gPad.RedrawAxis()
        if not blind: observed.Draw('same')

        ratiounity = ROOT.TLine(expected.GetXaxis().GetXmin(),1,expected.GetXaxis().GetXmax(),1)
        ratiounity.Draw()

        # get the legend
        entries = [
            [expected,'Expected','l'],
            [twoSigma,'Expected 2#sigma','F'],
            [oneSigma,'Expected 1#sigma','F'],
        ]
        if not blind: entries = [[observed,'Observed','l']] + entries
        legend = self._getLegend(entries=entries,numcol=numcol,position=legendpos)
        legend.Draw()

        # cms lumi styling
        self._setStyle(canvas,position=lumipos,preliminary=isprelim)

        self._save(canvas,savename)

        # get expected limit
        y = 0
        for x in range(1,1500):
            y = expected.Eval(x)
            if y > 1: break
        y = 0
        for l1 in range(1,1500):
            y = oneSigma_low.Eval(l1)
            if y > 1: break
        y = 0
        for h1 in range(1,1500):
            y = oneSigma_high.Eval(h1)
            if y > 1: break
        for l2 in range(1,1500):
            y = twoSigma_low.Eval(l2)
            if y > 1: break
        y = 0
        for h2 in range(1,1500):
            y = twoSigma_high.Eval(h2)
            if y > 1: break

        # get observed limit
        if not blind:
            dy = 0
            for dx in range(1,1500):
                dy = observed.Eval(dx)
                if dy > 1: break
        else:
            dx = 0


        logging.info("Expected Limit: %i GeV (+%i, -%i)" % (x, h1-x, x-l1))
        if not blind: logging.info("Observed Limit: %i GeV" % (dx))

        return [l2,l1,x,h1,h2,dx]

    def moneyPlot(self,limvals,savename,**kwargs):
        xaxis = kwargs.pop('xaxis','Excluded Masses (GeV)')
        yaxis = kwargs.pop('yaxis','')
        blind = kwargs.pop('blind',True)
        lumipos = kwargs.pop('lumipos',0)
        isprelim = kwargs.pop('isprelim',True)
        legendpos = kwargs.pop('legendpos',31)
        numcol = kwargs.pop('numcol',1)

        logging.info('Plotting {0}'.format(savename))

        canvas = ROOT.TCanvas(savename,savename,50,50,800,600)
        canvas.SetFillColor(0)
        canvas.SetBorderMode(0)
        canvas.SetFrameFillStyle(0)
        canvas.SetFrameBorderMode(0)
        canvas.SetLeftMargin(0.22)
        canvas.SetRightMargin(0.04)
        canvas.SetTopMargin(0.08)
        canvas.SetBottomMargin(0.12)

        labels = OrderedDict()
        labels['ee100'] = '100% #Phi^{#pm#pm} #rightarrow e^{#pm}e^{#pm}'
        labels['em100'] = '100% #Phi^{#pm#pm} #rightarrow e^{#pm}#mu^{#pm}'
        labels['mm100'] = '100% #Phi^{#pm#pm} #rightarrow #mu^{#pm}#mu^{#pm}'
        labels['et100'] = '100% #Phi^{#pm#pm} #rightarrow e^{#pm}#tau^{#pm}'
        labels['mt100'] = '100% #Phi^{#pm#pm} #rightarrow #mu^{#pm}#tau^{#pm}'
        labels['tt100'] = '100% #Phi^{#pm#pm} #rightarrow #tau^{#pm}#tau^{#pm}'
        labels['BP1']   = 'Benchmark 1'
        labels['BP2']   = 'Benchmark 2'
        labels['BP3']   = 'Benchmark 3'
        labels['BP4']   = 'Benchmark 4'

        colors = {
            'Combined' : {
                1: ROOT.kSpring,
                2: ROOT.kYellow,
            },
            'AP' : {
                1: ROOT.TColor.GetColor('#FF6633'),
                2: ROOT.TColor.GetColor('#FFCC33'),
            },
            'PP' : {
                1: ROOT.TColor.GetColor('#3399FF'),
                2: ROOT.TColor.GetColor('#33FFFF'),
            },
        }

        prodLabels = {
            'AP' : 'Assoc. Prod.',
            'PP' : 'Pair Prod.',
            'Combined': 'Combined',
        }

        nl = len(labels)
        h = ROOT.TH2F("h", "h; {0}; ".format(xaxis), 1,0,1500,nl+2,0.5,nl+2.5)
        h.GetYaxis().SetRangeUser(2,nl+1)
        h.Draw()

        cur = len(labels)*3. + 8
        errors_one = {}
        errors_two = {}
        expected = {}
        observed = {}
        for i,mode in enumerate(labels):
            h.GetYaxis().SetBinLabel(nl+1-i,labels[mode])
            cur -= 3
            errors_one[mode] = {}
            errors_two[mode] = {}
            expected[mode] = {}
            observed[mode] = {}
            sub = 0
            for prod in ['AP','PP']:
                sub += 1
                l2, l1, exp, h1, h2, obs = limvals[mode][prod]
                errors_one[mode][prod] = ROOT.TGraphAsymmErrors(1,array('d',[exp]),array('d',[(cur-sub)/3]),array('d',[exp-l1]),array('d',[h1-exp]),array('d',[0.5/3]),array('d',[0.5/3]))
                errors_two[mode][prod] = ROOT.TGraphAsymmErrors(1,array('d',[exp]),array('d',[(cur-sub)/3]),array('d',[exp-l2]),array('d',[h2-exp]),array('d',[0.5/3]),array('d',[0.5/3]))
                expected[mode][prod]   = ROOT.TGraphAsymmErrors(1,array('d',[exp]),array('d',[(cur-sub)/3]),array('d',[0.]),array('d',[0.]),array('d',[0.5/3]),array('d',[0.5/3]))
                observed[mode][prod]   = ROOT.TGraph(1,array('d',[exp if blind else obs]),array('d',[(cur-sub)/3]))
                errors_one[mode][prod].SetFillColor(colors[prod][1])
                errors_two[mode][prod].SetFillColor(colors[prod][2])
                errors_two[mode][prod].Draw('2')
                errors_one[mode][prod].Draw('2')
                expected[mode][prod].SetMarkerStyle(1)
                expected[mode][prod].Draw('same Z')
                observed[mode][prod].SetMarkerStyle(20)
                if not blind: observed[mode][prod].Draw('P')

        ROOT.gPad.RedrawAxis()

        # custom legend
        latex = ROOT.TLatex()
        latex.SetTextFont(42)
        latex.SetTextColor(ROOT.kBlack)
        latex.SetTextSize(0.08)
        
        legend = ROOT.TPad('legend','legend',0.65,0.5,0.95,0.85)
        legend.SetTopMargin(0)
        legend.SetBottomMargin(0)
        legend.SetLeftMargin(0)
        legend.SetRightMargin(0)
        legend.SetFrameLineWidth(0)
        legend.Draw()
        legend.cd()
        
        hl = ROOT.TH2F("hl", "hl; ; ", 1,-5.5,1.5,3,0.5,3.5)
        hl.Draw('AH')

        legendErrors = {}
        for i,prod in enumerate(['AP','PP','Combined']):
            legendErrors[prod] = {}
            legendErrors[prod]['two'] = ROOT.TGraphAsymmErrors(1,array('d',[0.]),array('d',[3.-i*2./3]),array('d',[1.0]),array('d',[1.0]),array('d',[0.5/2]),array('d',[0.5/2]))
            legendErrors[prod]['one'] = ROOT.TGraphAsymmErrors(1,array('d',[0.]),array('d',[3.-i*2./3]),array('d',[0.5]),array('d',[0.5]),array('d',[0.5/2]),array('d',[0.5/2]))
            legendErrors[prod]['exp'] = ROOT.TGraphAsymmErrors(1,array('d',[0.]),array('d',[3.-i*2./3]),array('d',[0.0]),array('d',[0.0]),array('d',[0.5/2]),array('d',[0.5/2]))
            legendErrors[prod]['two'].SetFillColor(colors[prod][2])
            legendErrors[prod]['one'].SetFillColor(colors[prod][1])
            legendErrors[prod]['two'].Draw('2')
            legendErrors[prod]['one'].Draw('2')
            legendErrors[prod]['exp'].SetMarkerStyle(1)
            legendErrors[prod]['exp'].Draw('same Z')
            latex.DrawLatex(-5,2.9-i*2./3,prodLabels[prod])
        legendErrors['obs'] = ROOT.TGraph(1,array('d',[0.]),array('d',[1.]))
        legendErrors['obs'].Draw('P')
        latex.DrawLatex(-5,0.9,'Observed')

        canvas.cd()
        ROOT.gPad.RedrawAxis()

        # cms lumi styling
        self._setStyle(canvas,position=lumipos,preliminary=isprelim)

        self._save(canvas,savename)

