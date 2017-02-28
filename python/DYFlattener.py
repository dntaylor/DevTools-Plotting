#!/usr/bin/env python
import argparse
import logging
import sys
import sys
import itertools
import operator

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from NtupleFlattener import NtupleFlattener
from DevTools.Utilities.utilities import prod, ZMASS


logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class DYFlattener(NtupleFlattener):
    '''
    DY flattener
    '''

    def __init__(self,sample,**kwargs):
        # setup properties
        self.leps = ['z1','z2']
        self.channels = ['ee','mm']
        self.selections = {
            'default': lambda row: row.z_deltaR>0.02 and row.z_mass>60. and row.z1_pt>25. and row.z2_pt>20.,
        }

        # setup histogram parameters
        self.histParams = {
            'count'                       : {'x': lambda row: 1,                  'xBinning': [1,0,2],                 }, # just a count of events passing selection
            'numVertices'                 : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],               },
            'numVertices_noreweight'      : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: 1./row.pileupWeight},
            'numVertices_60000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_60000/row.pileupWeight},
            'numVertices_61000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_61000/row.pileupWeight},
            'numVertices_62000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_62000/row.pileupWeight},
            'numVertices_63000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_63000/row.pileupWeight},
            'numVertices_64000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_64000/row.pileupWeight},
            'numVertices_65000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_65000/row.pileupWeight},
            'numVertices_66000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_66000/row.pileupWeight},
            'numVertices_67000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_67000/row.pileupWeight},
            'numVertices_68000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_68000/row.pileupWeight},
            'numVertices_69000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_69000/row.pileupWeight},
            'numVertices_70000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_70000/row.pileupWeight},
            'numVertices_71000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_71000/row.pileupWeight},
            'numVertices_72000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_72000/row.pileupWeight},
            'numVertices_73000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_73000/row.pileupWeight},
            'numVertices_74000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_74000/row.pileupWeight},
            'numVertices_75000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_75000/row.pileupWeight},
            'numVertices_76000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_76000/row.pileupWeight},
            'numVertices_77000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_77000/row.pileupWeight},
            'numVertices_78000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_78000/row.pileupWeight},
            'numVertices_79000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_79000/row.pileupWeight},
            'numVertices_80000'           : {'x': lambda row: row.numVertices,    'xBinning': [40,0,40],                'mcscale': lambda row: row.pileupWeight_80000/row.pileupWeight},
            'rho'                         : {'x': lambda row: row.rho,            'xBinning': [50,0,50],               },
            'rho_noreweight'              : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: 1./row.pileupWeight},
            'rho_60000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_60000/row.pileupWeight},
            'rho_61000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_61000/row.pileupWeight},
            'rho_62000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_62000/row.pileupWeight},
            'rho_63000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_63000/row.pileupWeight},
            'rho_64000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_64000/row.pileupWeight},
            'rho_65000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_65000/row.pileupWeight},
            'rho_66000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_66000/row.pileupWeight},
            'rho_67000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_67000/row.pileupWeight},
            'rho_68000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_68000/row.pileupWeight},
            'rho_69000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_69000/row.pileupWeight},
            'rho_70000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_70000/row.pileupWeight},
            'rho_71000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_71000/row.pileupWeight},
            'rho_72000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_72000/row.pileupWeight},
            'rho_73000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_73000/row.pileupWeight},
            'rho_74000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_74000/row.pileupWeight},
            'rho_75000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_75000/row.pileupWeight},
            'rho_76000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_76000/row.pileupWeight},
            'rho_77000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_77000/row.pileupWeight},
            'rho_78000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_78000/row.pileupWeight},
            'rho_79000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_79000/row.pileupWeight},
            'rho_80000'                   : {'x': lambda row: row.rho,            'xBinning': [50,0,50],                'mcscale': lambda row: row.pileupWeight_80000/row.pileupWeight},
            'met'                         : {'x': lambda row: row.met_pt,         'xBinning': [500, 0, 500],           },
            'metPhi'                      : {'x': lambda row: row.met_phi,        'xBinning': [500, -3.14159, 3.14159],},
            'zMass'                       : {'x': lambda row: row.z_mass,         'xBinning': [5000, 0, 500],          },
            'zPt'                         : {'x': lambda row: row.z_pt,           'xBinning': [5000, 0, 500],          },
            'zDeltaR'                     : {'x': lambda row: row.z_deltaR,       'xBinning': [500, 0, 5],             },
            'zLeadingLeptonPt'            : {'x': lambda row: row.z1_pt,          'xBinning': [10000, 0, 1000],        },
            'zLeadingLeptonEta'           : {'x': lambda row: row.z1_eta,         'xBinning': [500, -2.5, 2.5],        },
            'zLeadingLeptonIso'           : {'x': lambda row: row.z1_isolation,   'xBinning': [500, 0, 0.5],           },
            'zSubLeadingLeptonPt'         : {'x': lambda row: row.z2_pt,          'xBinning': [10000, 0, 1000],        },
            'zSubLeadingLeptonEta'        : {'x': lambda row: row.z2_eta,         'xBinning': [500, -2.5, 2.5],        },
            'zSubLeadingLeptonIso'        : {'x': lambda row: row.z2_isolation,   'xBinning': [500, 0, 0.5],           },
            'nJets'                       : {'x': lambda row: row.numJetsTight30, 'xBinning': [11, -0.5, 10.5],        },
        }

        # initialize flattener
        super(DYFlattener, self).__init__('DY',sample,**kwargs)


    def getWeight(self,row):
        if row.isData:
            weight = 1.
        else:
            cut = 'medium'
            # per event weights
            base = ['genWeight','pileupWeight','triggerEfficiency']
            if self.shift=='trigUp': base = ['genWeight','pileupWeight','triggerEfficiencyUp']
            if self.shift=='trigDown': base = ['genWeight','pileupWeight','triggerEfficiencyDown']
            if self.shift=='puUp': base = ['genWeight','pileupWeightUp','triggerEfficiency']
            if self.shift=='puDown': base = ['genWeight','pileupWeightDown','triggerEfficiency']
            for lep in zip(self.leps):
                if self.shift == 'lepUp':
                    base += ['{0}_{1}ScaleUp'.format(lep,cut)]
                elif self.shift == 'lepDown':
                    base += ['{0}_{1}ScaleDown'.format(lep,cut)]
                else:
                    base += ['{0}_{1}Scale'.format(lep,cut)]
            vals = [getattr(row,scale) for scale in base]
            for scale,val in zip(base,vals):
                if val != val: logging.warning('{0}: {1} is NaN'.format(row.channel,scale))
            weight = prod([val for val in vals if val==val])
            # scale to lumi/xsec
            weight *= float(self.intLumi)/self.sampleLumi if self.sampleLumi else 0.
            if hasattr(row,'qqZZkfactor'): weight *= row.qqZZkfactor/1.1 # ZZ variable k factor

        return weight

    def perRowAction(self,row):
        isData = row.isData

        ## per sample cuts
        #keep = True
        #if self.sample=='DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'  : keep = row.numGenJets==0 or row.numGenJets>4
        #if self.sample=='DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==1
        #if self.sample=='DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==2
        #if self.sample=='DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==3
        #if self.sample=='DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==4
        #if self.sample=='WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'       : keep = row.numGenJets==0 or row.numGenJets>4
        #if self.sample=='W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : keep = row.numGenJets==1
        #if self.sample=='W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : keep = row.numGenJets==2
        #if self.sample=='W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : keep = row.numGenJets==3
        #if self.sample=='W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : keep = row.numGenJets==4
        #if not keep: return

        # setup channels
        passMedium = [getattr(row,'{0}_passMedium'.format(lep)) for lep in self.leps]
        if not all(passMedium): return
        recoChan = ''.join([x for x in row.channel if x in 'emt'])

        # define weights
        w = self.getWeight(row)

        # define plot regions
        for selection in self.selections:
            result = self.selections[selection](row)
            if result:
                self.fill(row,selection,w,recoChan)




def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run Flattener')

    parser.add_argument('sample', type=str, default='DoubleMuon', nargs='?', help='Sample to flatten')
    parser.add_argument('shift', type=str, default='', nargs='?', help='Shift to apply to scale factors')

    return parser.parse_args(argv)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    flattener = DYFlattener(
        args.sample,
        shift=args.shift,
    )

    flattener.flatten()

    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)

