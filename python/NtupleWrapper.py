import logging
import os
import sys
import glob
import json
import pickle

sys.argv.append('-b')
import ROOT
sys.argv.pop()

ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 2001;")

from DevTools.Plotter.xsec import getXsec
from DevTools.Plotter.utilities import *
from DevTools.Plotter.histParams import getHistParams, getHistSelections, getProjectionParams

CMSSW_BASE = os.environ['CMSSW_BASE']

class NtupleWrapper(object):
    '''Wrapper for access to ntuples'''

    def __init__(self,analysis,sample,**kwargs):
        # default to access via sample/analysis
        self.new = kwargs.pop('new',False)
        self.version = kwargs.pop('version',getCMSSWVersion())
        self.analysis = analysis
        self.sample = sample
        self.shift = kwargs.pop('shift','')
        self.useProof = kwargs.pop('useProof',False)
        self.intLumi = kwargs.pop('intLumi',float(getLumi()))
        logging.debug('Initializing {0} {1} {2}'.format(self.analysis,self.sample,self.shift))
        # backup passing custom parameters
        #self.ntuple = kwargs.pop('ntuple','{0}/src/ntuples/{1}/{2}.root'.format(CMSSW_BASE,self.analysis,self.sample))
        self.ntupleDirectory = kwargs.pop('ntupleDirectory','{0}/{1}'.format(getNtupleDirectory(self.analysis,shift=self.shift,version=self.version),self.sample))
        if self.useProof: self.ntupleDirectory.replace('-merge','')
        self.inputFileList = kwargs.pop('inputFileList','')
        self.treeName = kwargs.pop('treeName',getTreeName(self.analysis))
        #self.flat = kwargs.pop('flat','flat/{0}/{1}.root'.format(self.analysis,self.sample))
        flat = getNewFlatHistograms if self.new else getFlatHistograms
        proj = getNewProjectionHistograms if self.new else getProjectionHistograms
        self.flat = kwargs.pop('flat',flat(self.analysis,self.sample,shift=self.shift,version=self.version))
        self.proj = kwargs.pop('proj',proj(self.analysis,self.sample,shift=self.shift,version=self.version))
        self.json = kwargs.pop('json',getSkimJson(self.analysis,self.sample,shift=self.shift,version=self.version))
        self.pickle = kwargs.pop('pickle',getSkimPickle(self.analysis,self.sample,shift=self.shift,version=self.version))
        self.skimInitialized = False
        # get stuff needed to flatten
        self.histParams = getHistParams(self.analysis,self.sample,shift=self.shift,version=self.version,**kwargs)
        self.selections = getHistSelections(self.analysis,self.sample,shift=self.shift,version=self.version,**kwargs)
        self.projections = getProjectionParams(self.analysis,self.sample,shift=self.shift,version=self.version,**kwargs)
        self.infile = 0
        self.outfile = 0
        self.j = 0
        self.initialized = False
        self.temp = True
        if self.useProof:
            self.proof = ROOT.TProof.Open('')
        # verify output file directory exists
        os.system('mkdir -p {0}'.format(os.path.dirname(self.flat)))
        os.system('mkdir -p {0}'.format(os.path.dirname(self.proj)))
        self.entryListMap = {}

    def __exit__(self, type, value, traceback):
        self.__finish()

    def __del__(self):
        self.__finish()

    def __finish(self):
        if self.infile:
            self.infile.Close()
        if self.outfile:
            self.outfile.Close()

    def __initializeNtuple(self):
        tchain = ROOT.TChain(self.treeName)
        if self.inputFileList: # reading from a passed list of inputfiles
            allFiles = []
            with open(self.inputFileList,'r') as f:
                for line in f.readlines():
                   allFiles += [line.strip()]
        else: # reading from an input directory (all files in directory will be processed)
            allFiles = glob.glob('{0}/*.root'.format(self.ntupleDirectory))
        #elif os.path.isfile(self.ntuple): # reading a single root file
        #    allFiles = [self.ntuple]
        if len(allFiles)==0: logging.error('No files found for sample {0}'.format(self.sample))
        summedWeights = 0.
        for f in allFiles:
            tfile = ROOT.TFile.Open(f)
            summedWeights += tfile.Get("summedWeights").GetBinContent(1)
            tfile.Close()
            tchain.Add(f)
        if not summedWeights and not isData(self.sample): logging.warning('No events for sample {0}'.format(self.sample))
        self.xsec = getXsec(self.sample)
        if not self.xsec: logging.error('No xsec for sample {0}'.format(self.sample))
        self.sampleLumi = float(summedWeights)/self.xsec if self.xsec else 0.
        self.sampleTree = tchain
        self.j += 1
        #listname = 'selList{0}'.format(self.j)
        #self.sampleTree.Draw('>>{0}'.format(listname),'1','entrylist')
        #skim = ROOT.gDirectory.Get(listname)
        #self.entryListMap['1'] = skim
        self.files = allFiles
        self.initialized = True
        if not self.temp: self.fileHash = hashFile(*self.files)
        if self.useProof: self.sampleTree.SetProof()
        logging.debug('Initialized {0}: summedWeights = {1}; xsec = {2}; sampleLumi = {3}; intLumi = {4}'.format(self.sample,summedWeights,self.xsec,self.sampleLumi,self.intLumi))

    def getTree(self):
        if not self.initialized: self.__initializeNtuple()
        return self.sampleTree

    def getSampleLumi(self):
        if not self.initialized: self.__initializeNtuple()
        return self.sampleLumi

    def getIntLumi(self):
        if not self.initialized: self.__initializeNtuple()
        return self.intLumi

    def __write(self,hist,directory=''):
        if self.temp: return
        self.outfile = ROOT.TFile(self.flat,'update')
        if not self.outfile.GetDirectory(directory): self.outfile.mkdir(directory)
        self.outfile.cd('{0}:/{1}'.format(self.flat,directory))
        hist.Write('',ROOT.TObject.kOverwrite)
        self.outfile.Close()

    def __writeProjection(self,hist,directory=''):
        if self.temp: return
        self.outfile = ROOT.TFile(self.proj,'update')
        if not self.outfile.GetDirectory(directory): self.outfile.mkdir(directory)
        self.outfile.cd('{0}:/{1}'.format(self.proj,directory))
        hist.Write('',ROOT.TObject.kOverwrite)
        self.outfile.Close()

    def __read(self,variable):
        '''Read the histogram from file'''
        # attempt to read
        if os.path.isfile(self.proj):
            infile = ROOT.TFile(self.proj,'read')
            hist = infile.Get(variable)
            if hist:
                self.j += 1
                hist = hist.Clone('h_{0}_{1}_{2}'.format(self.sample,variable.replace('/','_'),self.j))
                if hist.InheritsFrom('RooDataSet'): return hist
                hist.SetDirectory(0)
                return hist
        if os.path.isfile(self.flat):
            infile = ROOT.TFile(self.flat,'read')
            hist = infile.Get(variable)
            if hist:
                self.j += 1
                hist = hist.Clone('h_{0}_{1}_{2}'.format(self.sample,variable.replace('/','_'),self.j))
                hist.SetDirectory(0)
                if hist.InheritsFrom('RooDataSet'): return hist
                return hist
            # attempt to project
            #hist = self.__projectChannel(variable,temp=True)
            #if hist:
            #    hist = hist.Clone('h_{0}_{1}'.format(self.sample,variable.replace('/','_')))
            #    hist.SetDirectory(0)
            #    return hist
        logging.debug('Histogram {0} not found for {1}'.format(variable,self.sample))
        return 0

    def __checkHash(self,name,directory,strings=[]):
        'Check the hash for a sample'''
        if self.temp: return False
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

    def __checkProjectionHash(self,name,directory,channel='',genchannel=''):
        '''Check hash of projection from histogram.'''
        return False
        if self.temp: return False
        self.infile = ROOT.TFile(self.flat,'read')
        self.outfile = ROOT.TFile(self.proj,'update')
        flatHashDirectory = 'hash/{0}'.format(directory)
        projHashDirectory = 'hash/{0}'.format('/'.join([x for x in [directory,channel,genchannel] if x]))
        flatHashObj = self.infile.Get('{0}/{1}'.format(flatHashDirectory,name))
        projHashObj = self.outfile.Get('{0}/{1}'.format(projHashDirectory,name))
        if not projHashObj:
            projHashObj = ROOT.TNamed(name,'')
        newHash = flatHashObj.GetTitle()
        oldHash = projHashObj.GetTitle()
        if oldHash==newHash:
            self.outfile.Close()
            return True
        else:
            projHashObj.SetTitle(newHash)
            if not self.outfile.GetDirectory(projHashDirectory): self.outfile.mkdir(projHashDirectory)
            self.outfile.cd('{0}:/{1}'.format(self.proj,projHashDirectory))
            projHashObj.Write('',ROOT.TObject.kOverwrite)
            self.outfile.Close()
            return False

    def __flatten(self,directory,histName,selection,params,**kwargs):
        '''Produce flat histograms for a given selection.'''
        # only flatten specified hists
        allowed = kwargs.pop('hists',[])
        if allowed and histName not in allowed: return False
        # clear old
        ROOT.gDirectory.Delete('h_*')
        ROOT.gDirectory.Delete(histName)
        # selections
        mccut = kwargs.pop('mccut','')
        datacut = kwargs.pop('datacut','')
        if datacut and isData(self.sample): selection += ' && {0}'.format(datacut)
        if mccut and not isData(self.sample): selection += ' && {0}'.format(mccut)
        if 'datacut' in params and isData(self.sample): selection += ' && {0}'.format(params['datacut'])
        if 'mccut' in params and not isData(self.sample): selection += ' && {0}'.format(params['mccut'])
        if 'selection' in params: selection += ' && {0}'.format(params['selection'])
        # scalefactor
        scalefactor = kwargs.pop('scalefactor','1')
        mcscalefactor = kwargs.pop('mcscalefactor','')
        datascalefactor = kwargs.pop('datascalefactor','')
        if datascalefactor and isData(self.sample): scalefactor = datascalefactor
        if mcscalefactor and not isData(self.sample): scalefactor = mcscalefactor
        if 'scale' in params: scalefactor += '*{0}'.format(params['scale'])
        if 'mcscale' in params and not isData(self.sample): scalefactor += '*{0}'.format(params['mcscale'])
        if 'datascale' in params and isData(self.sample): scalefactor += '*{0}'.format(params['datascale'])
        # check if we need to draw the hist, or if the one in the ntuple is the latest
        if 'zVariable' in params: # 3D
             hashExists = self.__checkHash(histName,directory,strings=[params['zVariable'],params['yVariable'],params['xVariable'],', '.join([str(x) for x in params['xBinning']+params['yBinning']+params['zBinning']]),scalefactor,selection])
        elif 'yVariable' in params: # 2D
             hashExists = self.__checkHash(histName,directory,strings=[params['yVariable'],params['xVariable'],', '.join([str(x) for x in params['xBinning']+params['yBinning']]),scalefactor,selection])
        else: # 1D
             hashExists = self.__checkHash(histName,directory,strings=[params['xVariable'],', '.join([str(x) for x in params['xBinning']]),scalefactor,selection])
        if hashExists:
            self.__finish()
            return False
        # get the histogram
        name = histName
        self.j += 1
        tempName = 'h_{0}_{1}_{2}'.format(name,self.sample,self.j)
        if 'zVariable' in params: # 3D
            hist = self.__getHist3D(tempName,selection,scalefactor,params['xVariable'],params['yVariable'],params['zVariable'],params['xBinning'],params['yBinning'],params['zBinning'])
        elif 'yVariable' in params: # 2D
            hist = self.__getHist2D(tempName,selection,scalefactor,params['xVariable'],params['yVariable'],params['xBinning'],params['yBinning'])
        else: # 1D
            hist = self.__getHist1D(tempName,selection,scalefactor,params['xVariable'],params['xBinning'])
        hist.SetTitle(name)
        hist.SetName(name)
        # save to file
        self.__write(hist,directory=directory)
        return True

    def __getHist1D(self,histName,selection,scalefactor,xVariable,xBinning):
        if not self.initialized: self.__initializeNtuple()
        if not isData(self.sample): scalefactor = '{0}*{1}'.format(scalefactor,float(self.intLumi)/self.sampleLumi) if self.sampleLumi else '0'
        binning = xBinning
        tree = self.sampleTree
        if not tree: 
            hist = ROOT.TH1D(histName,histName,*binning)
            return hist
        # TODO, make sure this is worth it
        #if self.entryListMap['1'].GetN()<1:
        #    hist = ROOT.TH1D(histName,histName,*binning)
        #    return hist
        #tree.SetEntryList(self.entryListMap['1'])
        #if selection not in self.entryListMap:
        #    self.j += 1
        #    listname = 'selList{0}'.format(self.j)
        #    tree.Draw('>>{0}'.format(listname),selection,'entrylist')
        #    skim = ROOT.gDirectory.Get(listname)
        #    self.entryListMap[selection] = skim
        #skim = self.entryListMap[selection]
        #if not skim or skim.GetN()==0:
        #    return ROOT.TH1D(histName,histName,*binning)
        #tree.SetEntryList(skim)
        drawString = '{0}>>{1}({2})'.format(xVariable,histName,', '.join([str(x) for x in binning]))
        selectionString = '{0}*({1})'.format(scalefactor,selection)
        #selectionString = '{0}*(1)'.format(scalefactor)
        logging.debug('drawString: {0}'.format(drawString))
        logging.debug('selectionString: {0}'.format(selectionString))
        tree.Draw(drawString,selectionString,'goff')
        #tree.SetEntryList(self.entryListMap['1'])
        if ROOT.gDirectory.Get(histName):
            hist = ROOT.gDirectory.Get(histName)
        elif self.useProof:
            out = self.proof.GetOutputList()
            hist = out.FindObject(histName)
        else:
            hist = ROOT.TH1D(histName,histName,*binning)
        return hist

    def __getHist2D(self,histName,selection,scalefactor,xVariable,yVariable,xBinning,yBinning):
        if not self.initialized: self.__initializeNtuple()
        if not isData(self.sample): scalefactor = '{0}*{1}'.format(scalefactor,float(self.intLumi)/self.sampleLumi) if self.sampleLumi else '0'
        binning = xBinning+yBinning
        tree = self.sampleTree
        if not tree:
            hist = ROOT.TH2D(histName,histName,*binning)
            return hist
        # TODO, make sure this is worth it
        #if self.entryListMap['1'].GetN()<1:
        #    hist = ROOT.TH2D(histName,histName,*binning)
        #    return hist
        #tree.SetEntryList(self.entryListMap['1'])
        #if selection not in self.entryListMap:
        #    self.j += 1
        #    listname = 'selList{0}'.format(self.j)
        #    tree.Draw('>>{0}'.format(listname),selection,'entrylist')
        #    skim = ROOT.gDirectory.Get(listname)
        #    self.entryListMap[selection] = skim
        #skim = self.entryListMap[selection]
        #if not skim or skim.GetN()==0:
        #    return ROOT.TH2D(histName,histName,*binning)
        #tree.SetEntryList(skim)
        drawString = '{0}:{1}>>{2}({3})'.format(yVariable,xVariable,histName,', '.join([str(x) for x in binning]))
        selectionString = '{0}*({1})'.format(scalefactor,selection)
        #selectionString = '{0}*(1)'.format(scalefactor)
        logging.debug('drawString: {0}'.format(drawString))
        logging.debug('selectionString: {0}'.format(selectionString))
        tree.Draw(drawString,selectionString,'goff')
        #tree.SetEntryList(self.entryListMap['1'])
        if ROOT.gDirectory.Get(histName):
            hist = ROOT.gDirectory.Get(histName)
        elif self.useProof:
            out = self.proof.GetOutputList()
            hist = out.FindObject(histName)
        else:
            hist = ROOT.TH2D(histName,histName,*binning)
        return hist

    def __getHist3D(self,histName,selection,scalefactor,xVariable,yVariable,zVariable,xBinning,yBinning,zBinning):
        if not self.initialized: self.__initializeNtuple()
        if not isData(self.sample): scalefactor = '{0}*{1}'.format(scalefactor,float(self.intLumi)/self.sampleLumi) if self.sampleLumi else '0'
        binning = xBinning+yBinning+zBinning
        tree = self.sampleTree
        if not tree:
            hist = ROOT.TH3D(histName,histName,*binning)
            return hist
        # TODO, make sure this is worth it
        #if self.entryListMap['1'].GetN()<1:
        #    hist = ROOT.TH3D(histName,histName,*binning)
        #    return hist
        #tree.SetEntryList(self.entryListMap['1'])
        #if selection not in self.entryListMap:
        #    self.j += 1
        #    listname = 'selList{0}'.format(self.j)
        #    tree.Draw('>>{0}'.format(listname),selection,'entrylist')
        #    skim = ROOT.gDirectory.Get(listname)
        #    self.entryListMap[selection] = skim
        #skim = self.entryListMap[selection]
        #if not skim or skim.GetN()==0:
        #    return ROOT.TH3D(histName,histName,*binning)
        #tree.SetEntryList(skim)
        drawString = '{0}:{1}:{2}>>{3}({4})'.format(zVariable,yVariable,xVariable,histName,', '.join([str(x) for x in binning]))
        selectionString = '{0}*({1})'.format(scalefactor,selection)
        #selectionString = '{0}*(1)'.format(scalefactor)
        logging.debug('drawString: {0}'.format(drawString))
        logging.debug('selectionString: {0}'.format(selectionString))
        tree.Draw(drawString,selectionString,'goff')
        #tree.SetEntryList(self.entryListMap['1'])
        if ROOT.gDirectory.Get(histName):
            hist = ROOT.gDirectory.Get(histName)
        elif self.useProof:
            out = self.proof.GetOutputList()
            hist = out.FindObject(histName)
        else:
            hist = ROOT.TH3D(histName,histName,*binning)
        return hist

    def __project(self,histName,directory,hist2d,direction,binLabels=[],binRange=[0,-1],temp=False):
        '''Project a 2D histogram onto a 1D histogram.'''
        hists = ROOT.TList()
        if direction=='x':
            binning = [
                hist2d.GetXaxis().GetNbins(),
                hist2d.GetXaxis().GetXmin(),
                hist2d.GetXaxis().GetXmax(),
            ]
        else:
            binning = [
                hist2d.GetYaxis().GetNbins(),
                hist2d.GetYaxis().GetXmin(),
                hist2d.GetYaxis().GetXmax(),
            ]
        if binLabels:
            for label in binLabels:
                self.j += 1
                name = 'h_{0}_{1}_{2}'.format(histName,label,self.j)
                if direction=='x':
                    binNum = hist2d.GetYaxis().FindBin(label)
                    hist2d.ProjectionX(name,binNum,binNum,'e')
                else:
                    binNum = hist2d.GetXaxis().FindBin(label)
                    hist2d.ProjectionY(name,binNum,binNum,'e')
                if ROOT.gDirectory.Get(name):
                    hist = ROOT.gDirectory.Get(name)
                    if hist: hists.Add(hist)
        else:
            self.j += 1
            name = 'h_{0}_{1}'.format(histName,self.j)
            if direction=='x':
                hist2d.ProjectionX(name,binRange[0],binRange[1],'e')
            else:
                hist2d.ProjectionY(name,binRange[0],binRange[1],'e')
            if ROOT.gDirectory.Get(name):
                hist = ROOT.gDirectory.Get(name)
                hists.Add(hist)
        if hists.IsEmpty():
            hist = ROOT.TH1D(histName,histName,*binning)
        else:
            self.j += 1
            hist = hists[0].Clone('h_temp_{0}_{1}'.format(histName,self.j))
            hist.Reset()
            hist.Merge(hists)
            hist.SetName(histName)
            hist.SetTitle(histName)
        if not temp: self.__writeProjection(hist,directory=directory)
        return hist

    def __projectFrom3D(self,histName,directory,hist3d,direction,binLabels1=[],binLabels2=[],binRange1=[0,-1],binRange2=[0,-1],temp=False):
        '''Project a 3D histogram onto a 1D histogram.'''
        hists = ROOT.TList()
        if direction=='x':
            binning = [
                hist3d.GetXaxis().GetNbins(),
                hist3d.GetXaxis().GetXmin(),
                hist3d.GetXaxis().GetXmax(),
            ]
        elif direction=='y':
            binning = [
                hist3d.GetYaxis().GetNbins(),
                hist3d.GetYaxis().GetXmin(),
                hist3d.GetYaxis().GetXmax(),
            ]
        else:
            binning = [
                hist3d.GetZaxis().GetNbins(),
                hist3d.GetZaxis().GetXmin(),
                hist3d.GetZaxis().GetXmax(),
            ]
        if binLabels1 and binLabels2:
            for label1 in binLabels1:
                for label2 in binLabels2:
                    self.j += 1
                    name = 'h_{0}_{1}_{2}_{3}'.format(histName,label1,label2,self.j)
                    if direction=='x':
                        binNum1 = hist3d.GetYaxis().FindBin(label1)
                        binNum2 = hist3d.GetZaxis().FindBin(label2)
                        hist3d.ProjectionX(name,binNum1,binNum1,binNum2,binNum2,'e')
                    elif direction=='y':
                        binNum1 = hist3d.GetXaxis().FindBin(label1)
                        binNum2 = hist3d.GetZaxis().FindBin(label2)
                        hist3d.ProjectionY(name,binNum1,binNum1,binNum2,binNum2,'e')
                    else:
                        binNum1 = hist3d.GetXaxis().FindBin(label1)
                        binNum2 = hist3d.GetYaxis().FindBin(label2)
                        hist3d.ProjectionZ(name,binNum1,binNum1,binNum2,binNum2,'e')
                    if ROOT.gDirectory.Get(name):
                        hist = ROOT.gDirectory.Get(name)
                        if hist: hists.Add(hist)
        elif binLabels1 and not binLabels2:
            for label1 in binLabels1:
                self.j += 1
                name = 'h_{0}_{1}_{2}'.format(histName,label1,self.j)
                if direction=='x':
                    binNum1 = hist3d.GetYaxis().FindBin(label1)
                    hist3d.ProjectionX(name,binNum1,binNum1,binRange2[0],binRange2[1],'e')
                elif direction=='y':
                    binNum1 = hist3d.GetXaxis().FindBin(label1)
                    hist3d.ProjectionY(name,binNum1,binNum1,binRange2[0],binRange2[1],'e')
                else:
                    binNum1 = hist3d.GetXaxis().FindBin(label1)
                    hist3d.ProjectionZ(name,binNum1,binNum1,binRange2[0],binRange2[1],'e')
                if ROOT.gDirectory.Get(name):
                    hist = ROOT.gDirectory.Get(name)
                    if hist: hists.Add(hist)
        elif not binLabels1 and binLabels2:
            for label2 in binLabels2:
                self.j += 1
                name = 'h_{0}_{1}_{2}'.format(histName,label2,self.j)
                if direction=='x':
                    binNum2 = hist3d.GetZaxis().FindBin(label2)
                    hist3d.ProjectionX(name,binRange1[0],bingRange1[1],binNum2,binNum2,'e')
                elif direction=='y':
                    binNum2 = hist3d.GetZaxis().FindBin(label2)
                    hist3d.ProjectionY(name,binRange1[0],bingRange1[1],binNum2,binNum2,'e')
                else:
                    binNum2 = hist3d.GetYaxis().FindBin(label2)
                    hist3d.ProjectionZ(name,binRange1[0],bingRange1[1],binNum2,binNum2,'e')
                if ROOT.gDirectory.Get(name):
                    hist = ROOT.gDirectory.Get(name)
                    if hist: hists.Add(hist)
        else:
            self.j += 1
            name = 'h_{0}_{1}'.format(histName,self.j)
            if direction=='x':
                hist3d.ProjectionX(name,binRange1[0],binRange1[1],binRange2[0],binRange2[1],'e')
            elif direction=='y':
                hist3d.ProjectionY(name,binRange1[0],binRange1[1],binRange2[0],binRange2[1],'e')
            else:
                hist3d.ProjectionZ(name,binRange1[0],binRange1[1],binRange2[0],binRange2[1],'e')
            if ROOT.gDirectory.Get(name):
                hist = ROOT.gDirectory.Get(name)
                hists.Add(hist)
        if hists.IsEmpty():
            hist = ROOT.TH1D(histName,histName,*binning)
        else:
            self.j += 1
            hist = hists[0].Clone('h_temp_{0}_{1}'.format(histName,self.j))
            hist.Reset()
            hist.Merge(hists)
            hist.SetName(histName)
            hist.SetTitle(histName)
        if not temp: self.__writeProjection(hist,directory=directory)
        return hist

    def __projectChannel(self,variable,temp=False):
        '''Project down the 2D channels plot to the desired channels.'''
        components = variable.split('/')
        histName = components[-1]
        if len(components)>2 and components[-2] in self.projections and components[-3] in self.projections: # explicit channel/genchannel
            selectionName = '/'.join(components[:-3])
            genchannel = components[-2]
            channel = components[-3]
        elif len(components)>1 and components[-2] in self.projections: # explicit channel
            selectionName = '/'.join(components[:-2])
            genchannel = ''
            channel = components[-2]
        else: # all
            selectionName = '/'.join(components[:-1])
            genchannel = ''
            channel = 'all'
        if histName not in self.histParams:
            logging.error('Unrecognized histogram {0}'.format(histName))
            return 0
        if selectionName not in self.selections:
            logging.error('Unrecognized selection {0}'.format(selectionName))
            return 0
        # check if we need to project
        #passHash = self.__checkProjectionHash(histName,selectionName,channel=channel,genchannel=genchannel)
        #if passHash: return 0
        # not project
        histNameND = '/'.join([selectionName,histName])
        histNd = self.__read(histNameND)
        if histNd and histNd.InheritsFrom('TH3'):
            if genchannel:
                directory = '/'.join([selectionName,channel,genchannel])
                hist = self.__projectFrom3D(histName,directory,histNd,'x',binLabels1=self.projections[channel],binLabels2=self.projections[genchannel],temp=temp)
            else:
                directory = '/'.join([selectionName,channel])
                hist = self.__projectFrom3D(histName,directory,histNd,'x',binLabels1=self.projections[channel],temp=temp)
        elif histNd and histNd.InheritsFrom('TH2'):
            directory = '/'.join([selectionName,channel])
            hist = self.__project(histName,directory,histNd,'x',binLabels=self.projections[channel],temp=temp)
        elif histNd and histNd.InheritsFrom('TH1'): # its a 1d histogram
            hist = histNd
        else: # not a hist
            hist = 0
        return hist

    def __readSkim(self,directory,full=False):
        '''Read a value from the skim file.'''
        if not os.path.isfile(self.pickle): return
        if not self.skimInitialized:
            with open(self.pickle,'rb') as f:
                self.skim = pickle.load(f)
            self.skimInitialized = True
        components = directory.split('/')
        if components[-1] == 'all': components = components[:-1]
        # first try finding
        key = '/'.join(components)
        if key in self.skim:
            if full:
                return self.skim[key]['val'], self.skim[key]['err2']**0.5, self.skim[key]['count']
            else:
                return self.skim[key]['val'], self.skim[key]['err2']**0.5
        #logging.warning('Unrecognized selection {0}'.format(directory))
        if full:
            return 0.,0.,0
        else:
            return 0.,0.

    def getHist2D(self,variable):
        '''Get a histogram'''
        hist = self.__read(variable)
        return hist

    def getHist(self,variable):
        '''Get a histogram'''
        hist = self.__read(variable)
        if hist and hist.InheritsFrom('TH3'): # 3D, project down on x
            return self.__projectChannel(variable)
        elif hist and hist.InheritsFrom('TH2'): # 2D, project down on x
            return self.__projectChannel(variable)
        else:
            return hist

    def getDataset(self,variable,weight='w',selection='1',xRange=[],yRange=[],project=''):
        '''Get a RooDataSet'''
        ds = self.__read(variable)
        # recreate ds with weights
        args = ds.get()
        if xRange: args.find('x').setRange(*xRange)
        if yRange: args.find('y').setRange(*yRange)
        ds = ROOT.RooDataSet(ds.GetName(),ds.GetTitle(),ds,args,selection,weight)
        if project: ds = getattr(ds,'reduce')(ROOT.RooArgSet(ds.get().find(project)))
        return ds

    def getCount(self,directory,full=False):
        '''Get a count'''
        count = self.__readSkim(directory,full=False)
        if count is not None: return count
        return self.__read('{0}/count'.format(directory))

    def getTempHist(self,histName,selection,scalefactor,variable,binning):
        '''Get a histogram that is not saved in flat ntuple.'''
        self.j += 1
        tempname = '{0}_{1}_{2}_{3}'.format(histName,self.analysis,self.sample,self.j)
        return self.__getHist1D(tempname,selection,scalefactor,variable,binning)

    def getTempHist2D(self,histName,selection,scalefactor,xVariable,yVariable,xBinning,yBinning):
        '''Get a histogram that is not saved in flat ntuple.'''
        self.j += 1
        tempname = '{0}_{1}_{2}_{3}'.format(histName,self.analysis,self.sample,self.j)
        return self.__getHist2D(tempname,selection,scalefactor,xVariable,yVariable,xBinning,yBinning)

    def getTempCount(self,selection,scalefactor):
        '''Get a histogram that is a single bin of counts with statistical error'''
        self.j += 1
        tempname = 'count_{0}_{1}_{2}'.format(self.analysis,self.sample,self.j)
        hist = self.__getHist1D(tempname,selection,scalefactor,'1',[1,0,2])
        hist.SetTitle('count')
        return hist

    def flatten(self,histName,selectionName):
        '''Flatten a histogram'''
        self.temp = False
        if histName not in self.histParams:
            logging.error('Unrecognized histogram {0}'.format(histName))
        params = self.histParams[histName]
        if not params: return
        if selectionName not in self.selections:
            logging.error('Unrecognized selection {0}'.format(selectionName))
        selection = self.selections[selectionName]['args'][0]
        kwargs = self.selections[selectionName]['kwargs']
        updated = self.__flatten(selectionName,histName,selection,params,**kwargs)
        # project stuff
        if updated and len(self.projections.keys())>1: # if it changed and there are channels to project
            variable = '/'.join([selectionName,histName])
            self.__projectChannel(variable)
            chans = [x for x in self.projections.keys() if 'gen' not in x]
            genchans = [x for x in self.projections.keys() if 'gen' in x]
            genchans = [] # block genchans unless i really want it
            for chan in chans:
                variable = '/'.join([selectionName,chan,histName])
                self.__projectChannel(variable)
                for genchan in genchans:
                    variable = '/'.join([selectionName,chan,genchan,histName])
                    self.__projectChannel(variable)
            for genchan in genchans:
                variable = '/'.join([selectionName,genchan,histName])
            self.__projectChannel(variable)
        self.temp = True

