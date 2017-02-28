import logging
import os
import sys
import glob
import json
import pickle
import time

sys.argv.append('-b')
import ROOT
sys.argv.pop()

ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 2001;")

from DevTools.Plotter.xsec import getXsec
from DevTools.Plotter.utilities import getLumi, isData, hashFile, hashString, python_mkdir, getTreeName, getNtupleDirectory, getProjectionHistograms
from DevTools.Plotter.histParams import getHistParams, getHistSelections, getProjectionParams

try:
    from progressbar import ProgressBar, ETA, Percentage, Bar, SimpleProgress
    hasProgress = True
except:
    hasProgress = False

CMSSW_BASE = os.environ['CMSSW_BASE']

class NtupleFlattener(object):
    '''Loop over tree and store weights'''

    def __init__(self,analysis,sample,**kwargs):
        # default to access via sample/analysis
        self.analysis = analysis
        self.sample = sample
        self.shift = kwargs.pop('shift','')
        self.isData = isData(self.sample)
        logging.debug('Initializing {0} {1} {2}'.format(self.analysis,self.sample,self.shift))
        # backup passing custom parameters
        self.ntupleDirectory = kwargs.pop('ntupleDirectory','{0}/{1}'.format(getNtupleDirectory(self.analysis,shift=self.shift),self.sample))
        self.inputFileList = kwargs.pop('inputFileList','')
        self.outputFile = kwargs.pop('outputFile',getProjectionHistograms(self.analysis,self.sample,shift=self.shift))
        self.treeName = kwargs.pop('treeName',getTreeName(self.analysis))
        if hasProgress:
            self.pbar = kwargs.pop('progressbar',ProgressBar(widgets=['{0}: '.format(sample),' ',SimpleProgress(),' events ',Percentage(),' ',Bar(),' ',ETA()]))
        else:
            self.pbar = None
        # get stuff needed to flatten
        self.infile = 0
        self.tchain = 0
        self.initialized = False
        self.hists = {}
        self.__initializeHistograms()

    def __initializeNtuple(self):
        tchain = ROOT.TChain(self.treeName)
        if self.inputFileList: # reading from a passed list of inputfiles
            allFiles = []
            with open(self.inputFileList,'r') as f:
                for line in f.readlines():
                   allFiles += [line.strip()]
        else: # reading from an input directory (all files in directory will be processed)
            allFiles = glob.glob('{0}/*.root'.format(self.ntupleDirectory))
        if len(allFiles)==0: logging.error('No files found for sample {0}'.format(self.sample))
        summedWeights = 0.
        for f in allFiles:
            tfile = ROOT.TFile.Open(f)
            summedWeights += tfile.Get("summedWeights").GetBinContent(1)
            tfile.Close()
            tchain.Add(f)
        if not summedWeights and not isData(self.sample): logging.warning('No events for sample {0}'.format(self.sample))
        self.intLumi = float(getLumi())
        self.xsec = getXsec(self.sample)
        self.sampleLumi = float(summedWeights)/self.xsec if self.xsec else 0.
        self.sampleTree = tchain
        self.files = allFiles
        self.initialized = True
        logging.debug('Initialized {0}: summedWeights = {1}; xsec = {2}; sampleLumi = {3}; intLumi = {4}'.format(self.sample,summedWeights,self.xsec,self.sampleLumi,self.intLumi))

    def __initializeHistograms(self):
        chans = ['all']
        genChans = ['all']
        if hasattr(self,'channels'): chans += self.channels
        if hasattr(self,'genChannels'): genChans += self.genChannels
        if not hasattr(self,'selections'): self.selections = ['default']
        for selection in self.selections:
            for hist in self.histParams:
                for chan in chans:
                    for genChan in genChans:
                        histName = '{0}/{1}/{2}/gen_{3}'.format(selection,hist,chan,genChan)
                        if genChan=='all': histName = '{0}/{1}/{2}'.format(selection,hist,chan)
                        if chan=='all': histName = '{0}/{1}'.format(selection,hist)
                        xbins = self.histParams[hist]['xBinning']
                        self.hists[histName] = ROOT.TH1F(histName,histName,xbins[0],xbins[1],xbins[2])

    def getTree(self):
        if not self.initialized: self.__initializeNtuple()
        return self.sampleTree

    def getSampleLumi(self):
        if not self.initialized: self.__initializeNtuple()
        return self.sampleLumi

    def getIntLumi(self):
        if not self.initialized: self.__initializeNtuple()
        return self.intLumi

    def flush(self):
        sys.stdout.flush()
        sys.stderr.flush()

    def flatten(self):
        '''
        Primary access loop for flattening.
        '''
        self.__initializeNtuple()
        self.totalEntries = self.sampleTree.GetEntries()
        total = 0
        start = time.time()
        new = start
        old = start
        if hasProgress and self.pbar:
            self.pbar.maxval = self.totalEntries
            self.pbar.start()
            for row in self.sampleTree:
                total += 1
                self.pbar.update(total)
                self.perRowAction(row)
            print ''
        else:
            logging.info('Flattening {0} {1}'.format(self.analysis,self.sample))
            for row in self.sampleTree:
                total += 1
                if total==2: start = time.time() # just ignore first event for timing
                if total % 1000 == 1:
                    cur = time.time()
                    elapsed = cur-start
                    remaining = float(elapsed)/total * float(self.totalEntries) - float(elapsed)
                    mins, secs = divmod(int(remaining),60)
                    hours, mins = divmod(mins,60)
                    logging.info('{0}: Processing event {1}/{2} - {3}:{4:02d}:{5:02d} remaining'.format(self.analysis,total,self.totalEntries,hours,mins,secs))
                    self.flush()
                self.perRowAction(row)

    def perRowAction(self,row):
        '''
        Action to be performed on each row. Override.
        '''
        return

    def fill(self,row,selection,weight,chan,genChan='all'):
        '''Fill a histogram'''
        if weight!=weight:
            logging.warning('{0} {1} {2} attempted to add NaN weight'.format(histName,chan,genChan))
        for hist in self.histParams:
            val = self.histParams[hist]['x'](row)
            w = weight*self.histParams[hist]['mcscale'](row) if 'mcscale' in self.histParams[hist] and self.isData else weight
            histName = '{0}/{1}'.format(selection,hist)
            self.hists[histName].Fill(val,w)
            histName = '{0}/{1}/{2}'.format(selection,hist,chan)
            self.hists[histName].Fill(val,w)
            if genChan!='all':
                histName = '{0}/{1}/{2}/gen_{3}'.format(selection,hist,chan,genChan)
                self.hists[histName].Fill(val,w)

