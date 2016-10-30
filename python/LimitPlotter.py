import os
import sys
import logging
import math
from array import array
from collections import OrderedDict

import ROOT

from DevTools.Plotter.PlotterBase import PlotterBase
from DevTools.Plotter.xsec import xsecs
from DevTools.Plotter.utilities import python_mkdir, getLumi
from DevTools.Plotter.style import getStyle
import DevTools.Plotter.CMS_lumi as CMS_lumi
import DevTools.Plotter.tdrstyle as tdrstyle
from DevTools.Limits.prevLimits import prevLimits, prevExpLimits

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
        asymptoticFilenames = kwargs.pop('asymptoticFilenames',[])
        smooth = kwargs.pop('smooth',False)

        logging.info('Plotting {0}'.format(savename))

        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        canvas.SetLogy(1)

        limits = self._readLimits(xvals,filenames)
        if not limits: return
        if asymptoticFilenames: limits_asym = self._readLimits(xvals,asymptoticFilenames)

        n = len(xvals)
        twoSigma = ROOT.TGraph(2*n)
        oneSigma = ROOT.TGraph(2*n)
        expected = ROOT.TGraph(n)
        observed = ROOT.TGraph(n)
        twoSigma_low = ROOT.TGraph(n)
        twoSigma_high = ROOT.TGraph(n)
        oneSigma_low = ROOT.TGraph(n)
        oneSigma_high = ROOT.TGraph(n)
        twoSigmaForSmoothing_low = ROOT.TGraph(n)
        twoSigmaForSmoothing_high = ROOT.TGraph(n)
        oneSigmaForSmoothing_low = ROOT.TGraph(n)
        oneSigmaForSmoothing_high = ROOT.TGraph(n)
        expectedForSmoothing = ROOT.TGraph(n)
        twoSigma_asym = ROOT.TGraph(2*n)
        oneSigma_asym = ROOT.TGraph(2*n)
        expected_asym = ROOT.TGraph(n)
        observed_asym = ROOT.TGraph(n)

        for i in range(len(xvals)):
            twoSigma.SetPoint(     i,   xvals[i],     limits[xvals[i]][0]) # 0.025
            oneSigma.SetPoint(     i,   xvals[i],     limits[xvals[i]][1]) # 0.16
            expected.SetPoint(     i,   xvals[i],     limits[xvals[i]][2]) # 0.5
            oneSigma.SetPoint(     n+i, xvals[n-i-1], limits[xvals[n-i-1]][3]) # 0.84
            twoSigma.SetPoint(     n+i, xvals[n-i-1], limits[xvals[n-i-1]][4]) # 0.975
            observed.SetPoint(     i,   xvals[i],     limits[xvals[i]][5]) # obs
            twoSigma_high.SetPoint(i,   xvals[i],     limits[xvals[i]][0]) # 0.025
            oneSigma_high.SetPoint(i,   xvals[i],     limits[xvals[i]][1]) # 0.16
            oneSigma_low.SetPoint( i,   xvals[n-i-1], limits[xvals[n-i-1]][3]) # 0.84
            twoSigma_low.SetPoint( i,   xvals[n-i-1], limits[xvals[n-i-1]][4]) # 0.975
            twoSigmaForSmoothing_high.SetPoint(i, xvals[i],     math.log(limits[xvals[i]][0])) # 0.025
            oneSigmaForSmoothing_high.SetPoint(i, xvals[i],     math.log(limits[xvals[i]][1])) # 0.16
            oneSigmaForSmoothing_low.SetPoint( i, xvals[n-i-1], math.log(limits[xvals[n-i-1]][3])) # 0.84
            twoSigmaForSmoothing_low.SetPoint( i, xvals[n-i-1], math.log(limits[xvals[n-i-1]][4])) # 0.975
            expectedForSmoothing.SetPoint(     i, xvals[i],     math.log(limits[xvals[i]][2])) # 0.5
            if asymptoticFilenames:
                twoSigma_asym.SetPoint(i,  xvals[i],     limits_asym[xvals[i]][0]) # 0.025
                oneSigma_asym.SetPoint(i,  xvals[i],     limits_asym[xvals[i]][1]) # 0.16
                expected_asym.SetPoint(i,  xvals[i],     limits_asym[xvals[i]][2]) # 0.5
                oneSigma_asym.SetPoint(n+i,xvals[n-i-1], limits_asym[xvals[n-i-1]][3]) # 0.84
                twoSigma_asym.SetPoint(n+i,xvals[n-i-1], limits_asym[xvals[n-i-1]][4]) # 0.975
                observed_asym.SetPoint(i,  xvals[i],     limits_asym[xvals[i]][5]) # obs

        if smooth: # smooth out the expected bands
            twoSigmaSmoother_low  = ROOT.TGraphSmooth()
            twoSigmaSmoother_high = ROOT.TGraphSmooth()
            oneSigmaSmoother_low  = ROOT.TGraphSmooth()
            oneSigmaSmoother_high = ROOT.TGraphSmooth()
            expectedSmoother      = ROOT.TGraphSmooth()
            #twoSigmaSmooth_low    = twoSigmaSmoother_low.Approx(twoSigma_low,  'linear',n)
            #twoSigmaSmooth_high   = twoSigmaSmoother_high.Approx(twoSigma_high,'linear',n)
            #oneSigmaSmooth_low    = oneSigmaSmoother_low.Approx(oneSigma_low,  'linear',n)
            #oneSigmaSmooth_high   = oneSigmaSmoother_high.Approx(oneSigma_high,'linear',n)
            #expectedSmooth        = expectedSmoother.Approx(expected,          'linear',n)
            twoSigmaSmooth_low    = twoSigmaSmoother_low.SmoothKern( twoSigmaForSmoothing_low, 'normal',200,n)
            twoSigmaSmooth_high   = twoSigmaSmoother_high.SmoothKern(twoSigmaForSmoothing_high,'normal',200,n)
            oneSigmaSmooth_low    = oneSigmaSmoother_low.SmoothKern( oneSigmaForSmoothing_low, 'normal',200,n)
            oneSigmaSmooth_high   = oneSigmaSmoother_high.SmoothKern(oneSigmaForSmoothing_high,'normal',200,n)
            expectedSmooth        = expectedSmoother.SmoothKern(     expectedForSmoothing,     'normal',200,n)
            #twoSigmaSmooth_low    = twoSigmaSmoother_low.SmoothLowess(twoSigma_low,  '',0.4)
            #twoSigmaSmooth_high   = twoSigmaSmoother_high.SmoothLowess(twoSigma_high,'',0.4)
            #oneSigmaSmooth_low    = oneSigmaSmoother_low.SmoothLowess(oneSigma_low,  '',0.4)
            #oneSigmaSmooth_high   = oneSigmaSmoother_high.SmoothLowess(oneSigma_high,'',0.4)
            #expectedSmooth        = expectedSmoother.SmoothLowess(expected,          '',0.4)
            #twoSigmaSmooth_low    = twoSigmaSmoother_low.SmoothSuper(twoSigma_low,  '',0,0)
            #twoSigmaSmooth_high   = twoSigmaSmoother_high.SmoothSuper(twoSigma_high,'',0,0)
            #oneSigmaSmooth_low    = oneSigmaSmoother_low.SmoothSuper(oneSigma_low,  '',0,0)
            #oneSigmaSmooth_high   = oneSigmaSmoother_high.SmoothSuper(oneSigma_high,'',0,0)
            #expectedSmooth        = expectedSmoother.SmoothSuper(expected,          '',0,0)
            for i in range(n-2):
                twoSigma_high.SetPoint(i+1,   twoSigmaSmooth_high.GetX()[i+1],    math.exp(twoSigmaSmooth_high.GetY()[i+1]))
                twoSigma_low.SetPoint( i+1,   twoSigmaSmooth_low.GetX()[i+1],     math.exp(twoSigmaSmooth_low.GetY()[i+1]))
                oneSigma_high.SetPoint(i+1,   oneSigmaSmooth_high.GetX()[i+1],    math.exp(oneSigmaSmooth_high.GetY()[i+1]))
                oneSigma_low.SetPoint( i+1,   oneSigmaSmooth_low.GetX()[i+1],     math.exp(oneSigmaSmooth_low.GetY()[i+1]))
                expected.SetPoint(     i+1,   expectedSmooth.GetX()[i+1],         math.exp(expectedSmooth.GetY()[i+1]))
            for i in range(n-2):
                twoSigma.SetPoint(     i+1,   twoSigma_high.GetX()[i+1],    twoSigma_high.GetY()[i+1])
                twoSigma.SetPoint(     n+i+1, twoSigma_low.GetX()[n-1-i-1], twoSigma_low.GetY()[n-1-i-1])
                oneSigma.SetPoint(     i+1,   oneSigma_high.GetX()[i+1],    oneSigma_high.GetY()[i+1])
                oneSigma.SetPoint(     n+i+1, oneSigma_low.GetX()[n-1-i-1], oneSigma_low.GetY()[n-1-i-1])

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


        if asymptoticFilenames:
            twoSigma_asym.SetLineColor(ROOT.kViolet-1)
            twoSigma_asym.SetMarkerStyle(0)
            oneSigma_asym.SetLineColor(ROOT.kViolet)
            oneSigma_asym.SetMarkerStyle(0)
            expected_asym.SetLineStyle(7)
            expected_asym.SetLineColor(ROOT.kMagenta)
            expected_asym.SetMarkerStyle(0)
            expected_asym.SetFillStyle(0)
            observed_asym.SetLineColor(ROOT.kMagenta)
            observed_asym.SetMarkerStyle(0)
            observed_asym.SetFillStyle(0)

        expected.GetXaxis().SetLimits(xvals[0],xvals[-1])
        expected.GetXaxis().SetTitle(xaxis)
        expected.GetYaxis().SetTitle(yaxis)

        expected.Draw()
        twoSigma.Draw('f')
        oneSigma.Draw('f')

        if asymptoticFilenames:
            twoSigma_asym.Draw('same')
            oneSigma_asym.Draw('same')
            expected_asym.Draw('same')
            ROOT.gPad.RedrawAxis()
            if not blind: observed_asym.Draw('same')

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
        if asymptoticFilenames:
            entries_asym = [
                [expected_asym,'Expected (asym.)','l'],
                [twoSigma_asym,'Expected (asym.) 2#sigma','l'],
                [oneSigma_asym,'Expected (asym.) 1#sigma','l'],
            ]
            if not blind: entries_asym = [[observed_asym,'Observed (asym.)','l']] + entries_asym
        if asymptoticFilenames:
            order = [x for pair in zip(entries,entries_asym) for x in pair]
            legend = self._getLegend(entries=order,numcol=numcol+1,position=legendpos)
        else:
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

    def plotCrossSectionLimit(self,xvals,apfns,ppfns,savename,**kwargs):
        '''Plot limits'''
        xaxis = kwargs.pop('xaxis','')
        yaxis = kwargs.pop('yaxis','')
        blind = kwargs.pop('blind',True)
        lumipos = kwargs.pop('lumipos',0)
        isprelim = kwargs.pop('isprelim',True)
        legendpos = kwargs.pop('legendpos',34)
        numcol = kwargs.pop('numcol',2)
        smooth = kwargs.pop('smooth',False)

        logging.info('Plotting {0}'.format(savename))

        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        canvas.SetLogy(1)
        #canvas.Divide(1,2,0.,0.)
        #canvas.Divide(1,2)

        limits = {}
        limits['AP'] = self._readLimits(xvals,apfns)
        limits['PP'] = self._readLimits(xvals,ppfns)
        if not limits['AP'] or not limits['PP']: return




        # get cross sections
        n = len(xvals)
        xsecMap = {'AP':{},'PP':{}}
        xsecGraph = {'AP':ROOT.TGraph(n),'PP':ROOT.TGraph(n)}
        for i,mass in enumerate(xvals):
            sample_4l = 'HPlusPlusHMinusMinusHTo4L_M-{0}_TuneCUETP8M1_13TeV_pythia8'
            sample_3l = 'HPlusPlusHMinusHTo3L_M-{0}_TuneCUETP8M1_13TeV_calchep-pythia8'
            xsecMap['PP'][mass] = xsecs[sample_4l.format(mass)]
            xsecMap['AP'][mass] = xsecs[sample_3l.format(mass)]
            xsecGraph['AP'].SetPoint(i,mass,xsecMap['AP'][mass])
            xsecGraph['PP'].SetPoint(i,mass,xsecMap['PP'][mass])
        for prod in ['AP','PP']:
            xsecGraph[prod].SetMarkerStyle(0)
            xsecGraph[prod].SetFillStyle(0)
            xsecGraph[prod].SetLineColor(ROOT.kBlue if prod=='AP' else ROOT.kRed)
            xsecGraph[prod].GetXaxis().SetLimits(xvals[0],xvals[-1])
        xsecGraph['AP'].GetYaxis().SetTitleOffset(0.75)
        xsecGraph['AP'].GetYaxis().SetTitleSize(0.105)
        xsecGraph['PP'].GetYaxis().SetTitleOffset(0.85)
        xsecGraph['PP'].GetYaxis().SetTitleSize(0.095)
        xsecGraph['AP'].GetXaxis().SetTitle('')
        xsecGraph['PP'].GetXaxis().SetTitle('#Phi^{++} Mass (GeV)')
        xsecGraph['PP'].GetXaxis().SetTitleSize(0.110)
        xsecGraph['PP'].GetXaxis().SetLabelSize(0.073)
        xsecGraph['PP'].GetXaxis().SetLabelOffset(0.012)
        xsecGraph['AP'].GetYaxis().SetTitle('#sigma #upoint BR (pb)')
        xsecGraph['PP'].GetYaxis().SetTitle('#sigma #upoint BR^{2} (pb)')
        xsecGraph['AP'].GetYaxis().SetLabelSize(0.095)
        xsecGraph['PP'].GetYaxis().SetLabelSize(0.08)

        # AP/PP limits
        twoSigma = {}
        oneSigma = {}
        expected = {}
        observed = {}
        twoSigma_low = {}
        twoSigma_high = {}
        oneSigma_low = {}
        oneSigma_high = {}
        twoSigmaForSmoothing_low = {}
        twoSigmaForSmoothing_high = {}
        oneSigmaForSmoothing_low = {}
        oneSigmaForSmoothing_high = {}
        expectedForSmoothing = {}
        twoSigmaSmoother_low = {}
        twoSigmaSmoother_high = {}
        oneSigmaSmoother_low = {}
        oneSigmaSmoother_high = {}
        expectedSmoother = {}
        twoSigmaSmooth_low = {}
        twoSigmaSmooth_high = {}
        oneSigmaSmooth_low = {}
        oneSigmaSmooth_high = {}
        expectedSmooth = {}
        pad = {}
        pad['AP'] = ROOT.TPad('AP', 'AP', 0.0, 0.54, 1.0, 1.0)
        pad['AP'].Draw()
        pad['PP'] = ROOT.TPad('AP', 'AP', 0.0, 0.0, 1.0, 0.54)
        pad['PP'].Draw()
        canvas.cd()
        for p,prod in enumerate(['AP','PP']):
            #pad[prod] = canvas.cd(p+1)
            pad[prod].cd()
            pad[prod].SetLeftMargin(0.16)
            pad[prod].SetRightMargin(0.02)
            if prod=='AP': 
                pad[prod].SetTopMargin(0.11)
                pad[prod].SetBottomMargin(0.)
            if prod=='PP': 
                pad[prod].SetTopMargin(0.)
                pad[prod].SetBottomMargin(0.24)
            pad[prod].SetTickx(1)
            pad[prod].SetTicky(1)
            pad[prod].SetLogy(1)
            pad[prod].Draw()

            twoSigma[prod] = ROOT.TGraph(2*n)
            oneSigma[prod] = ROOT.TGraph(2*n)
            expected[prod] = ROOT.TGraph(n)
            observed[prod] = ROOT.TGraph(n)
            twoSigma_low[prod] = ROOT.TGraph(n)
            twoSigma_high[prod] = ROOT.TGraph(n)
            oneSigma_low[prod] = ROOT.TGraph(n)
            oneSigma_high[prod] = ROOT.TGraph(n)
            twoSigmaForSmoothing_low[prod] = ROOT.TGraph(n)
            twoSigmaForSmoothing_high[prod] = ROOT.TGraph(n)
            oneSigmaForSmoothing_low[prod] = ROOT.TGraph(n)
            oneSigmaForSmoothing_high[prod] = ROOT.TGraph(n)
            expectedForSmoothing[prod] = ROOT.TGraph(n)

            for i in range(len(xvals)):
                twoSigma[prod].SetPoint(                 i,   xvals[i],     limits[prod][xvals[i]][0]             *xsecMap[prod][xvals[i]]) # 0.025
                oneSigma[prod].SetPoint(                 i,   xvals[i],     limits[prod][xvals[i]][1]             *xsecMap[prod][xvals[i]]) # 0.16
                expected[prod].SetPoint(                 i,   xvals[i],     limits[prod][xvals[i]][2]             *xsecMap[prod][xvals[i]]) # 0.5
                oneSigma[prod].SetPoint(                 n+i, xvals[n-i-1], limits[prod][xvals[n-i-1]][3]         *xsecMap[prod][xvals[n-i-1]]) # 0.84
                twoSigma[prod].SetPoint(                 n+i, xvals[n-i-1], limits[prod][xvals[n-i-1]][4]         *xsecMap[prod][xvals[n-i-1]]) # 0.975
                observed[prod].SetPoint(                 i,   xvals[i],     limits[prod][xvals[i]][5]             *xsecMap[prod][xvals[i]]) # obs
                twoSigma_high[prod].SetPoint(            i,   xvals[i],     limits[prod][xvals[i]][0]             *xsecMap[prod][xvals[i]]) # 0.025
                oneSigma_high[prod].SetPoint(            i,   xvals[i],     limits[prod][xvals[i]][1]             *xsecMap[prod][xvals[i]]) # 0.16
                oneSigma_low[prod].SetPoint(             i,   xvals[n-i-1], limits[prod][xvals[n-i-1]][3]         *xsecMap[prod][xvals[n-i-1]]) # 0.84
                twoSigma_low[prod].SetPoint(             i,   xvals[n-i-1], limits[prod][xvals[n-i-1]][4]         *xsecMap[prod][xvals[n-i-1]]) # 0.975
                twoSigmaForSmoothing_high[prod].SetPoint(i,   xvals[i],     math.log(limits[prod][xvals[i]][0]    *xsecMap[prod][xvals[i]])) # 0.025
                oneSigmaForSmoothing_high[prod].SetPoint(i,   xvals[i],     math.log(limits[prod][xvals[i]][1]    *xsecMap[prod][xvals[i]])) # 0.16
                oneSigmaForSmoothing_low[prod].SetPoint( i,   xvals[n-i-1], math.log(limits[prod][xvals[n-i-1]][3]*xsecMap[prod][xvals[n-i-1]])) # 0.84
                twoSigmaForSmoothing_low[prod].SetPoint( i,   xvals[n-i-1], math.log(limits[prod][xvals[n-i-1]][4]*xsecMap[prod][xvals[n-i-1]])) # 0.975
                expectedForSmoothing[prod].SetPoint(     i,   xvals[i],     math.log(limits[prod][xvals[i]][2]    *xsecMap[prod][xvals[i]])) # 0.5

            if smooth: # smooth out the expected bands
                twoSigmaSmoother_low[prod]  = ROOT.TGraphSmooth()
                twoSigmaSmoother_high[prod] = ROOT.TGraphSmooth()
                oneSigmaSmoother_low[prod]  = ROOT.TGraphSmooth()
                oneSigmaSmoother_high[prod] = ROOT.TGraphSmooth()
                expectedSmoother[prod]      = ROOT.TGraphSmooth()
                #twoSigmaSmooth_low[prod]    = twoSigmaSmoother_low[prod].Approx(twoSigma_low[prod],  'linear',n)
                #twoSigmaSmooth_high[prod]   = twoSigmaSmoother_high[prod].Approx(twoSigma_high[prod],'linear',n)
                #oneSigmaSmooth_low[prod]    = oneSigmaSmoother_low[prod].Approx(oneSigma_low[prod],  'linear',n)
                #oneSigmaSmooth_high[prod]   = oneSigmaSmoother_high[prod].Approx(oneSigma_high[prod],'linear',n)
                #expectedSmooth[prod]        = expectedSmoother[prod].Approx(expected[prod],          'linear',n)
                twoSigmaSmooth_low[prod]    = twoSigmaSmoother_low[prod].SmoothKern( twoSigmaForSmoothing_low[prod], 'normal',200,n)
                twoSigmaSmooth_high[prod]   = twoSigmaSmoother_high[prod].SmoothKern(twoSigmaForSmoothing_high[prod],'normal',200,n)
                oneSigmaSmooth_low[prod]    = oneSigmaSmoother_low[prod].SmoothKern( oneSigmaForSmoothing_low[prod], 'normal',200,n)
                oneSigmaSmooth_high[prod]   = oneSigmaSmoother_high[prod].SmoothKern(oneSigmaForSmoothing_high[prod],'normal',200,n)
                expectedSmooth[prod]        = expectedSmoother[prod].SmoothKern(     expectedForSmoothing[prod],     'normal',200,n)
                #twoSigmaSmooth_low[prod]    = twoSigmaSmoother_low[prod].SmoothLowess(twoSigma_low[prod],  '',0.4)
                #twoSigmaSmooth_high[prod]   = twoSigmaSmoother_high[prod].SmoothLowess(twoSigma_high[prod],'',0.4)
                #oneSigmaSmooth_low[prod]    = oneSigmaSmoother_low[prod].SmoothLowess(oneSigma_low[prod],  '',0.4)
                #oneSigmaSmooth_high[prod]   = oneSigmaSmoother_high[prod].SmoothLowess(oneSigma_high[prod],'',0.4)
                #expectedSmooth[prod]        = expectedSmoother[prod].SmoothLowess(expected[prod],          '',0.4)
                #twoSigmaSmooth_low[prod]    = twoSigmaSmoother_low[prod].SmoothSuper(twoSigma_low[prod],  '',0,0)
                #twoSigmaSmooth_high[prod]   = twoSigmaSmoother_high[prod].SmoothSuper(twoSigma_high[prod],'',0,0)
                #oneSigmaSmooth_low[prod]    = oneSigmaSmoother_low[prod].SmoothSuper(oneSigma_low[prod],  '',0,0)
                #oneSigmaSmooth_high[prod]   = oneSigmaSmoother_high[prod].SmoothSuper(oneSigma_high[prod],'',0,0)
                #expectedSmooth[prod]        = expectedSmoother[prod].SmoothSuper(expected[prod],          '',0,0)
                for i in range(n-2):
                    twoSigma_high[prod].SetPoint(i+1,   twoSigmaSmooth_high[prod].GetX()[i+1],    math.exp(twoSigmaSmooth_high[prod].GetY()[i+1]))
                    twoSigma_low[prod].SetPoint( i+1,   twoSigmaSmooth_low[prod].GetX()[i+1],     math.exp(twoSigmaSmooth_low[prod].GetY()[i+1]))
                    oneSigma_high[prod].SetPoint(i+1,   oneSigmaSmooth_high[prod].GetX()[i+1],    math.exp(oneSigmaSmooth_high[prod].GetY()[i+1]))
                    oneSigma_low[prod].SetPoint( i+1,   oneSigmaSmooth_low[prod].GetX()[i+1],     math.exp(oneSigmaSmooth_low[prod].GetY()[i+1]))
                    expected[prod].SetPoint(     i+1,   expectedSmooth[prod].GetX()[i+1],         math.exp(expectedSmooth[prod].GetY()[i+1]))
                for i in range(n-2):
                    twoSigma[prod].SetPoint(     i+1,   twoSigma_high[prod].GetX()[i+1],    twoSigma_high[prod].GetY()[i+1])
                    twoSigma[prod].SetPoint(     n+i+1, twoSigma_low[prod].GetX()[n-1-i-1], twoSigma_low[prod].GetY()[n-1-i-1])
                    oneSigma[prod].SetPoint(     i+1,   oneSigma_high[prod].GetX()[i+1],    oneSigma_high[prod].GetY()[i+1])
                    oneSigma[prod].SetPoint(     n+i+1, oneSigma_low[prod].GetX()[n-1-i-1], oneSigma_low[prod].GetY()[n-1-i-1])

            twoSigma[prod].SetFillColor(ROOT.kYellow)
            twoSigma[prod].SetLineColor(ROOT.kYellow)
            twoSigma[prod].SetMarkerStyle(0)
            oneSigma[prod].SetFillColor(ROOT.kSpring)
            oneSigma[prod].SetLineColor(ROOT.kSpring)
            oneSigma[prod].SetMarkerStyle(0)
            expected[prod].SetLineStyle(7)
            expected[prod].SetMarkerStyle(0)
            expected[prod].SetFillStyle(0)
            observed[prod].SetMarkerStyle(0)
            observed[prod].SetFillStyle(0)

            expected[prod].GetXaxis().SetLimits(xvals[0],xvals[-1])
            expected[prod].GetXaxis().SetTitle(xaxis)
            expected[prod].GetYaxis().SetTitle(yaxis)

            xsecGraph[prod].Draw()
            twoSigma[prod].Draw('f')
            oneSigma[prod].Draw('f')
            expected[prod].Draw('same')
            xsecGraph[prod].Draw('same')
            ROOT.gPad.RedrawAxis()
            if not blind: observed[prod].Draw('same')

            canvas.cd()

        #canvas.cd()
        # get the legend
        entries = [
            #[expected['AP'],'Expected','l'],
            #[twoSigma['AP'],'Expected 2#sigma','F'],
            #[oneSigma['AP'],'Expected 1#sigma','F'],
            [xsecGraph['AP'],'#splitline{Assoc. Prod.}{Cross Section}','l'],
            [xsecGraph['PP'],'#splitline{Pair Prod.}{Cross Section}','l'],
        ]
        #if not blind: entries = [[observed['AP'],'Observed','l']] + entries
        legend = self._getLegend(entries=entries,numcol=numcol,position=legendpos)
        legend.Draw()

        # cms lumi styling
        self._setStyle(canvas,position=lumipos,preliminary=isprelim)

        self._save(canvas,savename)



    def moneyPlot(self,limvals,savename,**kwargs):
        xaxis = kwargs.pop('xaxis','#Phi^{#pm#pm} Mass (GeV)')
        yaxis = kwargs.pop('yaxis','')
        blind = kwargs.pop('blind',True)
        lumipos = kwargs.pop('lumipos',0)
        isprelim = kwargs.pop('isprelim',True)
        legendpos = kwargs.pop('legendpos',31)
        numcol = kwargs.pop('numcol',1)
        doPreviousExclusion = kwargs.pop('doPreviousExclusion',False)
        offAxis = kwargs.pop('offAxis',False)

        logging.info('Plotting {0}'.format(savename))

        canvas = ROOT.TCanvas(savename,savename,50,50,1000 if offAxis else 800,900)
        canvas.SetFillColor(0)
        canvas.SetBorderMode(0)
        canvas.SetFrameFillStyle(0)
        canvas.SetFrameBorderMode(0)
        canvas.SetLeftMargin(0.22)
        canvas.SetRightMargin(0.24 if offAxis else 0.04)
        canvas.SetTopMargin(0.05)
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
            # mode : { 1: 13TeV Exp, 2: 13TeV Exc, 3: 8TeV Exp, 4: 8TeV Exc},
            'HppComb': {1: ROOT.TColor.GetColor('#248F24'), 2: ROOT.TColor.GetColor('#2EB82E'), 3: ROOT.TColor.GetColor('#999900'), 4: ROOT.TColor.GetColor('#CCCC00'), },
            'HppAP'  : {1: ROOT.TColor.GetColor('#0073E6'), 2: ROOT.TColor.GetColor('#1A8CFF'), 3: ROOT.TColor.GetColor('#009999'), 4: ROOT.TColor.GetColor('#00CCCC'), },
            'HppPP'  : {1: ROOT.TColor.GetColor('#B32400'), 2: ROOT.TColor.GetColor('#E62E00'), 3: ROOT.TColor.GetColor('#990099'), 4: ROOT.TColor.GetColor('#CC00CC'), },
        }

        prodLabels = {
            'HppAP'  : 'Associated Production',
            'HppPP'  : 'Pair Production',
            'HppComb': 'Combined',
        }

        nl = len(labels)
        h = ROOT.TH2F("h", "h; {0}; ".format(xaxis), 1,0,1000 if offAxis else 1900,2*nl+4,0.5,nl+2.5)
        h.GetYaxis().SetRangeUser(1.,nl+2.)
        h.GetYaxis().SetTickSize(0)
        h.GetXaxis().SetLabelSize(0.030)
        h.Draw()

        cur = len(labels)*4. + 10
        errors_one = {}
        errors_two = {}
        expected = {}
        observed = {}
        prevExpExclusion = {}
        prevExclusion = {}

        multiExpected = ROOT.TMultiGraph()
        multiObserved = ROOT.TMultiGraph()
        multiPrevExpected = ROOT.TMultiGraph()
        multiPrevObserved = ROOT.TMultiGraph()

        for i,mode in enumerate(labels):
            h.GetYaxis().SetBinLabel(2*nl+2-2*i,labels[mode])
            cur -= 4
            errors_one[mode] = {}
            errors_two[mode] = {}
            expected[mode] = {}
            observed[mode] = {}
            prevExpExclusion[mode] = {}
            prevExclusion[mode] = {}
            sub = 0
            for prod in ['HppAP','HppPP','HppComb']:
                sub += 1
                # get current expected and observed limits, draw as tgraphs
                l2, l1, exp, h1, h2, obs = limvals[mode][prod]

                expected[mode][prod] = ROOT.TGraph(2,array('d',[exp,exp]),array('d',[(cur-sub+0.5)/4,(cur-sub-0.5)/4]))
                expected[mode][prod].SetFillColor(colors[prod][1])
                expected[mode][prod].SetLineColor(colors[prod][1])
                expected[mode][prod].SetLineWidth(-504)
                expected[mode][prod].SetFillStyle(3004)
                expected[mode][prod].SetFillColor(colors[prod][1])
                multiExpected.Add(expected[mode][prod])

                observed[mode][prod] = ROOT.TGraph(2,array('d',[exp,exp] if blind else [obs,obs]),array('d',[(cur-sub+0.5)/4,(cur-sub-0.5)/4]))
                observed[mode][prod].SetFillColorAlpha(colors[prod][2],0.35)
                observed[mode][prod].SetLineColor(colors[prod][2])
                observed[mode][prod].SetLineWidth(-9001)
                multiObserved.Add(observed[mode][prod])

                # get previous exclusions, draw as filled tgraph bar chart
                prevExp = prevExpLimits[mode][prod]
                prevExpExclusion[mode][prod] = ROOT.TGraph(2,array('d',[prevExp,prevExp]),array('d',[(cur-sub+0.5)/4,(cur-sub-0.5)/4]))
                prevExpExclusion[mode][prod].SetFillColor(colors[prod][3])
                prevExpExclusion[mode][prod].SetLineColor(colors[prod][3])
                prevExpExclusion[mode][prod].SetLineWidth(-504)
                prevExpExclusion[mode][prod].SetFillStyle(3004)
                multiPrevExpected.Add(prevExpExclusion[mode][prod])

                prevExc = prevLimits[mode][prod]
                prevExclusion[mode][prod] = ROOT.TGraph(2,array('d',[prevExc,prevExc]),array('d',[(cur-sub+0.5)/4,(cur-sub-0.5)/4]))
                prevExclusion[mode][prod].SetFillColorAlpha(colors[prod][4],0.35)
                prevExclusion[mode][prod].SetLineColor(colors[prod][4])
                prevExclusion[mode][prod].SetLineWidth(-9001)
                multiPrevObserved.Add(prevExclusion[mode][prod])

        multiExpected.Draw('L')
        if not blind: multiObserved.Draw('L')
        if doPreviousExclusion: multiPrevExpected.Draw('L')
        if doPreviousExclusion: multiPrevObserved.Draw('L')

        ROOT.gPad.RedrawAxis()


        obsleg = ROOT.TGraph()
        obsleg.SetLineColor(ROOT.kBlack)
        obsleg.SetFillColorAlpha(ROOT.kBlack,0.35)

        expleg = ROOT.TGraph()
        expleg.SetLineWidth(0)
        expleg.SetFillStyle(3004)

        explineargs = [0.8,0.5,0.8,0.6]

        curr = {}
        for prod in ['HppAP','HppPP','HppComb']:
            curr[prod+'8'] = ROOT.TGraph()
            curr[prod+'8'].SetLineColor(colors[prod][4])
            curr[prod+'8'].SetFillColorAlpha(colors[prod][4],0.35)
            curr[prod+'13'] = ROOT.TGraph()
            curr[prod+'13'].SetLineColor(colors[prod][2])
            curr[prod+'13'].SetFillColorAlpha(colors[prod][2],0.35)

        if doPreviousExclusion:
            legend = ROOT.TLegend(0.765 if offAxis else 0.55,0.64 if offAxis else 0.44,0.99 if offAxis else 0.95,0.72 if offAxis else 0.52,'','NDC')
            legend.SetTextFont(42)
            legend.SetTextSize(0.02)
            legend.SetBorderSize(0)
            legend.SetFillColor(0)

            if offAxis:
                legend.AddEntry(obsleg,'Obs. exclusion 95% CL','f')
                legend.AddEntry(expleg,'Exp. exclusion 95% CL','f')
                explineargs = [0.813,0.646,0.813,0.675]
            else:
                legend.AddEntry(obsleg,'Observed exclusion 95% CL','f')
                legend.AddEntry(expleg,'Expected exclusion 95% CL','f')
                explineargs = [0.635,0.446,0.635,0.475]
            legend.Draw()

            sublegends = {}
            for i,prod in enumerate(['HppAP','HppPP','HppComb']):
                if offAxis:
                    sublegends[prod] = ROOT.TLegend(0.765,0.64-0.04*3*(i+1),0.99,0.64-0.04*3*i,'','NDC')
                else:
                    sublegends[prod] = ROOT.TLegend(0.558,0.44-0.04*2*(i+1),0.95,0.44-0.04*2*i,'','NDC')
                sublegends[prod].SetTextFont(42)
                sublegends[prod].SetTextSize(0.02)
                sublegends[prod].SetBorderSize(0)
                sublegends[prod].SetFillColor(0)
                sublegends[prod].SetHeader(prodLabels[prod])
                sublegends[prod].SetNColumns(1 if offAxis else 2)
                sublegends[prod].AddEntry(curr[prod+'8'],'19.7 fb^{-1} (8 TeV)','f')
                sublegends[prod].AddEntry(curr[prod+'13'],'12.9 fb^{-1} (13 TeV)','f')
                sublegends[prod].Draw()
        else:
            legend = ROOT.TLegend(0.765 if offAxis else 0.60,0.4 if offAxis else 0.2,0.99 if offAxis else 0.95,0.6 if offAxis else 0.4,'','NDC')
            legend.SetTextFont(42)
            legend.SetBorderSize(0)
            legend.SetFillColor(0)

            legend.AddEntry(obsleg,'Observed exclusion 95% CL','f')
            legend.AddEntry(expleg,'Expected exclusion 95% CL','lf')
            for prod in ['HppAP','HppPP','HppComb']:
                legend.AddEntry(curr[prod+'13'],prodLabels[prod],'f')

            if offAxis:
                explineargs = [0.813,0.527,0.813,0.556]
            else:
                explineargs = [0.674,0.326,0.674,0.355]

            legend.Draw()

        expline = ROOT.TLine(*explineargs)
        expline.SetNDC()
        expline.SetLineWidth(4)
        expline.Draw()

        # cms lumi styling
        if doPreviousExclusion:
            self._setStyle(canvas,position=lumipos,preliminary=isprelim,period_int=0)
        else:
            self._setStyle(canvas,position=lumipos,preliminary=isprelim)

        self._save(canvas,savename)

