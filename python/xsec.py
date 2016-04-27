import logging

PB = 1.
pb = PB
FB = 1.e-3
fb = FB

xsecs = {
    'DoubleMuon'                                                       : 1.,
    'DoubleEG'                                                         : 1.,
    'MuonEG'                                                           : 1.,
    'SingleMuon'                                                       : 1.,
    'SingleElectron'                                                   : 1.,
    'Tau'                                                              : 1.,

    'QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8'                  : 1.,
    'QCD_Pt-20toInf_MuEnrichedPt15_TuneCUETP8M1_13TeV_pythia8'         : 720648000 * PB,

    'QCD_Pt_5to10_TuneCUETP8M1_13TeV_pythia8'                          : 61018300000           * PB,
    'QCD_Pt_10to15_TuneCUETP8M1_13TeV_pythia8'                         :  5887580000           * PB,
    'QCD_Pt_15to30_TuneCUETP8M1_13TeV_pythia8'                         :  1837410000           * PB,
    'QCD_Pt_30to50_TuneCUETP8M1_13TeV_pythia8'                         :   140932000           * PB,
    'QCD_Pt_50to80_TuneCUETP8M1_13TeV_pythia8'                         :    19204300           * PB,
    'QCD_Pt_80to120_TuneCUETP8M1_13TeV_pythia8'                        :     2762530           * PB,
    'QCD_Pt_120to170_TuneCUETP8M1_13TeV_pythia8'                       :      471100           * PB,
    'QCD_Pt_170to300_TuneCUETP8M1_13TeV_pythia8'                       :      117276           * PB,
    'QCD_Pt_300to470_TuneCUETP8M1_13TeV_pythia8'                       :        7823           * PB,
    'QCD_Pt_470to600_TuneCUETP8M1_13TeV_pythia8'                       :         648.2         * PB,
    'QCD_Pt_600to800_TuneCUETP8M1_13TeV_pythia8'                       :         186.9         * PB,
    'QCD_Pt_800to1000_TuneCUETP8M1_13TeV_pythia8'                      :          32.293       * PB,
    'QCD_Pt_1000to1400_TuneCUETP8M1_13TeV_pythia8'                     :           9.4183      * PB,
    'QCD_Pt_1400to1800_TuneCUETP8M1_13TeV_pythia8'                     :           0.84265     * PB,
    'QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8'                     :           0.114943    * PB,
    'QCD_Pt_2400to3200_TuneCUETP8M1_13TeV_pythia8'                     :           0.00682981  * PB,
    'QCD_Pt_3200toInf_TuneCUETP8M1_13TeV_pythia8'                      :           0.000165445 * PB,

    'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'      :  18610.       * PB, # already NNLO
    'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'          :   6025.2      * PB,

    'DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'     :    421.5      * PB * 1.216, # 1.216 LO -> NNLO for DY
    'DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'     :    184.3      * PB * 1.216,
    'DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          :   1016.       * PB * 1.216,
    'DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          :    331.4      * PB * 1.216,
    'DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          :     96.36     * PB * 1.216,
    'DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          :     51.4      * PB * 1.216,

    'ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1'                    :   3.36 * PB,
    'ST_t-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1'                    : 216.99 * PB,
    'ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1' :  80.95 * PB,
    'ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1'              :  26.38 * PB,
    'ST_t-channel_top_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1'                  :  44.33 * PB,
    'ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1'                  :  35.6  * PB,
    'ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1'                      :  35.6  * PB,

    'TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'                   :    831.76     * PB,
    'TTTo2L2Nu_13TeV-powheg'                                           :     87.31     * PB,
    'TT_TuneCUETP8M1_13TeV-powheg-pythia8'                             :    831.76     * PB,
    'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'             :     57.35     * PB,
    'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'    :    114.5      * PB,
    'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' :    114.6      * PB,

    'TTZToLLNuNu_M-10_TuneCUETP8M1_13TeV-amcatnlo-pythia8'             :      0.2529   * PB,
    'TTZToQQ_TuneCUETP8M1_13TeV-amcatnlo-pythia8'                      :      0.5297   * PB,
    'TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8'     :      0.2043   * PB,
    'TTWJetsToQQ_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8'      :      0.4062   * PB,
    'ttZJets_13TeV_madgraphMLM'                                        :      0.259    * PB,
    'ttWJets_13TeV_madgraphMLM'                                        :      0.243    * PB,
    'ttH_M125_13TeV_powheg_pythia8'                                    :      0.5085   * PB,

    'tZq_ll_4f_13TeV-amcatnlo-pythia8_TuneCUETP8M1'                    :      0.0758   * PB,
    'tZq_nunu_4f_13TeV-amcatnlo-pythia8_TuneCUETP8M1'                  :      0.1379   * PB,

    'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'               :  61526.7      * PB,

    'ZGTo2LG_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'                  :    117.864    * PB,
    'WGToLNuG_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'                 :    489.       * PB,

    # https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageAt1314TeV2014
    # https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageBR
    # PDG
    'WH_HToBB_WToLNu_M125_13TeV_amcatnloFXFX_madspin_pythia8'          :      1.380  * 0.5824 * (0.108*3)    * PB, # WH * H->bb * W->lnu
    'ZH_HToBB_ZToLL_M125_13TeV_amcatnloFXFX_madspin_pythia8'           :      0.8696 * 0.5824 * (0.033658*3) * PB, # ZH * H->bb * Z->ll
    'ZH_HToBB_ZToNuNu_M125_13TeV_amcatnloFXFX_madspin_pythia8'         :      0.8696 * 0.5824 * 0.2          * PB, # ZH * H->bb * Z->inv
    'ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8'                         :      0.8696 * 0.5824 * 0.6991       * PB, # ZH * H->bb * Z->had
    'ZH_HToGG_ZToAll_M125_13TeV_powheg_pythia8'                        :      0.8696 * 0.00227               * PB, # ZH * H->gamgam
    'ZH_HToZG_ZToAll_M-125_13TeV_powheg_pythia8'                       :      0.8696 * 0.001533              * PB, # ZH * H->Zgam
    'ZH_HToZZ_4LFilter_M125_13TeV_powheg2-minlo-HZJ_JHUgenV6_pythia8'  :      0.147 * PB, # MCM , 0.8696 * 0.02619 * (0.033658*3)**2 # ZH * H->ZZ * Z->ll^2 

    'WWTo2L2Nu_13TeV-powheg'                                           :     10.481    * PB,
    'WWTo4Q_13TeV-powheg'                                              :     45.20     * PB,
    'WWToLNuQQ_13TeV-powheg'                                           :     43.53     * PB,
    'WW_TuneCUETP8M1_13TeV-pythia8'                                    :     63.21     * PB,

    'WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8'                   :     10.71     * PB,
    'WZTo1L3Nu_13TeV_amcatnloFXFX_madspin_pythia8'                     :      3.05     * PB,
    'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8'                      :      5.60     * PB,
    'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8'                       :      4.42965  * PB,
    'WZJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'                   :      5.29     * PB,
    'WZ_TuneCUETP8M1_13TeV-pythia8'                                    :     47.13     * PB,

    'ZZTo4Q_13TeV_amcatnloFXFX_madspin_pythia8'                        :      6.842    * PB,
    'ZZTo2Q2Nu_13TeV_amcatnloFXFX_madspin_pythia8'                     :      4.04     * PB,
    'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8'                      :      3.28     * PB,
    'ZZTo2L2Nu_13TeV_powheg_pythia8'                                   :      0.564    * PB,
    'ZZTo4L_13TeV_powheg_pythia8'                                      :      1.256    * PB * 1.1,
    'ZZTo4L_13TeV-amcatnloFXFX-pythia8'                                :      1.212    * PB * 1.1,
    'ZZ_TuneCUETP8M1_13TeV-pythia8'                                    :     16.523    * PB,

    'GluGluToZZTo2e2mu_BackgroundOnly_13TeV_MCFM'                      :      0.003194 * PB * 1.7,
    'GluGluToZZTo2e2tau_BackgroundOnly_13TeV_MCFM'                     :      0.003194 * PB * 1.7,
    'GluGluToZZTo2mu2tau_BackgroundOnly_13TeV_MCFM'                    :      0.003194 * PB * 1.7,
    'GluGluToZZTo4e_BackgroundOnly_13TeV_MCFM'                         :      0.001586 * PB * 1.7,
    'GluGluToZZTo4mu_BackgroundOnly_13TeV_MCFM'                        :      0.001586 * PB * 1.7,
    'GluGluToZZTo4tau_BackgroundOnly_13TeV_MCFM'                       :      0.001586 * PB * 1.7,
    'GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8'                  :      0.003194 * PB * 1.7,
    'GluGluToContinToZZTo2e2tau_13TeV_MCFM701_pythia8'                 :      0.003194 * PB * 1.7,
    'GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8'                :      0.003194 * PB * 1.7,
    'GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8'                     :      0.001586 * PB * 1.7,
    'GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8'                    :      0.001586 * PB * 1.7,
    'GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8'                   :      0.001586 * PB * 1.7,
    'GluGluToContinToZZTo2e2nu_13TeV_MCFM701_pythia8'                  :      0.00172  * PB * 1.7,
    'GluGluToContinToZZTo2mu2nu_13TeV_MCFM701_pythia8'                 :      0.00172  * PB * 1.7,
    'GluGluToContinToZZTo2tau2nu_13TeV_MCFM701_pythia8'                :      0.00172  * PB * 1.7,

    'WWW_TuneCUETP8M1_13TeV-amcatnlo-pythia8'                          :      0.1651   * PB,
    'WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8'                          :      0.1651   * PB,
    'WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8'                          :      0.05565  * PB,
    'ZZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8'                          :      0.01398  * PB,
    'WWG_TuneCUETP8M1_13TeV-amcatnlo-pythia8'                          :      0.2147   * PB,
    'WZG_TuneCUETP8M1_13TeV-amcatnlo-pythia8'                          :      0.04123  * PB,

    'HPlusPlusHMinusMinusHTo4L_M-200_13TeV-pythia8'                    :      6.787e-02 * PB, # LO output from pythia8
    'HPlusPlusHMinusMinusHTo4L_M-300_13TeV-pythia8'                    :      1.413e-02 * PB,
    'HPlusPlusHMinusMinusHTo4L_M-400_13TeV-pythia8'                    :      4.160e-03 * PB,
    'HPlusPlusHMinusMinusHTo4L_M-500_13TeV-pythia8'                    :      1.487e-03 * PB,
    'HPlusPlusHMinusMinusHTo4L_M-600_13TeV-pythia8'                    :      6.080e-04 * PB,
    'HPlusPlusHMinusMinusHTo4L_M-700_13TeV-pythia8'                    :      2.806e-04 * PB,
    'HPlusPlusHMinusMinusHTo4L_M-800_13TeV-pythia8'                    :      1.300e-04 * PB,
    'HPlusPlusHMinusMinusHTo4L_M-900_13TeV-pythia8'                    :      6.820e-05 * PB,
    'HPlusPlusHMinusMinusHTo4L_M-1000_13TeV-pythia8'                   :      3.477e-05 * PB,
}


def getXsec(sample):
    if sample in xsecs:
        return xsecs[sample]
    else:
        logging.error('Failed to find cross section for {0}.'.format(sample))
        return 0.
