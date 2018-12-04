import ROOT

ROOT.gROOT.SetBatch(True)

import DevTools.Plotter.CMS_lumi as CMS_lumi
import DevTools.Plotter.tdrstyle as tdrstyle

tdrstyle.setTDRStyle()

fname = '/hdfs/store/user/dntaylor/2018-12-03_MuMuTauTauModAnalysis_80X_trigOnly_v1-merge/SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-125_M-10_TuneCUETP8M1_13TeV_madgraph_pythia8/mergeFilesJob-6469ccfc28b533b3454263168831a4b9.root'
fnameMC = '/hdfs/store/user/dntaylor/2018-12-03_MuMuTauTauModAnalysis_80X_trigOnlyMC_v1-merge/SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-125_M-10_TuneCUETP8M1_13TeV_madgraph_pythia8/mergeFilesJob-7c7158e8f2fc80b7fd98aa8ffa5a36f0.root'

tfile = ROOT.TFile.Open(fname)
tfileMC = ROOT.TFile.Open(fnameMC)

tree = tfile.Get('MuMuTauTauModTree')
treeMC = tfileMC.Get('MuMuTauTauModTree')

j = 0

def getHist(tree,selection,scalefactor,variable,binning):
    global j
    j += 1
    histname = 'h{}'.format(j)
    drawString = '{0}>>{1}({2})'.format(variable,histname,', '.join([str(x) for x in binning]))
    selectionString = '{0}*({1})'.format(scalefactor,selection)
    tree.Draw(drawString,selectionString,'goff')
    hist = ROOT.gDirectory.Get(histname)
    return hist

denomSel = 'amm_mass>1 && amm_mass<30 && am1_pt>26 && am1_isLooseMuon && am1_isolation<0.25 && am2_pt>3 && am2_isLooseMuon && am2_isolation<0.25 && atm_pt>3 && ath_pt>10'
numSel = '{} && atm_isLooseMuon && ath_byMediumIsolationMVArun2v1DBoldDMwLT'.format(denomSel)


plots = {
    'athPt'     : {'variable': 'ath_pt',     'binning': [8,10,50], 'label': 'p^{#tau_{h}}_{T} (GeV)',},
    'attDeltaR' : {'variable': 'att_deltaR', 'binning': [8,0,0.8], 'label': '#DeltaR(#tau_{#mu}#tau_{h})',},
}

for plot in plots:

    denom   = getHist(tree,  denomSel,'1',plots[plot]['variable'],plots[plot]['binning'])
    num     = getHist(tree,  numSel,  '1',plots[plot]['variable'],plots[plot]['binning'])
    denomMC = getHist(treeMC,denomSel,'1',plots[plot]['variable'],plots[plot]['binning'])
    numMC   = getHist(treeMC,numSel,  '1',plots[plot]['variable'],plots[plot]['binning'])
    
    eff = num.Clone('eff')
    effMC = numMC.Clone('effMC')
    
    eff.Divide(denom)
    effMC.Divide(denomMC)
    
    eff.SetLineColor(ROOT.kBlack)
    eff.SetLineStyle(7)
    eff.SetLineWidth(2)
    eff.SetTitle('HPS')
    
    effMC.SetLineColor(ROOT.kBlack)
    effMC.SetLineStyle(1)
    effMC.SetLineWidth(2)
    effMC.SetTitle('Muon Cleaned HPS')
    
    canvas = ROOT.TCanvas('c','c',600,600)
    
    eff.Draw('hist')
    eff.GetYaxis().SetRangeUser(0.2,1.3)
    eff.GetXaxis().SetTitle(plots[plot]['label'])
    eff.GetYaxis().SetTitle('#tau_{h} identification efficiency')
    
    effMC.Draw('hist same')
    
    legend = ROOT.TLegend(0.3,0.2,0.85,0.3,'','NDC')
    legend.SetNColumns(2)
    legend.AddEntry(effMC,effMC.GetTitle(),'l')
    legend.AddEntry(eff,eff.GetTitle(),'l')
    legend.SetTextFont(42)
    legend.SetBorderSize(0)
    legend.SetFillColor(0)
    
    legend.Draw()
    
    CMS_lumi.cmsText = 'CMS'
    CMS_lumi.writeExtraText = True
    CMS_lumi.extraText = "Simulation Preliminary"
    CMS_lumi.lumi_13TeV = ''
    CMS_lumi.CMS_lumi(canvas,4,11)
    
    canvas.Print('hpsEff_{}.png'.format(plot))
    canvas.Print('hpsEff_{}.pdf'.format(plot))
    
