import os
import sys
import logging
import math
from array import array
from collections import OrderedDict

import ROOT

from DevTools.Plotter.PlotterBase import PlotterBase
from DevTools.Plotter.NtupleWrapper import NtupleWrapper
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


class Plotter(PlotterBase):
    '''Basic plotter utilities'''

    def __init__(self,analysis,**kwargs):
        '''Initialize the plotter'''
        super(Plotter, self).__init__(analysis,**kwargs)
        self.new = kwargs.pop('new',False)

        # empty initialization
        self.histDict = {}
        self.analysisDict = {}
        self.stackOrder = []
        self.histOrder = []
        self.sampleFiles = {}
        self.styles = {}
        self.signals = []
        self.histScales = {}
        self.sampleSelection = {}
        self.uncertainties = {}
        self.j = 0

    #def __exit__(self, type, value, traceback):
    #    self.finish()

    #def __del__(self):
    #    self.finish()

    def finish(self):
        '''Cleanup stuff'''
        logging.info('Finished plotting')
        #self.saveFile.Close()

    def _openFile(self,sampleName,**kwargs):
        '''Verify and open a sample'''
        analysis = kwargs.pop('analysis',self.analysis)
        if analysis not in self.sampleFiles: self.sampleFiles[analysis] = {}
        if sampleName not in self.sampleFiles[analysis]:
            self.sampleFiles[analysis][sampleName] = NtupleWrapper(analysis,sampleName,new=self.new,**kwargs)
            ROOT.gROOT.cd()

    def setSelectionMap(self,selMap):
        '''Set a map of per sample selections.'''
        self.sampleSelection = selMap

    def addHistogramToStack(self,histName,histConstituents,style={},**kwargs):
        '''
        Add a histogram to the stack. histConstituents is a list.
        '''
        analysis = kwargs.pop('analysis',self.analysis)
        for sampleName in histConstituents:
            self._openFile(sampleName,analysis=analysis,**kwargs)
        self.analysisDict[histName] = analysis
        self.histDict[histName] = histConstituents
        self.stackOrder += [histName]
        self.styles[histName] = getStyle(histName)
        self.styles[histName].update(style)

    def setStyle(self,histName,style):
        '''Manually add a style'''
        self.styles[histName] = style

    def addHistogram(self,histName,histConstituents,style={},signal=False,scale=1,noplot=False,**kwargs):
        '''
        Add histogram to plot. histConstituents is a list.
        Style is a custom styling.
        '''
        analysis = kwargs.pop('analysis',self.analysis)
        for sampleName in histConstituents:
            self._openFile(sampleName,analysis=analysis,**kwargs)
        self.analysisDict[histName] = analysis
        self.histDict[histName] = histConstituents
        if not noplot: self.histOrder += [histName]
        self.styles[histName] = getStyle(histName)
        self.styles[histName].update(style)
        if signal: self.signals += [histName]
        if scale!=1: self.histScales[histName] = scale

    def addUncertainty(self,*histNames,**uncertainties):
        '''Add an uncertainty to a histogram'''
        for histName in histNames:
            if histName not in self.uncertainties: self.uncertainties[histName] = {}
            for uncName, val in uncertainties.iteritems():
                self.uncertainties[histName][uncName] = val

    def clearHistograms(self):
        self.sampleFiles = {}
        self.analysisDict = {}
        self.histDict = {}
        self.histOrder = []
        self.stackOrder = []
        self.styles = {}
        self.signals = []
        self.histScales = {}
        self.sampleSelection = {}
        self.uncertainties = {}

    def _readSampleVariable(self,sampleName,variable,**kwargs):
        '''Read the histogram from file'''
        analysis = kwargs.pop('analysis',self.analysis)
        hist = self.sampleFiles[analysis][sampleName].getHist(variable)
        logging.debug('Read {0} {1} {2}: {3}'.format(analysis, sampleName, variable, hist))
        if hist:
            self.j += 1
            hist = hist.Clone('h_temp_{0}'.format(self.j))
        return hist

    def _getTempHistogram(self,sampleName,histName,selection,scalefactor,variable,binning,**kwargs):
        '''Read the histogram from file'''
        analysis = kwargs.pop('analysis',self.analysis)
        hist = self.sampleFiles[analysis][sampleName].getTempHist(histName,selection,scalefactor,variable,binning)
        logging.debug('Create temp {0} {1} {2}: {3}'.format(analysis, sampleName, histName, hist))
        if hist:
            self.j += 1
            hist = hist.Clone('h_temp_{0}'.format(self.j))
            logging.debug(' - Integral: {0}; Entries: {1};'.format(hist.Integral(),hist.GetEntries()))
        else:
            logging.debug(' - Failed')
        return hist

    def _getHistogram(self,histName,variable,**kwargs):
        '''Get a styled histogram'''
        rebin = kwargs.pop('rebin',0)
        nofill = kwargs.pop('nofill',False)
        analysis = self.analysisDict[histName]
        scalefactor = kwargs.pop('scalefactor','1')
        mcscalefactor = kwargs.pop('mcscalefactor','1')
        datascalefactor = kwargs.pop('datascalefactor','1')
        selection = kwargs.pop('selection','')
        binning = kwargs.pop('binning',[])
        overflow = kwargs.pop('overflow',False)
        underflow = kwargs.pop('underflow',False)
        scalewidth = kwargs.pop('scalewidth',False)
        # check if it is a variable map, variable list, or single variable
        if isinstance(variable,dict):       # its a map
            variable = variable[histName]
        if isinstance(variable,basestring): # its a single variable
            variable = [variable]
        # it is now a list
        if histName not in self.histDict:
            logging.error('{0} not defined.'.format(histName))
            return 0

        # get histogram
        hists = ROOT.TList()
        logging.debug('Reading {0}'.format(histName))
        for varName in variable:
            for sampleName in self.histDict[histName]:
                if selection and binning: # get temp hist
                    sf = '*'.join([scalefactor,datascalefactor if isData(sampleName) else mcscalefactor])
                    thissel = '{0} && {1}'.format(selection, self.sampleSelection[sampleName]) if sampleName in self.sampleSelection else selection
                    hist = self._getTempHistogram(sampleName,histName,thissel,sf,varName,binning,analysis=analysis)
                else:
                    hist = self._readSampleVariable(sampleName,varName,analysis=analysis)
                if hist: hists.Add(hist)
        if hists.IsEmpty(): return 0
        hist = hists[0].Clone('h_{0}_{1}'.format(histName,varName.replace('/','_')))
        hist.Reset()
        hist.Merge(hists)

        logging.debug('{0} - Integral: {1}'.format(histName, hist.Integral()))

        if rebin:
            if type(rebin) in [list,tuple]:
                hist = hist.Rebin(len(rebin)-1,'',array('d',rebin))
                # normalize to the bin width
                if scalewidth: hist.Scale(1,'width')
            else:
                hist = hist.Rebin(rebin)

        # put overflow on plot
        if overflow or underflow:
            nx = hist.GetNbinsX()
            if underflow: nx += 1
            if overflow: nx += 1
            xbins = [0]*(nx+1)
            for i in range(nx):
                xbins[i]=hist.GetBinLowEdge(i+1)
            xbins[nx]=xbins[nx-1]+hist.GetBinWidth(nx)
            tempName = hist.GetName()+'OU'
            htmp = ROOT.TH1D(tempName, hist.GetTitle(), nx, array('d',xbins))
            htmp.Sumw2()
            for i in range(nx):
                htmp.SetBinContent(i+1, hist.GetBinContent(i+1))
                htmp.SetBinError(i+1, hist.GetBinError(i+1))
            htmp.SetBinContent(0, hist.GetBinContent(0))
            htmp.SetBinError(0, hist.GetBinError(0))
            htmp.SetEntries(hist.GetEntries())
            hist = htmp

        # add uncertainties
        if histName in self.uncertainties:
            unc2 = 0.
            for uncName,val in self.uncertainties[histName].iteritems():
                unc2 += val**2
            unc = unc2**0.5
            for b in range(hist.GetNbinsX()):
                bVal = hist.GetBinContent(b+1)
                bErr = hist.GetBinError(b+1)
                newErr = ((bVal*unc)**2 + bErr**2)**0.5
                hist.SetBinError(b+1,newErr)

        # style it
        style = self.styles[histName]
        hist.SetTitle(style['name'])
        if 'linecolor' in style:
            hist.SetLineColor(style['linecolor'])
            hist.SetMarkerColor(style['linecolor'])
        if 'linestyle' in style:
            hist.SetLineStyle(style['linestyle'])
        if not nofill:
            if 'fillstyle' in style: hist.SetFillStyle(style['fillstyle'])
            if 'fillcolor' in style: hist.SetFillColor(style['fillcolor'])

        # remove bins < 0
        for b in range(hist.GetNbinsX()):
            if hist.GetBinContent(b+1)<0.:
                logging.debug('{0}: Zeroing negative bin {1}: {2}'.format(histName, b,hist.GetBinContent(b+1)))
                hist.SetBinContent(b+1,0.)

        return hist

    def _getHistogramCounts(self,histName,variables,**kwargs):
        '''Get the integral of each given histogram'''
        savename = kwargs.pop('savename','')
        nofill = kwargs.pop('nofill',False)
        analysis = self.analysisDict[histName]
        numBins = len(variables)
        histTitle = 'h_{0}_{1}'.format(savename.replace('/','_'),histName)
        hist = ROOT.TH1D(histTitle,histTitle,numBins,0,numBins)
        for b,variable in enumerate(variables):
            varHist = self._getHistogram(histName,variable,analysis=analysis)
            if not varHist:
               hist.SetBinContent(b+1,0)
               hist.SetBinError(b+1,0)
            else:
               integral = varHist.Integral()
               err2 = 0.
               for hb in range(varHist.GetNbinsX()):
                   err2 += varHist.GetBinError(hb+1)**2
               hist.SetBinContent(b+1,integral)
               hist.SetBinError(b+1,err2**0.5)
        style = self.styles[histName]
        hist.SetTitle(style['name'])
        if 'linecolor' in style:
            hist.SetLineColor(style['linecolor'])
            hist.SetMarkerColor(style['linecolor'])
        if 'linestyle' in style:
            hist.SetLineStyle(style['linestyle'])
        if not nofill:
            if 'fillstyle' in style: hist.SetFillStyle(style['fillstyle'])
            if 'fillcolor' in style: hist.SetFillColor(style['fillcolor'])
        return hist


    def _get2DHistogram(self,histName,variable,**kwargs):
        '''Get a styled histogram'''
        rebinx = kwargs.pop('rebinx',0)
        rebiny = kwargs.pop('rebiny',0)
        analysis = self.analysisDict[histName]
        # check if it is a variable map
        varName = variable if isinstance(variable,basestring) else variable[histName]
        if histName in self.histDict:
            hists = ROOT.TList()
            for sampleName in self.histDict[histName]:
                hist = self._readSampleVariable(sampleName,varName,analysis=analysis)
                if hist: hists.Add(hist)
            if hists.IsEmpty(): return 0
            hist = hists[0].Clone('h_{0}_{1}'.format(histName,varName.replace('/','_')))
            hist.Reset()
            hist.Merge(hists)
            if rebinx: hist = hist.RebinX(rebinx)
            if rebiny: hist = hist.RebinY(rebiny)
            style = self.styles[histName]
            hist.SetTitle(style['name'])
            return hist
        else:
            logging.error('{0} not defined.'.format(histName))
            return 0

    def _getStack(self,variable,**kwargs):
        '''Get a stack of histograms'''
        self.j += 1
        stackname = 'h_stack_{0}'.format(self.j)
        stack = ROOT.THStack(stackname,stackname)
        logging.debug('Reading stack')
        for histName in self.stackOrder:
            hist = self._getHistogram(histName,variable,**kwargs)
            if hist: stack.Add(hist)
        return stack

    def _getStackCounts(self,variables,**kwargs):
        '''Get a stack of histograms'''
        savename = kwargs.pop('savename','')
        self.j += 1
        stackname = 'h_stack_{0}'.format(self.j)
        stack = ROOT.THStack(stackname,stackname)
        for histName in self.stackOrder:
            hist = self._getHistogramCounts(histName,variables,savename=savename,**kwargs)
            if hist: stack.Add(hist)
        return stack

    def _get_stat_err(self, hist):
        '''Create statistical errorbars froma histogram'''
        staterr = hist.Clone("{0}_staterr".format(hist.GetName))
        staterr.SetFillColor(ROOT.kGray+3)
        staterr.SetLineColor(ROOT.kGray+3)
        staterr.SetLineWidth(0)
        staterr.SetMarkerSize(0)
        staterr.SetFillStyle(3013)
        return staterr

    def _get_ratio_stat_err(self, hist, **kwargs):
        '''Return a statistical error bars for a ratio plot'''
        ratiomin = kwargs.pop('ratiomin',0.5)
        ratiomax = kwargs.pop('ratiomax',1.5)
        ratiostaterr = hist.Clone("{0}_ratiostaterr".format(hist.GetName))
        #ratiostaterr.Sumw2()
        ratiostaterr.SetStats(0)
        ratiostaterr.SetTitle("")
        #ratiostaterr.GetYaxis().SetTitle("Data / MC")
        ratiostaterr.GetYaxis().SetTitle("Obs / Exp")
        ratiostaterr.SetMaximum(ratiomax)
        ratiostaterr.SetMinimum(ratiomin)
        ratiostaterr.SetMarkerSize(0)
        ratiostaterr.SetFillColor(ROOT.kGray+3)
        ratiostaterr.SetFillStyle(3013)
        ratiostaterr.GetXaxis().SetLabelSize(0.19)
        ratiostaterr.GetXaxis().SetTitleSize(0.21)
        ratiostaterr.GetXaxis().SetTitleOffset(1.0)
        ratiostaterr.GetXaxis().SetLabelOffset(0.03)
        ratiostaterr.GetYaxis().SetLabelSize(0.19)
        ratiostaterr.GetYaxis().SetLabelOffset(0.006)
        ratiostaterr.GetYaxis().SetTitleSize(0.21)
        ratiostaterr.GetYaxis().SetTitleOffset(0.35)
        ratiostaterr.GetYaxis().SetNdivisions(503)

        # bin by bin errors
        for i in range(hist.GetNbinsX()+2):
            ratiostaterr.SetBinContent(i, 1.0)
            if hist.GetBinContent(i)>1e-6:  # not empty
                binerror = hist.GetBinError(i) / hist.GetBinContent(i)
                ratiostaterr.SetBinError(i, binerror)
            else:
                ratiostaterr.SetBinError(i, 999.)

        return ratiostaterr

    def _get_ratio_err(self,num,denom,data=False):
        '''Return the ratio of two histograms, taking errors from numerator only'''
        if data:
            # get ratio between two hists with poisson errors
            graph = ROOT.TGraphAsymmErrors(num.GetNbinsX())
            chisqr = ROOT.TMath.ChisquareQuantile
            npoints = 0
            for bin in range(num.GetNbinsX()):
                entries = num.GetBinContent(bin+1)
                denomentries = denom.GetBinContent(bin+1)
                if entries <= 0:
                    entries = 0
                ey_low = entries - 0.5 * chisqr(0.1586555, 2. * entries)
                ey_high = 0.5 * chisqr(
                    1. - 0.1586555, 2. * (entries + 1)) - entries
                ex = num.GetBinWidth(bin+1) / 2.
                if denomentries > 0:
                    graph.SetPoint(npoints, num.GetBinCenter(bin+1), num.GetBinContent(bin+1)/denomentries)
                    graph.SetPointEXlow(npoints, 0)
                    graph.SetPointEXhigh(npoints, 0)
                    graph.SetPointEYlow(npoints, ey_low/denomentries)
                    graph.SetPointEYhigh(npoints, ey_high/denomentries)
                else:
                    graph.SetPoint(npoints, num.GetBinCenter(bin+1), 0)
                    graph.SetPointEXlow(npoints, 0)
                    graph.SetPointEXhigh(npoints, 0)
                    graph.SetPointEYlow(npoints, 0)
                    graph.SetPointEYhigh(npoints, 0)
                npoints += 1
            graph.Set(npoints)
            return graph
        else:
            self.j += 1
            newnum = num.Clone('ratio_{0}'.format(self.j))
            for b in range(num.GetNbinsX()):
                nVal = num.GetBinContent(b+1)
                nErr = num.GetBinError(b+1)
                dVal = denom.GetBinContent(b+1)
                if dVal>1e-6:
                    val = nVal/dVal
                    err = nErr/dVal
                else:
                    val = 0
                    err = 0
                newnum.SetBinContent(val)
                newnum.SetBinError(err)
            return newnum

    def _get_poisson_err(self,hist):
        # adapted from rootpy to get asymmetric poisson errors
        graph = ROOT.TGraphAsymmErrors(hist.GetNbinsX())
        chisqr = ROOT.TMath.ChisquareQuantile
        npoints = 0
        for bin in range(hist.GetNbinsX()):
            entries = hist.GetBinContent(bin+1)
            if entries <= 0:
                #continue
                entries = 0
            ey_low = entries - 0.5 * chisqr(0.1586555, 2. * entries)
            ey_high = 0.5 * chisqr(
                1. - 0.1586555, 2. * (entries + 1)) - entries
            ex = hist.GetBinWidth(bin+1) / 2.
            graph.SetPoint(npoints, hist.GetBinCenter(bin+1), hist.GetBinContent(bin+1))
            graph.SetPointEXlow(npoints, 0)
            graph.SetPointEXhigh(npoints, 0)
            graph.SetPointEYlow(npoints, ey_low)
            graph.SetPointEYhigh(npoints, ey_high)
            npoints += 1
        graph.Set(npoints)
        return graph

    def _getLegend(self,**kwargs):
        '''Get the legend'''
        stack = kwargs.pop('stack',None)
        hists = kwargs.pop('hists',{})
        entries = []
        if stack:
            for hist,name in zip(reversed(stack.GetHists()),reversed(self.stackOrder)):
                style = self.styles[name]
                entries += [[hist,hist.GetTitle(),style['legendstyle']]]
        if hists:
            for name,hist in hists.iteritems():
                style = self.styles[name]
                entries += [[hist,hist.GetTitle(),style['legendstyle']]]
        return super(Plotter,self)._getLegend(entries=entries,**kwargs)

    def plot(self,variable,savename,**kwargs):
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
        plotratio = kwargs.pop('plotratio',True)
        blinder = kwargs.pop('blinder',[])
        rangex = kwargs.pop('rangex',[])
        binlabels = kwargs.pop('binlabels',[])
        save = kwargs.pop('save',True)
        getHists = kwargs.pop('getHists',False)

        logging.info('Plotting {0}'.format(savename))

        ROOT.gDirectory.Delete('h_*')

        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        #ROOT.SetOwnership(canvas,False)

        # ratio plot
        if plotratio:
            plotpad = ROOT.TPad("plotpad", "top pad", 0.0, 0.21, 1.0, 1.0)
            #ROOT.SetOwnership(plotpad,False)
            plotpad.SetBottomMargin(0.04)
            plotpad.SetRightMargin(0.03)
            plotpad.Draw()
            plotpad.SetLogy(logy)
            plotpad.SetLogx(logx)
            ratiopad = ROOT.TPad("ratiopad", "bottom pad", 0.0, 0.0, 1.0, 0.21)
            #ROOT.SetOwnership(ratiopad,False)
            ratiopad.SetTopMargin(0.06)
            ratiopad.SetRightMargin(0.03)
            ratiopad.SetBottomMargin(0.5)
            ratiopad.SetLeftMargin(0.16)
            ratiopad.SetTickx(1)
            ratiopad.SetTicky(1)
            ratiopad.Draw()
            ratiopad.SetLogx(logx)
            if plotpad != ROOT.TVirtualPad.Pad(): plotpad.cd()
            #plotpad.cd()
        else:
            canvas.SetLogy(logy)
            canvas.SetLogx(logx)


        highestMax = -9999999.
        lowestMin = 9999999.

        # stack
        stack = 0
        if self.stackOrder:
            stack = self._getStack(variable,**kwargs)
            highestMax = max(highestMax,stack.GetMaximum())
            #bins={}
            #for hist in stack.GetHists():
            #    for x in range(hist.GetNbinsX()):
            #        if x not in bins: bins[x] = 0.
            #        bins[x] += hist.GetBinContent(x+1)
            #lowestMin = min([lowestMin]+[bins[x] for x in bins if bins[x]>0])

        # overlay histograms
        hists = OrderedDict()
        for histName in self.histOrder:
            hist = self._getHistogram(histName,variable,nofill=True,**kwargs)
            if not hist: logging.error('Failed to find hist {0} {1}'.format(histName,variable))
            if histName=='data':
                hist.SetMarkerStyle(20)
                hist.SetMarkerSize(1.)
                hist.SetLineColor(ROOT.kBlack)
                if len(blinder)==2:
                    lowbin = hist.FindBin(blinder[0])
                    highbin = hist.FindBin(blinder[1])
                    for b in range(highbin-lowbin+1):
                        hist.SetBinContent(b+lowbin,0.)
                        hist.SetBinError(b+lowbin,0.)
                hist.SetBinErrorOption(ROOT.TH1.kPoisson)
            else:
                hist.SetLineWidth(3)
            if histName in self.histScales:
                hist.Scale(self.histScales[histName])
                name = hist.GetTitle()
                name += ' (x{0})'.format(self.histScales[histName])
                hist.SetTitle(name)
            highestMax = max(highestMax,hist.GetMaximum())
            if histName=='data': lowestMin = min([lowestMin]+[hist.GetBinContent(x) for x in range(hist.GetNbinsX()) if hist.GetBinContent(x)>0])
            hists[histName] = hist

        if getHists:
            return stack, hists

        # now draw them
        logging.debug('Drawing')
        if self.stackOrder:
            stack.Draw("hist")
            stack.GetXaxis().SetTitle(xaxis)
            stack.GetYaxis().SetTitle(yaxis)
            stack.SetMaximum(yscale*highestMax)
            stack.GetYaxis().SetLabelSize(0.05)
            if len(rangex)==2: stack.GetXaxis().SetRangeUser(*rangex)
            if binlabels:
                for b,label in enumerate(binlabels):
                    stack.GetXaxis().SetBinLabel(b+1,label)
            if ymax!=None: stack.SetMaximum(ymax)
            if ymin!=None:
                stack.SetMinimum(ymin)
            elif logy and lowestMin<highestMax:
                stack.SetMinimum(lowestMin)
            if plotratio: stack.GetHistogram().GetXaxis().SetLabelOffset(999)
            self.j += 1
            staterr = self._get_stat_err(stack.GetStack().Last().Clone('h_stack_{0}'.format(self.j)))
            staterr.Draw('e2 same')
            for histName,hist in hists.iteritems():
                style = self.styles[histName]
                hist.Draw(style['drawstyle']+' same')
        else:
            first = True
            for histName,hist in hists.iteritems():
                style = self.styles[histName]
                if first:
                    first = False
                    hist.Draw(style['drawstyle'])
                    hist.GetXaxis().SetTitle(xaxis)
                    hist.GetYaxis().SetTitle(yaxis)
                    hist.SetMaximum(yscale*highestMax)
                    hist.GetYaxis().SetLabelSize(0.05)
                    if len(rangex)==2: hist.GetXaxis().SetRangeUser(*rangex)
                    if ymax!=None: hist.SetMaximum(ymax)
                    if ymin!=None: hist.SetMinimum(ymin)
                    if plotratio: hist.GetXaxis().SetLabelOffset(999)
                else:
                    hist.Draw(style['drawstyle']+' same')

        # get the legend
        logging.debug('Legend')
        legend = self._getLegend(stack=stack,hists=hists,numcol=numcol,position=legendpos)
        legend.Draw()

        # cms lumi styling
        logging.debug('CMSLumi')
        pad = plotpad if plotratio else canvas
        if pad != ROOT.TVirtualPad.Pad(): pad.cd()
        self._setStyle(pad,position=lumipos,preliminary=isprelim)

        # the ratio portion
        if plotratio:
            logging.debug('Making Ratio')
            self.j += 1
            stackname = 'h_stack_{0}_ratio'.format(self.j)
            if stack:
                denom = stack.GetStack().Last().Clone(stackname)
            else:
                denom = hists.items()[0][1].Clone(stackname)
            ratiostaterr = self._get_ratio_stat_err(denom)
            ratiostaterr.SetXTitle(xaxis)
            unityargs = [rangex[0],1,rangex[1],1] if len(rangex)==2 else [denom.GetXaxis().GetXmin(),1,denom.GetXaxis().GetXmax(),1]
            ratiounity = ROOT.TLine(*unityargs)
            ratiounity.SetLineStyle(2)
            ratios = OrderedDict()
            for histName, hist in hists.iteritems():
                self.j += 1
                numname = 'h_{0}_{1}_ratio'.format(histName,self.j)
                if histName in self.signals:
                    sighists = ROOT.TList()
                    sighists.Add(hist)
                    sighists.Add(denom)
                    num = sighists[0].Clone(numname)
                    num.Reset()
                    num.Merge(sighists)
                else:
                    num = hist.Clone(numname)
                numratio = self._get_ratio_err(num,denom,data=histName=='data')
                ratios[histName] = numratio

            # and draw
            if ratiopad != ROOT.TVirtualPad.Pad(): ratiopad.cd()
            #ratiopad.cd()
            ratiostaterr.Draw("e2")
            if len(rangex)==2: ratiostaterr.GetXaxis().SetRangeUser(*rangex)
            if binlabels:
                for b,label in enumerate(binlabels):
                    ratiostaterr.GetXaxis().SetBinLabel(b+1,label)
            ratiounity.Draw('same')
            for histName, hist in ratios.iteritems():
                if histName=='data':
                    #hist.Draw('e0 same')
                    hist.Draw('0P same')
                else:
                    hist.SetLineWidth(3)
                    hist.Draw('hist same')
            #if canvas != ROOT.TVirtualPad.Pad(): canvas.cd()
            ##canvas.cd()

        # save
        if save:
            self._save(canvas,savename)
            logging.debug('Done')
            return 0
        else:
            return self._saveTemp(canvas)

    def plotCounts(self,bins,labels,savename,**kwargs):
        '''Plot a histogram of counts for each bin and save'''
        xaxis = kwargs.pop('xaxis', '')
        yaxis = kwargs.pop('yaxis', 'Events')
        logy = kwargs.pop('logy',False)
        logx = kwargs.pop('logx',False)
        ymin = kwargs.pop('ymin',None)
        ymax = kwargs.pop('ymax',None)
        yscale = kwargs.pop('yscale',5 if logy else 1.2)
        numcol = kwargs.pop('numcol',1)
        labelsOption = kwargs.pop('labelsOption','')
        legendpos = kwargs.pop('legendpos',33)
        lumipos = kwargs.pop('lumipos',11)
        isprelim = kwargs.pop('preliminary',True)
        plotratio = kwargs.pop('plotratio',True)
        save = kwargs.pop('save',True)

        logging.info('Plotting {0}'.format(savename))
        ROOT.gDirectory.Delete('h_*')

        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        #ROOT.SetOwnership(canvas,False)

        # ratio plot
        if plotratio:
            plotpad = ROOT.TPad("plotpad", "top pad", 0.0, 0.21, 1.0, 1.0)
            #ROOT.SetOwnership(plotpad,False)
            plotpad.SetBottomMargin(0.04)
            plotpad.Draw()
            plotpad.SetLogy(logy)
            plotpad.SetLogx(logx)
            ratiopad = ROOT.TPad("ratiopad", "bottom pad", 0.0, 0.0, 1.0, 0.21)
            #ROOT.SetOwnership(ratiopad,False)
            ratiopad.SetTopMargin(0.06)
            ratiopad.SetBottomMargin(0.5)
            ratiopad.SetTickx(1)
            ratiopad.SetTicky(1)
            ratiopad.Draw()
            ratiopad.SetLogx(logx)
            if plotpad != ROOT.TVirtualPad.Pad(): plotpad.cd()
            #plotpad.cd()
        else:
            canvas.SetLogy(logy)
            canvas.SetLogx(logx)

        highestMax = -9999999.

        # stack
        stack = ROOT.THStack()
        if self.stackOrder:
            stack = self._getStackCounts(bins,savename=savename,**kwargs)
            highestMax = max(highestMax,stack.GetMaximum())

        # overlay histograms
        hists = OrderedDict()
        for histName in self.histOrder:
            hist = self._getHistogramCounts(histName,bins,nofill=True,**kwargs)
            if histName=='data':
                hist.SetMarkerStyle(20)
                hist.SetMarkerSize(1.)
                hist.SetLineColor(ROOT.kBlack)
                hist.SetBinErrorOption(ROOT.TH1.kPoisson)
            else:
                hist.SetLineWidth(3)
            if histName in self.histScales:
                hist.Scale(self.histScales[histName])
                name = hist.GetTitle()
                name += ' (x{0})'.format(self.histScales[histName])
                hist.SetTitle(name)
            highestMax = max(highestMax,hist.GetMaximum())
            hists[histName] = hist

        # now draw them
        if self.stackOrder:
            stack.Draw("hist")
            stack.GetXaxis().SetTitle(xaxis)
            stack.GetYaxis().SetTitle(yaxis)
            stack.SetMaximum(yscale*highestMax)
            for b,label in enumerate(labels):
                stack.GetHistogram().GetXaxis().SetBinLabel(b+1,label)
            if ymax!=None: stack.SetMaximum(ymax)
            if ymin!=None: stack.SetMinimum(ymin)
            if labelsOption: stack.GetHistogram().GetXaxis().LabelsOption(labelsOption)
            if plotratio: stack.GetHistogram().GetXaxis().SetLabelOffset(999)
            self.j += 1
            staterr = self._get_stat_err(stack.GetStack().Last().Clone('h_stack_{0}'.format(self.j)))
            staterr.Draw('e2 same')
        for histName,hist in hists.iteritems():
            style = self.styles[histName]
            hist.Draw(style['drawstyle']+' same')

        # get the legend
        legend = self._getLegend(stack=stack,hists=hists,numcol=numcol,position=legendpos)
        legend.Draw()

        # cms lumi styling
        pad = plotpad if plotratio else canvas
        if pad != ROOT.TVirtualPad.Pad(): pad.cd()
        self._setStyle(pad,position=lumipos,preliminary=isprelim)

        # cms lumi styling
        pad = plotpad if plotratio else canvas
        if pad != ROOT.TVirtualPad.Pad(): pad.cd()
        self._setStyle(pad,position=lumipos,preliminary=isprelim)

        # the ratio portion
        if plotratio:
            denom = stack.GetStack().Last().Clone('h_stack_{0}_ratio'.format(savename.replace('/','_')))
            ratiostaterr = self._get_ratio_stat_err(denom)
            ratiostaterr.SetXTitle(xaxis)
            for b,label in enumerate(labels):
                ratiostaterr.GetXaxis().SetBinLabel(b+1,label)
            if labelsOption: ratiostaterr.GetXaxis().LabelsOption(labelsOption)
            unityargs = [stack.GetXaxis().GetXmin(),1,stack.GetXaxis().GetXmax(),1]
            ratiounity = ROOT.TLine(*unityargs)
            ratiounity.SetLineStyle(2)
            ratios = OrderedDict()
            for histName, hist in hists.iteritems():
                if histName in self.signals:
                    sighists = ROOT.TList()
                    sighists.Add(hist)
                    sighists.Add(denom)
                    num = sighists[0].Clone('h_{0}_{1}_ratio'.format(histName,savename.replace('/','_')))
                    num.Reset()
                    num.Merge(sighists)
                else:
                    num = hist.Clone('h_{0}_{1}_ratio'.format(histName,savename.replace('/','_')))
                numratio = self._get_ratio_err(num,denom,data=histName=='data')
                ratios[histName] = numratio

            # and draw
            if ratiopad != ROOT.TVirtualPad.Pad(): ratiopad.cd()
            #ratiopad.cd()
            ratiostaterr.Draw("e2")
            ratiounity.Draw('same')
            for histName, hist in ratios.iteritems():
                if histName=='data':
                    #hist.Draw('e0 same')
                    hist.Draw('0P same')
                else:
                    hist.SetLineWidth(3)
                    hist.Draw('hist same')
            #if canvas != ROOT.TVirtualPad.Pad(): canvas.cd()
            #canvas.cd()

        # save
        if save:
            self._save(canvas,savename)
        else:
            return self._saveTemp(canvas)


    def plotRatio(self,numerator,denominator,savename,**kwargs):
        '''Plot a ratio of two variables and save'''
        xaxis = kwargs.pop('xaxis', 'Variable')
        yaxis = kwargs.pop('yaxis', 'Efficiency')
        logy = kwargs.pop('logy',False)
        logx = kwargs.pop('logx',False)
        ymin = kwargs.pop('ymin',None)
        ymax = kwargs.pop('ymax',None)
        yscale = kwargs.pop('yscale',5 if logy else 1.2)
        numcol = kwargs.pop('numcol',1)
        legendpos = kwargs.pop('legendpos',34)
        customOrder = kwargs.pop('customOrder',[])
        subtractMap = kwargs.pop('subtractMap',{})
        getHists = kwargs.pop('getHists', False)
        save = kwargs.pop('save',True)

        logging.info('Plotting {0}'.format(savename))

        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        #ROOT.SetOwnership(canvas,False)
        canvas.SetLogy(logy)
        canvas.SetLogx(logx)

        highestMax = 0.

        hists = OrderedDict()
        histOrder = customOrder if customOrder else self.histOrder
        
        for i,histName in enumerate(histOrder):
            num = self._getHistogram(histName,numerator,nofill=True,**kwargs)
            denom = self._getHistogram(histName,denominator,nofill=True,**kwargs)
            if histName in subtractMap:
                for subName in subtractMap[histName]:
                    numsub = self._getHistogram(subName,numerator,nofill=True,**kwargs)
                    num.Add(numsub,-1)
                    denomsub = self._getHistogram(subName,denominator,nofill=True,**kwargs)
                    denom.Add(denomsub,-1)
            num.Sumw2()
            denom.Sumw2()
            num.Divide(denom)
            num.SetLineWidth(3)
            style = self.styles[histName]
            if i==0:
                num.Draw('e0')
                num.GetXaxis().SetTitle(xaxis)
                num.GetYaxis().SetTitle(yaxis)
                num.GetYaxis().SetTitleOffset(1.5)
                num.SetMinimum(0.)
                if ymax!=None: num.SetMaximum(ymax)
                if ymin!=None: num.SetMinimum(ymin)
            else:
                num.Draw('e0 same')
            highestMax = max(highestMax,num.GetMaximum())
            if ymax==None: num.SetMaximum(yscale*highestMax)
            hists[histName] = num

        if getHists: return hists

        legend = self._getLegend(hists=hists,numcol=numcol,position=legendpos)
        legend.Draw()

        self._setStyle(canvas)

        # save
        if save:
            self._save(canvas,savename)
        else:
            return self._saveTemp(canvas)

    def plotSOverB(self,variable,signals,backgrounds,savename,**kwargs):
        '''Plot ROC curve'''
        xaxis = kwargs.pop('xaxis', 'Variable')
        yaxis = kwargs.pop('yaxis', 'Signal over background')
        logy = kwargs.pop('logy',False)
        logx = kwargs.pop('logx',False)
        invert = kwargs.pop('invert',False)
        yscale = kwargs.pop('yscale',5 if logy else 1.2)
        ymin = kwargs.pop('ymin',None)
        ymax = kwargs.pop('ymax',None)
        numcol = kwargs.pop('numcol',1)
        legendpos = kwargs.pop('legendpos',34)
        save = kwargs.pop('save',True)

        logging.info('Plotting {0}'.format(savename))
        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        #ROOT.SetOwnership(canvas,False)
        canvas.SetLogy(logy)
        canvas.SetLogx(logx)

        canvas.SetLogy(True)

        if isinstance(signals,str): signals = [signals]
        if isinstance(backgrounds,str): backgrounds = [backgrounds]*len(signals)

        highestMax = 0.
        lowestMin = 999999.
        hists = OrderedDict()

        for i,histNames in enumerate(zip(signals,backgrounds)):
            signal, background = histNames
            sig = self._getHistogram(signal,variable,nofill=True,**kwargs)
            bg = self._getHistogram(background,variable,nofill=True,**kwargs)
            numBins = sig.GetNbinsX()
            self.j += 1
            name = 'h_sOverB_{0}'.format(self.j)
            sOverB = ROOT.TH1D(name,name,numBins,sig.GetXaxis().GetXmin(),sig.GetXaxis().GetXmax())
            thisMin = 999999.
            for b in range(numBins):
                blow = 1 if invert else b+1
                bhigh = b+1 if invert else numBins
                sigVal = 0
                sigErr2 = 0
                bgVal = 0
                bgErr2 = 0
                for j in range(blow,bhigh+1):
                    sigVal += sig.GetBinContent(j)
                    sigErr2 += sig.GetBinError(j)**2
                    bgVal += bg.GetBinContent(j)
                    bgErr2 += bg.GetBinError(j)**2
                sOverBVal = divWithError((sigVal,sigErr2**0.5),(bgVal,bgErr2**0.5))
                if sOverBVal>0: thisMin = min(thisMin,sOverBVal)
                sOverB.SetBinContent(b+1,sOverBVal[0])
                sOverB.SetBinError(b+1,sOverBVal[1])
            lowestMin = min(lowestMin,thisMin)
            sOverB.SetMinimum(lowestMin)
            style = self.styles[signal]
            sOverB.SetLineWidth(2)
            sOverB.SetLineColor(style['linecolor'])
            sOverB.SetMarkerColor(style['linecolor'])
            sOverB.SetFillColor(0)
            if i==0:
                sOverB.Draw('e0')
                sOverB.GetXaxis().SetTitle(xaxis)
                sOverB.GetYaxis().SetTitle(yaxis)
                sOverB.GetYaxis().SetTitleOffset(1.2)
                #sOverB.SetMinimum(0.)
                if ymax!=None: sOverB.SetMaximum(ymax)
                if ymin!=None: sOverB.SetMinimum(ymin)
            else:
                sOverB.Draw('e0 same')
            sOverB.SetTitle(style['name'])
            #highestMax = max(highestMax,sOverB.GetMaximum())
            #if ymax==None: sOverB.SetMaximum(yscale*highestMax)
            hists[signal] = sOverB

        legend = self._getLegend(hists=hists,numcol=numcol,position=legendpos)
        legend.Draw()

        self._setStyle(canvas)

        # save
        if save:
            self._save(canvas,savename)
        else:
            return self._saveTemp(canvas)

    def plotSignificance(self,variable,signals,backgrounds,savename,**kwargs):
        '''Plot ROC curve'''
        xaxis = kwargs.pop('xaxis', 'Variable')
        yaxis = kwargs.pop('yaxis', 'Significance')
        logy = kwargs.pop('logy',False)
        logx = kwargs.pop('logx',False)
        invert = kwargs.pop('invert',False)
        yscale = kwargs.pop('yscale',5 if logy else 1.2)
        ymin = kwargs.pop('ymin',None)
        ymax = kwargs.pop('ymax',2)
        numcol = kwargs.pop('numcol',3)
        legendpos = kwargs.pop('legendpos',34)
        save = kwargs.pop('save',True)

        logging.info('Plotting {0}'.format(savename))
        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        #ROOT.SetOwnership(canvas,False)
        canvas.SetLogy(logy)
        canvas.SetLogx(logx)

        canvas.SetLogy(True)

        if isinstance(signals,str): signals = [signals]
        if isinstance(backgrounds,str): backgrounds = [backgrounds]*len(signals)

        highestMax = 0.
        lowestMin = 999999.
        hists = OrderedDict()

        for i,histNames in enumerate(zip(signals,backgrounds)):
            signal, background = histNames
            sig = self._getHistogram(signal,variable,nofill=True,**kwargs)
            bg = self._getHistogram(background,variable,nofill=True,**kwargs)
            numBins = sig.GetNbinsX()
            self.j += 1
            name = 'h_sOverB_{0}'.format(self.j)
            significance = ROOT.TH1D(name,name,numBins,sig.GetXaxis().GetXmin(),sig.GetXaxis().GetXmax())
            thisMin = 999999.
            for b in range(numBins):
                blow = 1 if invert else b+1
                bhigh = b+1 if invert else numBins
                sigVal = 0
                sigErr2 = 0
                bgVal = 0
                bgErr2 = 0
                for j in range(blow,bhigh+1):
                    sigVal += sig.GetBinContent(j)
                    sigErr2 += sig.GetBinError(j)**2
                    bgVal += bg.GetBinContent(j)
                    bgErr2 += bg.GetBinError(j)**2
                significanceVal = sigVal / (sigVal+bgVal) if sigVal+bgVal else 0.
                if significanceVal>0: thisMin = min(thisMin,significanceVal)
                significance.SetBinContent(b+1,significanceVal)
                significance.SetBinError(b+1,0.)
            lowestMin = min(lowestMin,thisMin)
            significance.SetMinimum(lowestMin)
            style = self.styles[signal]
            significance.SetLineWidth(2)
            significance.SetLineColor(style['linecolor'])
            significance.SetMarkerColor(style['linecolor'])
            significance.SetFillColor(0)
            if i==0:
                significance.Draw('e0')
                significance.GetXaxis().SetTitle(xaxis)
                significance.GetYaxis().SetTitle(yaxis)
                significance.GetYaxis().SetTitleOffset(1.2)
                if ymax!=None: significance.SetMaximum(ymax)
                if ymin!=None: significance.SetMinimum(ymin)
            else:
                significance.Draw('e0 same')
            significance.SetTitle(style['name'])
            hists[signal] = significance

        legend = self._getLegend(hists=hists,numcol=numcol,position=legendpos)
        legend.Draw()

        self._setStyle(canvas)

        # save
        if save:
            self._save(canvas,savename)
        else:
            return self._saveTemp(canvas)


    def plotEfficiency(self,variable,savename,**kwargs):
        '''Plot ROC curve'''
        xaxis = kwargs.pop('xaxis', 'Variable')
        yaxis = kwargs.pop('yaxis', 'Efficiency')
        numcol = kwargs.pop('numcol',1)
        legendpos = kwargs.pop('legendpos',33)
        logy = kwargs.pop('logy',False)
        logx = kwargs.pop('logx',False)
        customOrder = kwargs.pop('customOrder',[])
        invert = kwargs.pop('invert',False)
        ymin = kwargs.pop('ymin',0)
        ymax = kwargs.pop('ymax',1.2)
        save = kwargs.pop('save',True)

        logging.info('Plotting {0}'.format(savename))
        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        #ROOT.SetOwnership(canvas,False)
        canvas.SetLogy(logy)
        canvas.SetLogx(logx)

        hists = OrderedDict()
        histOrder = customOrder if customOrder else self.histOrder
        for i,histName in enumerate(histOrder):
            sig = self._getHistogram(histName,variable,nofill=True,**kwargs)
            numBins = sig.GetNbinsX()
            sigEff = [0]*numBins
            sigVal = [0]*numBins
            totSig = sig.Integral()
            for b in range(numBins):
                sigEff[b] = sig.Integral(1,b+1)/totSig if invert else sig.Integral(b+1,numBins)/totSig
                sigVal[b] = sig.GetBinLowEdge(b+1)
            eff = ROOT.TGraph(numBins,array('f',sigVal),array('f',sigEff))
            style = self.styles[histName]
            eff.SetLineWidth(2)
            eff.SetLineColor(style['linecolor'])
            eff.SetMarkerColor(style['linecolor'])
            eff.SetFillColor(0)
            if i==0:
                eff.Draw('AL')
                eff.GetXaxis().SetTitle(xaxis)
                eff.GetYaxis().SetTitle(yaxis)
                eff.GetYaxis().SetTitleOffset(1.2)
                eff.SetMaximum(ymax)
                eff.SetMinimum(ymin)
            else:
                eff.Draw('L same')
            eff.SetTitle(style['name'])
            hists[histName] = eff

        legend = self._getLegend(hists=hists,numcol=numcol,position=legendpos)
        legend.Draw()

        self._setStyle(canvas)

        # save
        if save:
            self._save(canvas,savename)
        else:
            return self._saveTemp(canvas)

    def plotROC(self,signalVariable,backgroundVariable,savename,**kwargs):
        '''Plot ROC curve'''
        xaxis = kwargs.pop('xaxis', 'Signal Efficiency')
        yaxis = kwargs.pop('yaxis', 'Background Rejection')
        numcol = kwargs.pop('numcol',1)
        legendpos = kwargs.pop('legendpos',33)
        logy = kwargs.pop('logy',False)
        logx = kwargs.pop('logx',False)
        customOrder = kwargs.pop('customOrder',[])
        sigOrder = kwargs.pop('sigOrder',[])
        bgOrder = kwargs.pop('bgOrder',[])
        workingPoints = kwargs.pop('workingPoints',{})
        invert = kwargs.pop('invert',False)
        ymin = kwargs.pop('ymin',0)
        ymax = kwargs.pop('ymax',1.2)
        save = kwargs.pop('save',True)

        logging.info('Plotting {0}'.format(savename))
        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        #ROOT.SetOwnership(canvas,False)
        canvas.SetLogy(logy)
        canvas.SetLogx(logx)

        hists = OrderedDict()
        histOrder = customOrder if customOrder else self.histOrder
        sigHists = sigOrder if sigOrder and bgOrder and len(sigOrder)==len(bgOrder) else histOrder
        bgHists = bgOrder if sigOrder and bgOrder and len(sigOrder)==len(bgOrder) else histOrder
        wpStyles = [20,21,22,23,33,34,24,25,26,32,27,28]
        wpHists = []
        for i,(sigName,bgName) in enumerate(zip(sigHists,bgHists)):
            sig = self._getHistogram(sigName,signalVariable,nofill=True,**kwargs)
            bg = self._getHistogram(bgName,backgroundVariable,nofill=True,**kwargs)
            numBins = sig.GetNbinsX()
            sigEff = [0]*numBins
            bgEff = [0]*numBins
            totSig = sig.Integral()
            totBg = bg.Integral()
            for b in range(numBins):
                sigEff[b] = sig.Integral(1,b+1)/totSig if invert else sig.Integral(b+1,numBins)/totSig
                bgEff[b] = (totBg-bg.Integral(1,b+1))/totBg if invert else (totBg-bg.Integral(b+1,numBins))/totBg
            roc = ROOT.TGraph(numBins,array('f',sigEff),array('f',bgEff))
            style = self.styles[sigName]
            roc.SetLineWidth(2)
            roc.SetLineColor(style['linecolor'])
            roc.SetMarkerColor(style['linecolor'])
            roc.SetFillColor(0)
            if i==0:
                roc.Draw('AL')
                roc.GetXaxis().SetTitle(xaxis)
                roc.GetYaxis().SetTitle(yaxis)
                roc.GetYaxis().SetTitleOffset(1.2)
                roc.SetMaximum(ymax)
                roc.SetMinimum(ymin)
            else:
                roc.Draw('L same')
            roc.SetTitle(style['name'])
            hists[sigName] = roc
            # working points
            if sigName in workingPoints:
                for w,wp in enumerate(sorted(workingPoints[sigName])):
                    wpbin = max(1,sig.FindBin(workingPoints[sigName][wp]))
                    wpgraph = ROOT.TGraph(1,array('f',[sigEff[wpbin-1]]),array('f',[bgEff[wpbin-1]]))
                    wpgraph.SetMarkerColor(style['linecolor'])
                    wpgraph.SetMarkerStyle(wpStyles[w])
                    wpgraph.Draw('P same')
                    wpHists += [wpgraph]

        legend = self._getLegend(hists=hists,numcol=numcol,position=legendpos)
        legend.Draw()

        if sigName in workingPoints:
            wpEntries = []
            for w,wp in enumerate(sorted(workingPoints[sigName])):
                hist = ROOT.TGraph(1,array('f',[0]),array('f',[0]))
                hist.SetMarkerStyle(wpStyles[w])
                wpEntries += [[hist,wp,'P']]
                
            wpLegend = super(Plotter,self)._getLegend(entries=wpEntries,position=11,numcol=2)
            wpLegend.Draw()

        self._setStyle(canvas)

        # save
        if save:
            self._save(canvas,savename)
        else:
            return self._saveTemp(canvas)

    def plotNormalized(self,variable,savename,**kwargs):
        '''Plot a ratio of two variables and save'''
        xaxis = kwargs.pop('xaxis', 'Variable')
        yaxis = kwargs.pop('yaxis', 'Events')
        ymin = kwargs.pop('ymin',None)
        ymax = kwargs.pop('ymax',None)
        numcol = kwargs.pop('numcol',1)
        legendpos = kwargs.pop('legendpos',33)
        logy = kwargs.pop('logy',False)
        logx = kwargs.pop('logx',False)
        rangex = kwargs.pop('rangex',[])
        customOrder = kwargs.pop('customOrder',[])
        subtractMap = kwargs.pop('subtractMap',{})
        save = kwargs.pop('save',True)

        logging.info('Plotting {0}'.format(savename))
        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        #ROOT.SetOwnership(canvas,False)
        canvas.SetLogy(logy)
        canvas.SetLogx(logx)

        highestMax = 0.

        hists = OrderedDict()
        histOrder = customOrder if customOrder else self.histOrder
        for i,histName in enumerate(histOrder):
            hist = self._getHistogram(histName,variable,nofill=True,**kwargs)
            if histName in subtractMap:
                for subName in subtractMap[histName]:
                    histsub = self._getHistogram(subName,variable,nofill=True,**kwargs)
                    hist.Add(histsub,-1)
            if hist.Integral(): hist.Scale(1./hist.Integral())
            hist.SetLineWidth(3)
            highestMax = max(highestMax,hist.GetMaximum())
            if ymax==None: hist.SetMaximum(1.2*highestMax)
            hists[histName] = hist

        for i,histName in enumerate(histOrder):
            hist = hists[histName]
            style = self.styles[histName]
            if i==0:
                hist.Draw(style['drawstyle'])
                hist.GetXaxis().SetTitle(xaxis)
                hist.GetYaxis().SetTitle(yaxis)
                hist.GetYaxis().SetTitleOffset(1.5)
                if len(rangex)==2: hist.GetXaxis().SetRangeUser(*rangex)
                if ymax!=None: hist.SetMaximum(ymax)
                if ymin!=None: hist.SetMinimum(ymin)
                if ymax==None: hist.SetMaximum(1.2*highestMax)
            else:
                hist.Draw(style['drawstyle']+' same')

        legend = self._getLegend(hists=hists,numcol=numcol,position=legendpos)
        legend.Draw()

        self._setStyle(canvas)

        # save
        if save:
            self._save(canvas,savename)
        else:
            return self._saveTemp(canvas)

    def plot2D(self,variable,savename,**kwargs):
        '''Plot a variable and save'''
        xaxis = kwargs.pop('xaxis', 'Variable')
        yaxis = kwargs.pop('yaxis', 'Events')
        ymin = kwargs.pop('ymin',None)
        ymax = kwargs.pop('ymax',None)
        numcol = kwargs.pop('numcol',1)
        legendpos = kwargs.pop('legendpos',33)
        logy = kwargs.pop('logy',False)
        logx = kwargs.pop('logx',False)
        logz = kwargs.pop('logz',False)
        save = kwargs.pop('save',True)

        logging.info('Plotting {0}'.format(savename))
        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        #ROOT.SetOwnership(canvas,False)
        canvas.SetLogy(logy)
        canvas.SetLogx(logx)
        canvas.SetLogz(logz)
        canvas.SetRightMargin(0.14) # for Z axis


        highestMax = 0.

        hists = OrderedDict()
        for i,histName in enumerate(self.histOrder):
            hist = self._get2DHistogram(histName,variable,**kwargs)
            hist.Draw('colz')
            if i==0:
                hist.GetXaxis().SetTitle(xaxis)
                hist.GetYaxis().SetTitle(yaxis)
                hist.GetYaxis().SetTitleOffset(1.5)
            hists[histName] = hist

        #legend = self._getLegend(stack=stack,hists=hists,numcol=numcol,position=legendpos)
        #legend.Draw()

        self._setStyle(canvas,position=0)

        # save
        if save:
            self._save(canvas,savename)
        else:
            return self._saveTemp(canvas)

    def plotEnvelope(self,variable,savename,xvalMap,envelopePoints,**kwargs):
        xaxis = kwargs.pop('xaxis', 'Variable')
        yaxis = kwargs.pop('yaxis', 'Variable')
        ymin = kwargs.pop('ymin',None)
        ymax = kwargs.pop('ymax',None)
        numcol = kwargs.pop('numcol',1)
        legendpos = kwargs.pop('legendpos',33)
        lumipos = kwargs.pop('lumipos',11)
        logy = kwargs.pop('logy',False)
        logx = kwargs.pop('logx',False)
        save = kwargs.pop('save',True)
        envelopeStyles = kwargs.pop('envelopeStyles',[])
        envelopeColors = kwargs.pop('envelopeColors',[])
        envelopeLabels = kwargs.pop('envelopeLabels',[])
        fitFunctions = kwargs.pop('fitFunctions',[])

        logging.info('Plotting {0}'.format(savename))
        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        #ROOT.SetOwnership(canvas,False)
        canvas.SetLogy(logy)
        canvas.SetLogx(logx)


        xpoints = sorted(xvalMap.keys())

        envelopes = {e:{} for e in envelopePoints}

        hists = OrderedDict()
        for x,histName in sorted(xvalMap.iteritems()):
            hist = self._getHistogram(histName,variable,**kwargs)
            hists[x] = hist
            total = hist.Integral()
            for b in range(hist.GetNbinsX()):
                thisInt = hist.Integral(0,b+1)
                ratio = thisInt/total if total else 0.
                for e in envelopePoints:
                    if ratio < e: envelopes[e][x] = hist.GetBinLowEdge(b+1)

        highestMax = max([max(envelopes[e].values()) for e in envelopePoints])

        envGraphs = OrderedDict()
        fits = {}
        newfits = {}
        for i,e in enumerate(envelopePoints):
            xvals = [x for x in sorted(envelopes[e])]
            yvals = [envelopes[e][x] for x in sorted(envelopes[e])]
            graph = ROOT.TGraph(len(xvals),array('d',xvals),array('d',yvals))
            if len(envelopeStyles)==len(envelopePoints): graph.SetLineStyle(envelopeStyles[i])
            if len(envelopeColors)==len(envelopePoints): graph.SetLineColor(envelopeColors[i])
            if len(envelopeLabels)==len(envelopePoints): graph.SetTitle(envelopeLabels[i])
            graph.SetLineWidth(2)
            if i==0:
                graph.SetMaximum(highestMax*1.1)
                graph.GetXaxis().SetTitle(xaxis)
                graph.GetYaxis().SetTitle(yaxis)
                graph.Draw("AL")
            else:
                graph.Draw("L same")
            #print 'Fitting {0} with pol1'.format(e)
            #fit = graph.Fit('pol1','SN')

            envGraphs[e] = graph
            #fits[e] = fit
           
            #if i==0:
            #    newfit = ROOT.TF1('f{0}'.format(e),'pol1',min(xvalMap.keys()),max(xvalMap.keys()))
            #    newfit.SetParameters(fit.GetParams())
            #    if len(envelopeColors)==len(envelopePoints): newfit.SetLineColor(envelopeColors[i])
            #    newfit.Draw("same")
            #    newfits[e] = newfit

        fits = OrderedDict()
        for i,fitFunction in enumerate(fitFunctions):
            fit = ROOT.TF1('f{0}'.format(i),*fitFunction[0:3])
            fit.SetParameters(*fitFunction[3:])
            fit.SetLineColor(1)
            fit.SetTitle('Selection')
            fit.Draw("same")
            fits[i] = fit
       
        entries = [[g,g.GetTitle(),'L'] for g in reversed(fits.values()+envGraphs.values())]
        legend = super(Plotter,self)._getLegend(entries=entries,numcol=numcol,position=legendpos)
        legend.Draw()

        self._setStyle(canvas,position=lumipos)

        # save
        if save:
            self._save(canvas,savename)
        else:
            return self._saveTemp(canvas)


    def plotMCDataRatio(self,stackVariableMap,dataVariable,savename,**kwargs):
        '''Plot a ratio of MC stack to Data'''
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
        blinder = kwargs.pop('blinder',[])
        rangex = kwargs.pop('rangex',[])
        binlabels = kwargs.pop('binlabels',[])
        save = kwargs.pop('save',True)

        logging.info('Plotting {0}'.format(savename))

        ROOT.gDirectory.Delete('h_*')
        ROOT.gStyle.SetOptFit(ROOT.kFALSE)

        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        #ROOT.SetOwnership(canvas,False)

        canvas.SetLogy(logy)
        canvas.SetLogx(logx)

        # histogram (denominator)
        data = self._getHistogram('data',dataVariable,nofill=True,**kwargs)
        data.SetMarkerStyle(20)
        data.SetMarkerSize(1.)
        data.SetLineColor(ROOT.kBlack)
        data.SetBinErrorOption(ROOT.TH1.kPoisson)

        # get ratios
        # stacks (numerators)
        stacks = OrderedDict()
        hists = OrderedDict()
        i = 0
        fitResults = {}
        for name,variable in stackVariableMap.iteritems():
            stacks[name] = self._getStack(variable,**kwargs)
            num = stacks[name].GetStack().Last()
            denom = data
            num.Sumw2()
            denom.Sumw2()
            num.Divide(denom)
            #num.SetLineWidth(3)
            style = self.styles[name]
            num.SetTitle(style['name'])
            if 'linecolor' in style:
                num.SetLineColor(style['linecolor'])
                num.SetMarkerColor(style['linecolor'])
            if 'linestyle' in style:
                num.SetLineStyle(style['linestyle'])
            if 'fillstyle' in style: num.SetFillStyle(style['fillstyle'])
            if 'fillcolor' in style: num.SetFillColor(style['fillcolor'])
            if i==0:
                num.Draw('e1 l')
                num.GetXaxis().SetTitle(xaxis)
                num.GetYaxis().SetTitle(yaxis)
                num.GetYaxis().SetTitleOffset(1.5)
                num.SetMinimum(0.)
                if ymax!=None: num.SetMaximum(ymax)
                if ymin!=None: num.SetMinimum(ymin)
            else:
                num.Draw('e1 l same')
            hists[name] = num
            i += 1

            fit = ROOT.TF1('line','pol0',10,100)
            num.Fit(fit,'0Q')
            fitResults[name] = fit.GetParameter(0)

        unityargs = [data.GetXaxis().GetXmin(),1,data.GetXaxis().GetXmax(),1]
        ratiounity = ROOT.TLine(*unityargs)
        ratiounity.SetLineStyle(2)
        ratiounity.Draw('same')

        #for i in range(data.GetNbinsX()+2):
        #    if data.GetBinContent(i)>1e-6:  # not empty
        #        bincontent = 1.
        #        binerror = data.GetBinError(i) / data.GetBinContent(i)
        #    else:
        #        bincontent = 0.
        #        binerror = 0.
        #    data.SetBinContent(i, bincontent)
        #    data.SetBinError(i, binerror)
        #data.Draw('e0 same')

        #hists['data'] = data

        # get the legend
        logging.debug('Legend')
        legend = self._getLegend(hists=hists,numcol=numcol,position=legendpos)
        legend.Draw()

        # cms lumi styling
        logging.debug('CMSLumi')
        self._setStyle(canvas,position=lumipos,preliminary=isprelim)


        # save
        if save:
            self._save(canvas,savename)
            logging.debug('Done')
            return fitResults
        else:
            return self._saveTemp(canvas)
