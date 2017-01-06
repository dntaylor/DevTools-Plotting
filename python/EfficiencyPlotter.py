import os
import sys
import logging
import math
from array import array
from collections import OrderedDict

import ROOT

from DevTools.Plotter.PlotterBase import PlotterBase
from DevTools.Plotter.utilities import getLumi, isData
from DevTools.Plotter.style import getStyle
from DevTools.Utilities.utilities import *
import DevTools.Plotter.CMS_lumi as CMS_lumi
import DevTools.Plotter.tdrstyle as tdrstyle

ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 2001;")
tdrstyle.setTDRStyle()
ROOT.gStyle.SetPalette(1)

# set a custom style, copied from 6.04, just directly when CMSSW has 6.04
stops = array('d', [0.0000, 0.1250, 0.2500, 0.3750, 0.5000, 0.6250, 0.7500, 0.8750, 1.0000])
# rust
red   = array('d', [  0./255., 30./255., 63./255., 101./255., 143./255., 152./255., 169./255., 187./255., 230./255.])
green = array('d', [  0./255., 14./255., 28./255.,  42./255.,  58./255.,  61./255.,  67./255.,  74./255.,  91./255.])
blue  = array('d', [ 39./255., 26./255., 21./255.,  18./255.,  15./255.,  14./255.,  14./255.,  13./255.,  13./255.])
# solar
#red   = array('d', [ 99./255., 116./255., 154./255., 174./255., 200./255., 196./255., 201./255., 201./255., 230./255.])
#green = array('d', [  0./255.,   0./255.,   8./255.,  32./255.,  58./255.,  83./255., 119./255., 136./255., 173./255.])
#blue  = array('d', [  5./255.,   6./255.,   7./255.,   9./255.,   9./255.,  14./255.,  17./255.,  19./255.,  24./255.])
Idx = ROOT.TColor.CreateGradientColorTable(9, stops, red, green, blue, 255);
ROOT.gStyle.SetNumberContours(255)


class EfficiencyPlotter(PlotterBase):
    '''Plot profile of 2D histogram'''

    def __init__(self,analysis='Efficiency',**kwargs):
        '''Initialize the plotter'''
        super(EfficiencyPlotter, self).__init__(analysis,**kwargs)

        self.files = {}
        self.histOrder = []
        self.variables = {}
        self.styles = {}
        self.pretty = {}
        self.j = 0

        self.colors = [ROOT.kGreen, ROOT.kCyan, ROOT.kBlue, ROOT.kViolet, ROOT.kMagenta, ROOT.kRed, ROOT.kOrange,]

    def finish(self):
        '''Cleanup stuff'''
        logging.info('Finished plotting')
        #self.saveFile.Close()

    def _openFile(self,name,fname):
        '''Verify and open a sample'''
        self.files[name] = ROOT.TFile(fname,'read')
        ROOT.gROOT.cd()

    def _getLegend(self,hists,**kwargs):
        '''Get the legend'''
        entries = []
        for h in hists:
            entries += [[hists[h],'{0:.1f} #leq |#eta| #leq {1:.1f}'.format(*self.etabins[h:h+2]),'p0']]
        return super(EfficiencyPlotter,self)._getLegend(entries=entries,**kwargs)


    def addFile(self,name,fname):
        '''Add file of 2D hists'''
        self._openFile(name,fname)
        self.name = name

    def setBinning(self,etabins=[],ptbins=[]):
        '''Set binning for plotting'''
        self.etabins=etabins
        self.ptbins=ptbins

    def addHist(self,name,variable):
        '''Add histogram to plot'''
        self.histOrder += [name]
        self.variables[name] = variable

    def _getHistogram(self,name,**kwargs):
        eta = kwargs.pop('eta',0)
        hist2d = self.files[self.name].Get(self.variables[name])
        tempname = '{0}_{1}'.format(name,self.j)
        hist = ROOT.TH1F(tempname,tempname,len(self.ptbins)-1,array('d',self.ptbins))
        for p,pt in enumerate(self.ptbins):
            pt += 0.001
            val = hist2d.GetBinContent(hist2d.FindBin(pt,eta))
            err = hist2d.GetBinError(hist2d.FindBin(pt,eta))
            hist.SetBinContent(p+1,val)
            hist.SetBinError(p+1,err)
        return hist

    def plot(self,savename,**kwargs):
        '''Plot a variable and save'''
        xaxis = kwargs.pop('xaxis', 'Variable')
        yaxis = kwargs.pop('yaxis', 'Events')
        logy = kwargs.pop('logy',False)
        logx = kwargs.pop('logx',False)
        ymin = kwargs.pop('ymin',None)
        ymax = kwargs.pop('ymax',None)
        yscale = kwargs.pop('yscale',5 if logy else 1.2)
        numcol = kwargs.pop('numcol',1)
        legendpos = kwargs.pop('legendpos',33)
        lumipos = kwargs.pop('lumipos',11)
        isprelim = kwargs.pop('preliminary',True)
        rangex = kwargs.pop('rangex',[])
        save = kwargs.pop('save',True)

        logging.info('Plotting {0}'.format(savename))

        ROOT.gDirectory.Delete('h_*')

        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        #ROOT.SetOwnership(canvas,False)

        canvas.SetLogy(logy)
        canvas.SetLogx(logx)
        canvas.SetRightMargin(0.05)


        highestMax = -9999999.

        # overlay histograms
        hists = OrderedDict()
        for histName in self.histOrder:
            hists[histName] = OrderedDict()
            for e,eta in enumerate(self.etabins[:-1]):
                hist = self._getHistogram(histName,eta=eta,**kwargs)
                hist.SetLineColor(self.colors[e])
                hist.SetMarkerColor(self.colors[e])
                hist.SetFillColor(self.colors[e])
                hist.SetMarkerStyle(20)
                hist.SetMarkerSize(1.)
                hist.SetLineColor(ROOT.kBlack)
                highestMax = max(highestMax,hist.GetMaximum())
                hists[histName][e] = hist

        # now draw them
        logging.debug('Drawing')
        h = 0
        for histName,hist in hists['data'].iteritems():
            style = 'p0'
            if h: style += ' same'
            hist.SetMaximum(ymax)
            hist.SetMinimum(ymin)
            if h==0: hist.GetXaxis().SetTitle(xaxis)
            if h==0: hist.GetYaxis().SetTitle(yaxis)
            hist.Draw(style)
            h += 1

        # get the legend
        logging.debug('Legend')
        legend = self._getLegend(hists['data'],numcol=numcol,position=legendpos)
        legend.Draw()

        # cms lumi styling
        logging.debug('CMSLumi')
        pad = canvas
        if pad != ROOT.TVirtualPad.Pad(): pad.cd()
        self._setStyle(pad,position=lumipos,preliminary=isprelim)

        # save
        if save:
            self._save(canvas,savename)
            logging.debug('Done')
            return 0
        else:
            return self._saveTemp(canvas)

