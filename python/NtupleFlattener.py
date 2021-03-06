import logging
import os
import fnmatch
import sys
import glob
import json
import pickle
import time
from array import array
import numbers
from collections import OrderedDict

sys.argv.append('-b')
import ROOT
sys.argv.pop()

ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 2001;")

from DevTools.Plotter.xsec import getXsec
from DevTools.Plotter.utilities import getLumi, isData, hashFile, hashString, python_mkdir, getTreeName, getNtupleDirectory, getNewFlatHistograms

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
        self.skipHists = kwargs.pop('skipHists',False)
        self.isData = isData(self.sample)
        self.intLumi = kwargs.get('intLumi',float(getLumi()))
        logging.debug('Initializing {0} {1} {2}'.format(self.analysis,self.sample,self.shift))
        # backup passing custom parameters
        self.ntupleDirectory = kwargs.pop('ntupleDirectory','{0}/{1}'.format(getNtupleDirectory(self.analysis,shift=self.shift),self.sample))
        self.inputFileList = kwargs.pop('inputFileList','')
        self.outputFile = kwargs.pop('outputFile',getNewFlatHistograms(self.analysis,self.sample,shift=self.shift))
        if os.path.dirname(self.outputFile): python_mkdir(os.path.dirname(self.outputFile))
        self.treeName = kwargs.pop('treeName',getTreeName(self.analysis))
        if hasProgress:
            self.pbar = kwargs.pop('progressbar',ProgressBar(widgets=['{0}: '.format(sample),' ',SimpleProgress(),' ',Percentage(),' ',Bar(),' ',ETA()]))
        else:
            self.pbar = None
        # get stuff needed to flatten
        self.infile = 0
        self.tchain = 0
        self.initialized = False
        self.hists = {}
        self.datasets = {}

    def __initializeNtuple(self):
        tchain = ROOT.TChain(self.treeName)
        if self.inputFileList: # reading from a passed list of inputfiles
            allFiles = []
            with open(self.inputFileList,'r') as f:
                for line in f.readlines():
                   allFiles += [line.strip()]
        else: # reading from an input directory (all files in directory will be processed)
            #allFiles = glob.glob('{0}/*.root'.format(self.ntupleDirectory))
            allFiles = []
            for root, dirnames, fnames in os.walk(self.ntupleDirectory):
                if 'failed' in root: continue
                for fname in fnmatch.filter(fnames, '*.root'):
                    allFiles.append(os.path.join(root,fname))
        if len(allFiles)==0: logging.error('No files found for sample {0}'.format(self.sample))
        summedWeights = 0.
        for f in allFiles:
            tfile = ROOT.TFile.Open(f)
            summedWeights += tfile.Get("summedWeights").GetBinContent(1)
            tfile.Close()
            tchain.Add(f)
        if not summedWeights and not isData(self.sample): logging.warning('No events for sample {0}'.format(self.sample))
        self.xsec = getXsec(self.sample)
        self.sampleLumi = float(summedWeights)/self.xsec if self.xsec else 0.
        self.sampleTree = tchain
        self.files = allFiles
        self.initialized = True
        logging.debug('Initialized {0}: summedWeights = {1}; xsec = {2}; sampleLumi = {3}; intLumi = {4}'.format(self.sample,summedWeights,self.xsec,self.sampleLumi,self.intLumi))

    def __initializeHistograms(self):
        if self.skipHists: self.histParams = {}
        chans = ['all']
        genChans = ['all']
        if hasattr(self,'channels'): chans += self.channels
        if hasattr(self,'genChannels'): genChans += self.genChannels
        if not hasattr(self,'selections'): self.selections = ['default']
        if not hasattr(self,'selectionHists'): self.selectionHists = {}
        if not hasattr(self,'datasetParams'): self.datasetParams = {}
        if not hasattr(self,'textSelections'): self.textSelections = []
        if not hasattr(self,'textFields'): self.textFields = OrderedDict()
        for selection in self.selections:
            for hist in self.histParams:
                if selection in self.selectionHists:
                    if hist not in self.selectionHists[selection]: continue
                if 'doGen' in self.histParams[hist] and self.histParams[hist]['doGen']:
                    thisGenChans = genChans
                else:
                    thisGenChans = ['all']
                for chan in chans:
                    for genChan in thisGenChans:
                        histName = '{0}/{1}/gen_{2}/{3}'.format(selection,chan,genChan,hist)
                        if genChan=='all': histName = '{0}/{1}/{2}'.format(selection,chan,hist)
                        if chan=='all': histName = '{0}/{1}'.format(selection,hist)
                        xbins = self.histParams[hist].get('xBinning',[])
                        if 'yBinning' in self.histParams[hist]:
                            ybins = self.histParams[hist]['yBinning']
                            if isinstance(xbins,array) and isinstance(ybins,array): # variable width array
                                self.hists[histName] = ROOT.TH2D(histName,histName,len(xbins)-1,xbins,len(ybins)-1,ybins)
                            elif len(xbins)==3 and len(ybins)==3 and all([isinstance(x,numbers.Number) for x in xbins]) and all([isinstance(x,numbers.Number) for x in ybins]): # n, low, high
                                self.hists[histName] = ROOT.TH2D(histName,histName,xbins[0],xbins[1],xbins[2],ybins[0],ybins[1],ybins[2])
                            elif len(xbins)>0 and len(ybins)>0:
                                self.hists[histName] = ROOT.TH2D(histName,histName,len(xbins),0,len(xbins),len(ybins),0,len(ybins))
                                for i,label in enumerate(xbins):
                                    self.hists[histName].GetXaxis().SetBinLabel(i+1,str(label))
                                for i,label in enumerate(ybins):
                                    self.hists[histName].GetYaxis().SetBinLabel(i+1,str(label))
                            else:
                                self.hists[histName] = ROOT.TH2D()
                                self.hists[histName].SetName(histName)
                                self.hists[histName].SetTitle(histName)
                        else:
                            if isinstance(xbins,array): # variable width array
                                self.hists[histName] = ROOT.TH1D(histName,histName,len(xbins)-1,xbins)
                            elif len(xbins)==3 and all([isinstance(x,numbers.Number) for x in xbins]): # n, low, high
                                self.hists[histName] = ROOT.TH1D(histName,histName,xbins[0],xbins[1],xbins[2])
                            elif len(xbins)>0:
                                self.hists[histName] = ROOT.TH1D(histName,histName,len(xbins),0,len(xbins))
                                for i,label in enumerate(xbins):
                                    self.hists[histName].GetXaxis().SetBinLabel(i+1,label)
                            else:
                                self.hists[histName] = ROOT.TH1D()
                                self.hists[histName].SetName(histName)
                                self.hists[histName].SetTitle(histName)
                        self.hists[histName].Sumw2()
            for hist in self.datasetParams:
                if 'doGen' in self.datasetParams[hist] and self.datasetParams[hist]['doGen']:
                    thisGenChans = genChans
                else:
                    thisGenChans = ['all']
                for chan in chans:
                    for genChan in thisGenChans:
                        histName = '{0}/{1}/gen_{2}/{3}'.format(selection,chan,genChan,hist)
                        if genChan=='all': histName = '{0}/{1}/{2}'.format(selection,chan,hist)
                        if chan=='all': histName = '{0}/{1}'.format(selection,hist)
                        x = self.datasetParams[hist].get('xVar',None)
                        w = self.datasetParams[hist].get('wVar',None)
                        if 'yVar' in self.datasetParams[hist]:
                            y = self.datasetParams[hist].get('yVar',None)
                            self.datasets[histName] = ROOT.RooDataSet(histName,histName,ROOT.RooArgSet(x,y,w))#,w.GetName())
                        else:
                            self.datasets[histName] = ROOT.RooDataSet(histName,histName,ROOT.RooArgSet(x,w))#,w.GetName())
        for selection in self.textSelections:
            outdir = 'text/{}/{}/{}'.format(self.analysis,self.sample,selection)
            python_mkdir(outdir)
            outfile = '{}/events.csv'.format(outdir)
            with open(outfile,'w') as f:
                f.write(','.join(self.textFields.keys())+',weight\n')


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
        self.__initializeHistograms()
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
            self.pbar.finish()
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
                    logging.info('{0}: Processing {1} event {2}/{3} - {4}:{5:02d}:{6:02d} remaining'.format(self.analysis,self.sample,total,self.totalEntries,hours,mins,secs))
                    self.flush()
                self.perRowAction(row)
        self.write()

    def write(self):
        '''
        Write histograms to files
        '''
        total = 0
        totalHists = len(self.hists)+len(self.datasets)
        if hasProgress and self.pbar:
            self.pbar.maxval = totalHists
            self.pbar.start()
        else:
            logging.info('Writing histograms')
        self.outfile = ROOT.TFile(self.outputFile,'update')
        for h in sorted(self.hists):
            total += 1
            if hasProgress and self.pbar:
                self.pbar.update(total)
            else:
                logging.info('{0}: Writing {1} histogram {2}/{3} {4}'.format(self.analysis,self.sample,total,totalHists,h))
            components = h.split('/')
            directory = '/'.join(components[:-1])
            histName = components[-1]
            hist = self.hists[h]
            hist.SetName(histName)
            hist.SetTitle(histName)
            if not self.outfile.GetDirectory(directory): self.outfile.mkdir(directory)
            self.outfile.cd('{0}:/{1}'.format(self.outputFile,directory))
            hist.Write('',ROOT.TObject.kOverwrite)
        for h in sorted(self.datasets):
            total += 1
            if hasProgress and self.pbar:
                self.pbar.update(total)
            else:
                logging.info('{0}: Writing {1} dataset {2}/{3} {4}'.format(self.analysis,self.sample,total,totalHists,h))
            components = h.split('/')
            directory = '/'.join(components[:-1])
            histName = components[-1]
            hist = self.datasets[h]
            hist.SetName(histName)
            hist.SetTitle(histName)
            if not self.outfile.GetDirectory(directory): self.outfile.mkdir(directory)
            self.outfile.cd('{0}:/{1}'.format(self.outputFile,directory))
            hist.Write('',ROOT.TObject.kOverwrite)
        if hasProgress and self.pbar:
            self.pbar.finish()
        self.outfile.Close()


    def perRowAction(self,row):
        '''
        Action to be performed on each row. Override.
        '''
        return

    def fill(self,row,selection,weight,chan='all',genChan='all'):
        '''Fill a histogram'''
        if weight!=weight:
            logging.warning('{0} {1} {2} attempted to add NaN weight'.format(histName,chan,genChan))
        for hist in self.histParams:
            if selection in self.selectionHists:
                if hist not in self.selectionHists[selection]: continue
            if 'selection' in self.histParams:
                if not self.histParams[hist]['selection'](row): continue
            w = weight*self.histParams[hist]['mcscale'](row) if 'mcscale' in self.histParams[hist] and self.isData else weight
            histName = '{0}/{1}'.format(selection,hist)
            xval = self.histParams[hist]['x'](row)
            if 'y' in self.histParams[hist]:
                yval = self.histParams[hist]['y'](row)
                self.hists[histName].Fill(xval,yval,w)
                if chan!='all':
                    histName = '{0}/{1}/{2}'.format(selection,chan,hist)
                    self.hists[histName].Fill(xval,yval,w)
                if genChan!='all':
                    histName = '{0}/{1}/gen_{2}/{3}'.format(selection,chan,genChan,hist)
                    if histName in self.hists: self.hists[histName].Fill(xval,yval,w)
            else:
                self.hists[histName].Fill(xval,w)
                if chan!='all':
                    histName = '{0}/{1}/{2}'.format(selection,chan,hist)
                    self.hists[histName].Fill(xval,w)
                if genChan!='all':
                    histName = '{0}/{1}/gen_{2}/{3}'.format(selection,chan,genChan,hist)
                    if histName in self.hists: self.hists[histName].Fill(xval,w)

        for hist in self.datasetParams:
            wval = weight*self.datasetParams[hist]['mcscale'](row) if 'mcscale' in self.datasetParams[hist] and self.isData else weight
            if not wval:
                continue
            w = self.datasetParams[hist]['wVar']
            w.setVal(wval)
            histName = '{0}/{1}'.format(selection,hist)
            xval = self.datasetParams[hist]['x'](row)
            x = self.datasetParams[hist]['xVar']
            x.setVal(xval)
            if 'y' in self.datasetParams[hist]:
                yval = self.datasetParams[hist]['y'](row)
                y = self.datasetParams[hist]['yVar']
                y.setVal(yval)
                self.datasets[histName].add(ROOT.RooArgSet(x,y,w))
                if chan!='all':
                    histName = '{0}/{1}/{2}'.format(selection,chan,hist)
                    self.datasets[histName].add(ROOT.RooArgSet(x,y,w))
                if genChan!='all':
                    histName = '{0}/{1}/gen_{2}/{3}'.format(selection,chan,genChan,hist)
                    if histName in self.datasets: self.datasets[histName].add(ROOT.RooArgSet(x,y,w))
            else:
                self.datasets[histName].add(ROOT.RooArgSet(x,w))
                if chan!='all':
                    histName = '{0}/{1}/{2}'.format(selection,chan,hist)
                    self.datasets[histName].add(ROOT.RooArgSet(x,w))
                if genChan!='all':
                    histName = '{0}/{1}/gen_{2}/{3}'.format(selection,chan,genChan,hist)
                    if histName in self.datasets: self.datasets[histName].add(ROOT.RooArgSet(x,w))

        if selection in self.textSelections:
            outdir = 'text/{}/{}/{}'.format(self.analysis,self.sample,selection)
            outfile = '{}/events.csv'.format(outdir)
            with open(outfile,'a') as f:
                f.write(','.join(['{}'.format(self.textFields[k](row)) for k in self.textFields.keys()])+',{}\n'.format(weight))


