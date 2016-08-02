import logging
import os
import sys
import math

sys.argv.append('-b')
import ROOT
sys.argv.pop()

ROOT.gROOT.SetBatch(ROOT.kTRUE)

from DevTools.Plotter.NtupleWrapper import NtupleWrapper

try:
    from progressbar import ProgressBar, ETA, Percentage, Bar, SimpleProgress
    hasProgress = True
except:
    hasProgress = False

class FlattenTree(object):
    '''Produces flat histograms'''

    def __init__(self,analysis,sample,**kwargs):
        self.analysis = analysis
        self.sample = sample
        self.ntuple = NtupleWrapper(analysis,sample,**kwargs)
        self.histParameters = []
        self.selections = []
        self.countOnly = []

    def __exit__(self, type, value, traceback):
        self.__finish()

    def __del__(self):
        self.__finish()

    def __finish(self):
        pass

    def addHistogram(self,name,**kwargs):
        '''
        Add a histogram to flatten
        '''
        self.histParameters += [name]

    def addSelection(self,selection,**kwargs):
        '''Add selection and postfix name to flatten'''
        countOnly = kwargs.pop('countOnly',False)
        self.selections += [selection]
        if countOnly:
            self.countOnly += [selection]

    def clear(self):
        '''Reset the histograms/selections'''
        self.histParameters = []
        self.selections = []
        self.countOnly = []

    def flattenAll(self,**kwargs):
        '''Flatten all selections'''
        njobs = int(kwargs.pop('njobs',1))
        job = int(kwargs.pop('job',0))
        if hasProgress:
            pbar = kwargs.pop('progressbar',ProgressBar(widgets=['{0}: '.format(self.sample),' ',SimpleProgress(),' histograms ',Percentage(),' ',Bar(),' ',ETA()]))
        else:
            pbar = None
        # setup all jobs
        allJobs = []
        for selName in self.selections:
            for histName in self.histParameters:
                if selName in self.countOnly and 'count' not in histName: continue
                allJobs += [[histName,selName]]
        # split into multiple jobs
        totjobs = len(allJobs)
        nperjob = math.ceil(float(totjobs)/njobs)
        startjob = int(job*nperjob)
        endjob = int((job+1)*nperjob)
        allJobs = sorted(allJobs)[startjob:endjob]
        # flatten
        if hasProgress:
            for args in pbar(allJobs):
                self.ntuple.flatten(*args)
        else:
            n = len(allJobs)
            for i,args in enumerate(allJobs):
                logging.info('Processing {3} {4} plot {0} of {1}: {2}.'.format(i+1,n,' '.join(args),self.analysis,self.sample))
                self.ntuple.flatten(*args)
