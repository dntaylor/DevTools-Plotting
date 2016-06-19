import logging
from prettytable import PrettyTable

import ROOT

from DevTools.Plotter.NtupleWrapper import NtupleWrapper
from DevTools.Utilities.utilities import sumWithError, prodWithError, divWithError, python_mkdir


class Efficiency(object):
    '''A class to compute efficiency of selections'''

    def __init__(self,analysis):
        self.analysis = analysis
        # empty initialization
        self.processDict = {}
        self.analysisDict = {}
        self.processOrder = []
        self.sampleFiles = {}
        self.processSampleCuts = {}

    def _openFile(self,sampleName,**kwargs):
        '''Verify and open a sample'''
        analysis = kwargs.pop('analysis',self.analysis)
        if analysis not in self.sampleFiles: self.sampleFiles[analysis] = {}
        if sampleName not in self.sampleFiles[analysis]:
            self.sampleFiles[analysis][sampleName] = NtupleWrapper(analysis,sampleName,**kwargs)
            ROOT.gROOT.cd()

    def addProcess(self,processName,processSamples,**kwargs):
        '''
        Add process, processSamples is a list of samples to include
        '''
        analysis = kwargs.pop('analysis',self.analysis)
        sampleCuts = kwargs.pop('sampleCuts',{})
        for sampleName in processSamples:
            self._openFile(sampleName,analysis=analysis,**kwargs)
        self.analysisDict[processName] = analysis
        self.processDict[processName] = processSamples
        if sampleCuts: self.processSampleCuts[processName] = sampleCuts
        self.processOrder += [processName]

    def clear(self):
        self.sampleFiles = {}
        self.analysisDict = {}
        self.processDict = {}
        self.processOrder = []
        self.processSampleCuts = {}

    def _getTempCount(self,sampleName,selection,scalefactor,**kwargs):
        '''Get a temporary count'''
        analysis = kwargs.pop('analysis',self.analysis)
        hist = self.sampleFiles[analysis][sampleName].getTempCount(selection,scalefactor)
        val = hist.GetBinContent(1) if hist else 0.
        err = hist.GetBinError(1) if hist else 0.
        return val,err

    def getCount(self,processName,selection,scalefactor,**kwargs):
        total = [0.,0.]
        for sampleName in self.processDict[processName]:
            sel = selection
            if processName in self.processSampleCuts:
                if sampleName in self.processSampleCuts[processName]:
                    sel = '{0} && {1}'.format(selection,self.processSampleCuts[processName][sampleName])
            thisCount = self._getTempCount(sampleName,sel,scalefactor)
            total = sumWithError(total,thisCount)
        return total

    def printEfficiency(self,selectionList,baseSelection='1',**kwargs):
        '''
        Pretty print the efficiency
        Cut, process1 eff, process1 n-1 eff, ...
        '''
        headers = ['Cut']
        baseYields = {}
        fullYields = {}
        lastRow = ['Full selection']
        for processName in self.processOrder:
            headers += ['{0} Eff.'.format(processName), '{0} N-1 Eff'.format(processName)]
            baseYields[processName] = self.getCount(processName,baseSelection,'1')
            fullYields[processName] = self.getCount(processName,' && '.join(selectionList+[baseSelection]),'1')
            fullEff = divWithError(fullYields[processName],baseYields[processName])
            fullEffString = '{0:5.3f} +/- {1:5.3f}'.format(*fullEff)
            lastRow += [fullEffString,'---']
        table = PrettyTable(headers)
        table.align = 'r'
        table.align['Cut'] = 'l'
        for selection in selectionList:
            thisRow = [selection]
            nMinusOneSelections = [x for x in selectionList if x!=selection]
            for processName in self.processOrder:
                selectionOnly = self.getCount(processName,'{0} && {1}'.format(selection,baseSelection),'1')
                allButSelection = self.getCount(processName,' && '.join(nMinusOneSelections+[baseSelection]),'1')
                eff = divWithError(selectionOnly,baseYields[processName])
                nMinusOneEff = divWithError(fullYields[processName],allButSelection)
                effString = '{0:5.3f} +/- {1:5.3f}'.format(*eff)
                nMinusOneEffString = '{0:5.3f} +/- {1:5.3f}'.format(*nMinusOneEff)
                thisRow += [effString,nMinusOneEffString]
            table.add_row(thisRow)
        table.add_row(lastRow)
        print table.get_string()
