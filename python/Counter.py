import os
import sys
import logging
import math
import prettytable
from array import array
from collections import OrderedDict

import ROOT

from DevTools.Plotter.NtupleWrapper import NtupleWrapper
from DevTools.Plotter.utilities import getLumi, isData
from DevTools.Utilities.utilities import sumWithError, prodWithError, divWithError, python_mkdir

ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 2001;")


class Counter(object):
    '''Basic counter utilities'''

    def __init__(self,analysis,**kwargs):
        '''Initialize the counter'''
        self.analysis = analysis

        # empty initialization
        self.processDict = {}
        self.analysisDict = {}
        self.processOrder = []
        self.sampleFiles = {}
        self.processSampleCuts = {}
        self.signals = []
        self.scales = {}
        self.j = 0
        self.poisson = kwargs.pop('poisson',False) # return poisson errors

    def _openFile(self,sampleName,**kwargs):
        '''Verify and open a sample'''
        analysis = kwargs.pop('analysis',self.analysis)
        if analysis not in self.sampleFiles: self.sampleFiles[analysis] = {}
        if sampleName not in self.sampleFiles[analysis]:
            self.sampleFiles[analysis][sampleName] = NtupleWrapper(analysis,sampleName,**kwargs)
            ROOT.gROOT.cd()

    def addProcess(self,processName,processSamples,signal=False,**kwargs):
        '''
        Add process, processSamples is a list of samples to include
        '''
        analysis = kwargs.pop('analysis',self.analysis)
        sampleCuts = kwargs.pop('sampleCuts',{})
        scale = kwargs.pop('scale',{})
        for sampleName in processSamples:
            self._openFile(sampleName,analysis=analysis,**kwargs)
        self.analysisDict[processName] = analysis
        self.processDict[processName] = processSamples
        if sampleCuts: self.processSampleCuts[processName] = sampleCuts
        self.processOrder += [processName]
        if signal: self.signals += [processName]
        if scale: self.scales[processName] = scale

    def clear(self):
        self.sampleFiles = {}
        self.analysisDict = {}
        self.processDict = {}
        self.processOrder = []
        self.signals = []
        self.scales = {}
        self.processSampleCuts = {}

    def _readSampleCount(self,sampleName,directory,**kwargs):
        '''Read the count from file'''
        analysis = kwargs.pop('analysis',self.analysis)
        poisson = kwargs.pop('poisson', self.poisson)
        hist = self.sampleFiles[analysis][sampleName].getCount(directory,full=poisson)
        if isinstance(hist,list) or isinstance(hist,tuple):
            return hist
        if isinstance(hist,ROOT.TH1):
            val = hist.GetBinContent(1) if hist else 0.
            err = hist.GetBinError(1) if hist else 0.
            count = hist.GetEntires() if hist else 0
            if poisson:
                return val,err,count 
            else:
                return val,err
        if poisson:
            return 0.,0., 0 
        else:
            return 0.,0.

    def _getTempCount(self,sampleName,selection,scalefactor,**kwargs):
        '''Get a temporary count'''
        analysis = kwargs.pop('analysis',self.analysis)
        poisson = kwargs.pop('poisson', self.poisson)
        hist = self.sampleFiles[analysis][sampleName].getTempCount(selection,scalefactor)
        val = hist.GetBinContent(1) if hist else 0.
        err = hist.GetBinError(1) if hist else 0.
        count = hist.GetEntries() if hist else 0
        return (val,err,count) if poisson else (val,err)

    def _getPoisson(self,entries):
        if entries<0: entries = 0
        chisqr = ROOT.TMath.ChisquareQuantile
        ey_low = entries - 0.5 * chisqr(0.1586555, 2. * entries)
        ey_high = 0.5 * chisqr(
            1. - 0.1586555, 2. * (entries + 1)) - entries
        return ey_high

    def _getCount(self,processName,directory,**kwargs):
        '''Get count for process'''
        analysis = self.analysisDict[processName]
        scalefactor = kwargs.pop('scalefactor','1')
        mcscalefactor = kwargs.pop('mcscalefactor','1')
        datascalefactor = kwargs.pop('datascalefactor','1')
        selection = kwargs.pop('selection','')
        mccut = kwargs.pop('mccut','')
        poisson = kwargs.pop('poisson',self.poisson)
        # check if it is a map, list, or directory
        if isinstance(directory,dict):       # its a map
            directory = directory[processName]
        if isinstance(directory,basestring): # its a single directory
            directory = [directory]
        if processName in self.processDict:
            logging.debug('Process: {0}'.format(processName))
            counts = []
            for dirName in directory:
                logging.debug('Directory: {0}'.format(dirName))
                for sampleName in self.processDict[processName]:
                    logging.debug('Sample: {0}'.format(sampleName))
                    if selection:
                        logging.debug('Custom selection')
                        sf = '*'.join([scalefactor,datascalefactor if isData(sampleName) else mcscalefactor])
                        fullcut = ' && '.join([selection,mccut]) if mccut and not isData(sampleName) else selection
                        if processName in self.processSampleCuts:
                            if sampleName in self.processSampleCuts[processName]:
                                fullcut += ' && {0}'.format(self.processSampleCuts[processName][sampleName])
                        # scale a sample via a cut
                        if processName in self.scales and sampleName in self.scales[processName]:
                            for cut in self.scales[processName][sampleName]:
                                thissf = '{0}*{1}'.format(sf,self.scales[processName][sampleName][cut])
                                thisFullCut = '{0} && {1}'.format(fullcut, cut)
                                count = self._getTempCount(sampleName,thisFullCut,thissf,analysis=analysis,poisson=poisson)
                                logging.debug('Count: {0} +/- {1}'.format(*count))
                                if count: counts += [count]
                        else:
                            count = self._getTempCount(sampleName,fullcut,sf,analysis=analysis,poisson=poisson)
                            logging.debug('Count: {0} +/- {1}'.format(*count))
                            if count: counts += [count]
                    else:
                        count = self._readSampleCount(sampleName,dirName,analysis=analysis,poisson=poisson)
                        logging.debug('Count: {0} +/- {1}'.format(*count))
                        if count: counts += [count]
            if not counts:
                logging.debug('No entries for {0}'.format(processName))
                return (0., self._getPoisson(0.)) if poisson else (0.,0.)
            if len(counts)==1:
                if poisson: 
                    perr = self._getPoisson(counts[0][2])
                    w = float(counts[0][0])/counts[0][2]
                    val = counts[0][0]
                    err = perr * w
                else:
                    if len(counts[0])!=2: print counts
                    val, err = counts[0]
                logging.debug('Total: {0} +/- {1}'.format(val,err))
                return val,err
            else:
                if poisson:
                    newcounts = []
                    for count in counts:
                        perr = self._getPoisson(count[2])
                        w = float(count[0])/count[2]
                        val = count[0]
                        err = perr * w
                        newcounts += [[val,err]]
                    counts = newcounts
                total = sumWithError(*counts)
                logging.debug('Total: {0} +/- {1}'.format(*total))
                return total
        else:
            return (0.,0.)

    def printHeader(self,label=''):
        '''Print a header'''
        print '{0:20} | {1} |'.format(label,' | '.join(['{0:10}'.format(name) for name in self.processOrder + ['All BG']]))

    def printDivider(self):
        '''Print a divider'''
        print '{0:20}-|-{1}-|'.format('-'*20,'-|-'.join(['{0:10}'.format('-'*10) for name in self.processOrder + ['All BG']]))

    def getCount(self,processName,directory,**kwargs):
        '''Get a single count'''
        return self._getCount(processName,directory,**kwargs)

    def getCounts(self,directory,**kwargs):
        '''Get a map for the counts'''
        counts = {}
        for processName in self.processOrder:
            counts[processName] = self.getCount(processName,directory,**kwargs)
        return counts

    def printCounts(self,label,directory,**kwargs):
        '''Print the counts'''
        doError = kwargs.pop('doError',False)
        logging.info('Processing: {0}'.format(label))
        countMap = self.getCounts(directory,**kwargs)
        counts = []
        for processName in self.processOrder:
            counts += [countMap[processName]]
        vals = [x[0] for x in counts]
        errs = [x[1] for x in counts]
        nsig = len(self.signals)
        vals += [sum(vals[:-1*(nsig+1)])]
        errs += [sum([x**2 for x in errs[:-1*(nsig+1)]])**0.5]
        print '{0:20} | {1} |'.format(label,' | '.join(['{0:>10.4f}'.format(v) for v in vals]))
        if doError: print '{0:20} | {1} |'.format('',' | '.join(['{0:>10.4f}'.format(e) for e in errs]))
