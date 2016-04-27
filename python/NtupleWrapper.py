import logging
import os
import sys
import glob
import json

sys.argv.append('-b')
import ROOT
sys.argv.pop()

ROOT.gROOT.SetBatch(ROOT.kTRUE)

from DevTools.Plotter.xsec import getXsec
from DevTools.Plotter.utilities import getLumi, isData, hashFile, hashString, python_mkdir, getTreeName, getNtupleDirectory
from DevTools.Plotter.histParams import getHistParams, getHistParams2D, getHistSelections

CMSSW_BASE = os.environ['CMSSW_BASE']

class NtupleWrapper(object):
    '''Wrapper for access to ntuples'''

    def __init__(self,analysis,sample,**kwargs):
        # default to access via sample/analysis
        self.analysis = analysis
        self.sample = sample
        # backup passing custom parameters
        self.ntuple = kwargs.pop('ntuple','{0}/src/ntuples/{1}/{2}.root'.format(CMSSW_BASE,self.analysis,self.sample))
        self.ntupleDirectory = kwargs.pop('ntupleDirectory','{0}/{1}'.format(getNtupleDirectory(self.analysis),self.sample))
        self.treeName = kwargs.pop('treeName',getTreeName(self.analysis))
        self.flat = kwargs.pop('flat','flat/{0}/{1}.root'.format(self.analysis,self.sample))
        # get stuff needed to flatten
        self.histParams = getHistParams(self.analysis)
        self.histParams2D = getHistParams2D(self.analysis)
        self.selections = getHistSelections(self.analysis,self.sample)
        self.outfile = 0
        self.tchain = 0
        self.j = 0
        self.initialized = False

    def __exit__(self, type, value, traceback):
        self.__finish()

    def __del__(self):
        self.__finish()

    def __finish(self):
        if self.outfile:
            self.outfile.Close()

    def __initializeNtuple(self):
        tchain = ROOT.TChain(self.treeName)
        if os.path.isfile(self.ntuple):
            allFiles = [self.ntuple]
        else:
            allFiles = glob.glob('{0}/*.root'.format(self.ntupleDirectory))
        summedWeights = 0.
        for f in allFiles:
            tfile = ROOT.TFile.Open(f)
            summedWeights += tfile.Get("summedWeights").GetBinContent(1)
            tfile.Close()
            tchain.Add(f)
        self.intLumi = getLumi()
        self.xsec = getXsec(self.sample)
        self.sampleLumi = float(summedWeights)/self.xsec if self.xsec else 0.
        self.sampleTree = tchain
        self.files = allFiles
        self.initialized = True
        self.fileHash = hashFile(*self.files)

    def __write(self,hist,directory=''):
        self.outfile = ROOT.TFile(self.flat,'update')
        if not self.outfile.GetDirectory(directory): self.outfile.mkdir(directory)
        self.outfile.cd('{0}:/{1}'.format(self.flat,directory))
        hist.Write('',ROOT.TObject.kOverwrite)
        self.outfile.Close()

    def __read(self,variable):
        '''Read the histogram from file'''
        # attempt to read the histogram
        infile = ROOT.TFile(self.flat,'read')
        hist = infile.Get(variable)
        if hist:
            hist = hist.Clone('h_{0}_{1}'.format(self.sample,variable.replace('/','_')))
            #hist.Sumw2()
            hist.SetDirectory(0)
            return hist
        else:
            logging.info('Histogram {0} not found for {1}, attempt to flatten'.format(variable,self.sample))
        infile.Close()
        # attempt to flatten the histogram
        varComponents = variable.split('/')
        selection = '/'.join(varComponents[:-1])
        if selection not in self.selections:
            logging.error('{0}: unknown, {1} not found in histSelections.'.format(variable,directory))
            return 0
        sels = self.selections[selection]
        histName = varComponents[-1]
        if histName not in self.histParams and histName not in self.histParams2D:
            logging.error('{0}: unknown, {1} not found in histParams.'.format(variable,histName))
            return 0
        if histName in self.histParams: # 1D
            params = self.histParams[histName]
            self.__flatten(sels['args'][0],histName,params,**sels['kwargs'])
        else: # 2D
            params = self.histParams2D[histName]
            self.__flatten(sels['args'][0],histName,params,**sels['kwargs'])
        # now get it again
        infile = ROOT.TFile(self.flat,'read')
        hist = infile.Get(variable)
        if hist:
            hist = hist.Clone('h_{0}_{1}'.format(self.sample,variable.replace('/','_')))
            hist.Sumw2()
            return hist
        return 0

    def __checkHash(self,name,directory,strings=[]):
        'Check the hash for a sample'''
        if not self.initialized: self.__initializeNtuple()
        self.outfile = ROOT.TFile(self.flat,'update')
        hashDirectory = 'hash/{0}'.format(directory)
        hashObj = self.outfile.Get('{0}/{1}'.format(hashDirectory,name))
        if not hashObj:
            hashObj = ROOT.TNamed(name,'')
        oldHash = hashObj.GetTitle()
        newHash = self.fileHash + hashString(*strings)
        if oldHash==newHash:
            self.outfile.Close()
            return True
        else:
            hashObj.SetTitle(newHash)
            if not self.outfile.GetDirectory(hashDirectory): self.outfile.mkdir(hashDirectory)
            self.outfile.cd('{0}:/{1}'.format(self.flat,hashDirectory))
            hashObj.Write('',ROOT.TObject.kOverwrite)
            self.outfile.Close()
            return False

    def __flatten(self,directory,histName,selection,params,**kwargs):
        '''Produce flat histograms for a given selection.'''
        # clear old
        ROOT.gDirectory.Delete('h_*')
        ROOT.gDirectory.Delete(histName)
        # selections
        mccut = kwargs.pop('mccut','')
        datacut = kwargs.pop('datacut','')
        if datacut and isData(self.sample): selection += ' && {0}'.format(datacut)
        if mccut and not isData(self.sample): selection += ' && {0}'.format(mccut)
        if 'selection' in params: selection += ' && {0}'.format(params['selection'])
        # scalefactor
        scalefactor = kwargs.pop('scalefactor','1' if isData(self.sample) else 'genWeight')
        mcscalefactor = kwargs.pop('mcscalefactor','')
        datascalefactor = kwargs.pop('datascalefactor','')
        if datascalefactor and isData(self.sample): scalefactor = datascalefactor
        if mcscalefactor and not isData(self.sample): scalefactor = mcscalefactor
        if 'scale' in params: scalefactor += '*{0}'.format(params['scale'])
        if 'mcscale' in params and not isData(self.sample): scalefactor += '*{0}'.format(params['mcscale'])
        if 'datascale' in params and isData(self.sample): scalefactor += '*{0}'.format(params['datascale'])
        # verify output file directory exists
        os.system('mkdir -p {0}'.format(os.path.dirname(self.flat)))
        # check if we need to draw the hist, or if the one in the ntuple is the latest
        if 'variable' in params: # 1D
             hashExists = self.__checkHash(histName,directory,strings=[params['variable'],', '.join([str(x) for x in params['binning']]),scalefactor,selection])
        else: # 2D
             hashExists = self.__checkHash(histName,directory,strings=[params['yVariable'],params['xVariable'],', '.join([str(x) for x in params['xBinning']+params['yBinning']]),scalefactor,selection])
        if hashExists:
            self.__finish()
            return
        # get the histogram
        name = histName
        self.j += 1
        tempName = 'h_{0}_{1}_{2}'.format(name,self.sample,self.j)
        if 'variable' in params: # 1D
            hist = self.__getHist(tempName,selection,scalefactor,params['variable'],params['binning'])
        else: # 2D
            hist = self.__getHist2D(tempName,selection,scalefactor,params['xVariable'],params['yVariable'],params['xBinning'],params['yBinning'])
        hist.SetTitle(name)
        hist.SetName(name)
        # save to file
        self.__write(hist,directory=directory)

    def __getHist(self,histName,selection,scalefactor,variable,binning):
        if not self.initialized: self.__initializeNtuple()
        if not isData(self.sample): scalefactor = '{0}*{1}'.format(scalefactor,float(self.intLumi)/self.sampleLumi)
        drawString = '{0}>>{1}({2})'.format(variable,histName,', '.join([str(x) for x in binning]))
        selectionString = '{0}*({1})'.format(scalefactor,selection)
        tree = self.sampleTree
        if not tree: ROOT.TH1F(histName,histName,*binning)
        tree.Draw(drawString,selectionString,'goff')
        if ROOT.gDirectory.Get(histName):
            hist = ROOT.gDirectory.Get(histName)
        else:
            hist = ROOT.TH1F(histName,histName,*binning)
        return hist

    def __getHist2D(self,histName,selection,scalefactor,xVariable,yVariable,xBinning,yBinning):
        if not self.initialized: self.__initializeNtuple()
        if not isData(self.sample): scalefactor = '{0}*{1}'.format(scalefactor,float(self.intLumi)/self.sampleLumi)
        binning = xBinning+yBinning
        drawString = '{0}:{1}>>{2}({3})'.format(yVariable,xVariable,histName,', '.join([str(x) for x in binning]))
        selectionString = '{0}*({1})'.format(scalefactor,selection)
        tree = self.sampleTree
        if not tree: ROOT.TH2F(histName,histName,*binning)
        tree.Draw(drawString,selectionString,'goff')
        if ROOT.gDirectory.Get(histName):
            hist = ROOT.gDirectory.Get(histName)
        else:
            hist = ROOT.TH2F(histName,histName,*binning)
        return hist

    def getHist(self,variable):
        '''Get a histogram'''
        return self.__read(variable)

    def getTempHist(self,histName,selection,scalefactor,variable,binning):
        '''Get a histogram that is not saved in flat ntuple.'''
        return self.__getHist(histName,selection,scalefactor,variable,binning)

    def getTempCount(self,selection,scalefactor):
        '''Get a histogram that is a single bin of counts with statistical error'''
        return self.__getHist('count',selection,scalefactor,'1',[1,0,2])

    def flatten(self,histName,selectionName):
        '''Flatten a histogram'''
        if histName not in self.histParams:
            logging.error('Unrecognized histogram {0}'.format(histName))
        params = self.histParams[histName]
        if selectionName not in self.selections:
            logging.error('Unrecognized selection {0}'.format(selectionName))
        selection = self.selections[selectionName]['args'][0]
        kwargs = self.selections[selectionName]['kwargs']
        self.__flatten(selectionName,histName,selection,params,**kwargs)

    def flatten2D(self,histName,selectionName):
        '''Flatten a 2D histogram'''
        if histName not in self.histParams2D:
            logging.error('Unrecognized histogram {0}'.format(histName))
        params = self.histParams2D[histName]
        if selectionName not in self.selections:
            logging.error('Unrecognized selection {0}'.format(selectionName))
        selection = self.selections[selectionName]['args'][0]
        kwargs = self.selections[selectionName]['kwargs']
        self.__flatten(selectionName,histName,selection,params,**kwargs)


