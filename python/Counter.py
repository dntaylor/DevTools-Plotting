import os
import sys
import logging
import math
from array import array
from collections import OrderedDict

import ROOT

from DevTools.Plotter.NtupleWrapper import NtupleWrapper
from DevTools.Plotter.utilities import getLumi, isData
from DevTools.Utilities.utilities import sumWithError, prodWithError, divWithError, python_mkdir

ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")


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
        self.signals = []
        self.j = 0

    def __exit__(self, type, value, traceback):
        self.finish()

    def __del__(self):
        self.finish()

    def finish(self):
        '''Cleanup stuff'''
        logging.info('Finished')

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
        for sampleName in processSamples:
            self._openFile(sampleName,analysis=analysis,**kwargs)
        self.analysisDict[processName] = analysis
        self.processDict[processName] = processSamples
        self.processOrder += [processName]
        if signal: self.signals += [processName]

    def clear(self):
        self.sampleFiles = {}
        self.analysisDict = {}
        self.processDict = {}
        self.processOrder = []
        self.signals = []

    def _readSampleCount(self,sampleName,directory,**kwargs):
        '''Read the count from file'''
        analysis = kwargs.pop('analysis',self.analysis)
        hist = self.sampleFiles[analysis][sampleName].getCount(directory)
        val = hist.GetBinContent(1) if hist else 0.
        err = hist.GetBinError(1) if hist else 0.
        return val,err

    def _getTempCount(self,sampleName,selection,scalefactor,**kwargs):
        '''Get a temporary count'''
        analysis = kwargs.pop('analysis',self.analysis)
        hist = self.sampleFiles[analysis][sampleName].getTempCount(selection,scalefactor)
        val = hist.GetBinContent(1) if hist else 0.
        err = hist.GetBinError(1) if hist else 0.
        return val,err

    def _getCount(self,processName,directory,**kwargs):
        '''Get count for process'''
        analysis = self.analysisDict[processName]
        scalefactor = kwargs.pop('scalefactor','1')
        mcscalefactor = kwargs.pop('mcscalefactor','1')
        datascalefactor = kwargs.pop('datascalefactor','1')
        selection = kwargs.pop('selection','')
        mccut = kwargs.pop('mccut','')
        # check if it is a map, list, or directory
        if isinstance(directory,dict):       # its a map
            directory = directory[processName]
        if isinstance(directory,basestring): # its a single directory
            directory = [directory]
        if processName in self.processDict:
            counts = []
            for dirName in directory:
                for sampleName in self.processDict[processName]:
                    if selection:
                        sf = '*'.join([scalefactor,datascalefactor if isData(sampleName) else mcscalefactor])
                        fullcut = ' && '.join([selection,mccut]) if mccut and not isData(sampleName) else selection
                        count = self._getTempCount(sampleName,fullcut,sf,analysis=analysis)
                    else:
                        count = self._readSampleCount(sampleName,dirName,analysis=analysis)
                    if count: counts += [count]
            if not counts:
                return (0.,0.)
            if len(counts)==1:
                return counts[0]
            else:
                return sumWithError(*counts)
        else:
            return (0.,0.)

    def printHeader(self):
        '''Print a header'''
        print '{0:20} | {1} |'.format('',' | '.join(['{0:10}'.format(name) for name in self.processOrder]))

    def printDivider(self):
        '''Print a divider'''
        print '{0:20}-|-{1}-|'.format('-'*20,'-|-'.join(['{0:10}'.format('-'*10) for name in self.processOrder]))

    def printCounts(self,label,directory,**kwargs):
        '''Print the counts'''
        counts = []
        for processName in self.processOrder:
            counts += [self._getCount(processName,directory,**kwargs)]
        vals = [x[0] for x in counts]
        errs = [x[1] for x in counts]
        print '{0:20} | {1} |'.format(label,' | '.join(['{0:10.4g}'.format(v) for v in vals]))
