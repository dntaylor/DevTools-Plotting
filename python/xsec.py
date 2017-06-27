import logging
from xsec_Hpp4l import xsecs as xsecs_4l
from xsec_Hpp4l import xsecs_NLO as xsecs_4l_NLO
from xsec_Hpp4l import xsecs_kfactor as xsecs_4l_kfactor
from xsec_Hpp4l import xsecs_right as xsecs_r4l
from xsec_Hpp4l import xsecs_right_NLO as xsecs_r4l_NLO
from xsec_Hpp4l import xsecs_right_kfactor as xsecs_r4l_kfactor

PB = 1.
pb = PB
FB = 1.e-3
fb = FB

# where possible, taken from https://twiki.cern.ch/twiki/bin/viewauth/CMS/SummaryTable1G25ns
xsecs = {
    'DoubleMuon'                                                       : 1.,
    'DoubleEG'                                                         : 1.,
    'MuonEG'                                                           : 1.,
    'SingleMuon'                                                       : 1.,
    'SingleElectron'                                                   : 1.,
    'SinglePhoton'                                                     : 1.,
    'Tau'                                                              : 1.,

    'QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8'                  : 1.,
    'QCD_Pt-20toInf_MuEnrichedPt15_TuneCUETP8M1_13TeV_pythia8'         : 720648000 * PB,

    'GJet_Pt-20toInf_DoubleEMEnriched_MGG-40to80_TuneCUETP8M1_13TeV_Pythia8'  :   3216.0 * PB,
    'GJet_Pt-20to40_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8'  :    220.0 * PB,
    'GJet_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8' :    850.8 * PB,
    'QCD_Pt-30toInf_DoubleEMEnriched_MGG-40to80_TuneCUETP8M1_13TeV_Pythia8'   : 260500.0 * PB,
    'QCD_Pt-30to40_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8'   :  22110.0 * PB,
    'QCD_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8'  : 113400.0 * PB,

    # QCD pt binned
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

    # DY
    'DYJetsToLL_M-5to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'        :  71310        * PB,
    'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'       :  18610        * PB,
    'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'      :  18610.       * PB,
    'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'          :   1921.8 * 3  * PB,
    'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'           :   1921.8 * 3  * PB,

    # DY jet binned
    'DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'     :    421.5      * PB,
    'DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'     :    184.3      * PB,
    'DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      :    725.       * PB * 1.216 * 0.256, # match efficiency 0.256
    'DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      :    394.5      * PB * 1.216 * 0.188, # match efficiency 0.188
    'DY3JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      :     96.47     * PB * 1.216 * 0.0722, # match efficiency 0.0722
    'DY4JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      :     34.84     * PB * 1.216 * 0.0388, # match efficiency 0.0388
    'DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          :   1016.       * PB * 1.216,
    'DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          :    331.4      * PB * 1.216,
    'DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          :     96.36     * PB * 1.216,
    'DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          :     51.4      * PB * 1.216,

    # DY pt binned
    'DYJetsToLL_Pt-50To100_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'    :    354.3      * PB,
    'DYJetsToLL_Pt-100To250_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'   :     83.12     * PB,
    'DYJetsToLL_Pt-250To400_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'   :      3.047    * PB,
    'DYJetsToLL_Pt-400To650_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'   :      0.3921   * PB,
    'DYJetsToLL_Pt-650ToInf_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'   :      0.03636  * PB,

    # GG
    'DiPhotonJetsBox_M40_80-Sherpa'                                    :    303.2      * PB,
    'DiPhotonJetsBox_MGG-80toInf_13TeV-Sherpa'                         :     84.4      * PB,
    'DiPhotonJets_MGG-80toInf_13TeV_amcatnloFXFX_pythia8'              :    135.1      * PB,

    # single top
    'ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1'                    :   3.36 * PB,
    'ST_t-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1'                    :  70.69 * PB,
    'ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1'              :  26.38 * PB,
    'ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1' :  80.95 * PB, # ??
    'ST_t-channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin'       :  80.95 * PB, # ??
    'ST_t-channel_top_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1'                  :  44.33 * PB,
    'ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1'     : 136.02 * PB, # ??
    'ST_t-channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin'           : 136.02 * PB, # ??
    'ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1'                      :  35.85 * PB,
    'ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4'                    :  35.85 * PB,
    'ST_tW_top_5f_NoFullyHadronicDecays_13TeV-powheg_TuneCUETP8M1'                        :  38.09 * PB, # ??
    'ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1'                  :  35.85 * PB,
    'ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4'                :  35.85 * PB,
    'ST_tW_antitop_5f_NoFullyHadronicDecays_13TeV-powheg_TuneCUETP8M1'                    :  38.09 * PB, # ??

    # TTbar
    'TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'                   :    831.76     * PB,
    'TTTo2L2Nu_13TeV-powheg'                                           :     87.31     * PB,
    'TT_TuneCUETP8M1_13TeV-powheg-pythia8'                             :    831.76     * PB,
    'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'             :     87.31     * PB,
    'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'    :    114.5      * PB,
    'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' :    114.6      * PB,
    'TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'                    :    502.2      * PB,

    # TTV
    'TTGJets_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8'          :      3.697    * PB,
    'TTZToLLNuNu_M-10_TuneCUETP8M1_13TeV-amcatnlo-pythia8'             :      0.2529   * PB,
    'TTZToQQ_TuneCUETP8M1_13TeV-amcatnlo-pythia8'                      :      0.5297   * PB,
    'TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8'     :      0.2043   * PB,
    'TTWJetsToQQ_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8'      :      0.4062   * PB,
    'ttZJets_13TeV_madgraphMLM'                                        :      0.259    * PB,
    'ttZJets_13TeV_madgraphMLM-pythia8'                                :      0.259    * PB,
    'ttWJets_13TeV_madgraphMLM'                                        :      0.243    * PB,
    'ttH_M125_13TeV_powheg_pythia8'                                    :      0.5085   * PB,

    # T+G
    'TGJets_TuneCUETP8M1_13TeV_amcatnlo_madspin_pythia8'               :      2.967    * PB,
    'TTGG_0Jets_TuneCUETP8M1_13TeV_amcatnlo_madspin_pythia8'           :      0.01731  * PB,
    'TTGJets_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8'          :      3.819    * PB,

    # TZ
    'tZq_ll_4f_13TeV-amcatnlo-pythia8'                                 :      0.0758   * PB,
    'tZq_ll_4f_13TeV-amcatnlo-pythia8_TuneCUETP8M1'                    :      0.0758   * PB,
    'tZq_nunu_4f_13TeV-amcatnlo-pythia8_TuneCUETP8M1'                  :      0.1379   * PB,

    # W
    'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'               :  61526.7      * PB,
    'WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'                :  61526.7      * PB,

    # W jet binned
    'W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'               :   9493        * PB * 1.214,
    'W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'               :   3120        * PB * 1.214,
    'W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'               :    942.3      * PB * 1.214,
    'W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'               :    524.2      * PB * 1.214,    

    # W pt binned
    'WJetsToLNu_Pt-100To250_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'   :    676.3      * PB * 0.41, # filter efficiency 0.41
    'WJetsToLNu_Pt-250To400_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'   :     23.94     * PB * 0.43, # filter efficiency 0.43
    'WJetsToLNu_Pt-400To600_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'   :      3.031    * PB * 0.44, # filter efficiency 0.44
    'WJetsToLNu_Pt-600ToInf_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'   :      0.4524   * PB * 0.44, # filter efficiency 0.44

    # W ht binned
    'WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'    :   1345        * PB * 1.214,
    'WJetsToLNu_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'    :    359.7      * PB * 1.214,
    'WJetsToLNu_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'    :     48.91     * PB * 1.214,
    'WJetsToLNu_HT-600To800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'    :     12.05     * PB * 1.214,
    'WJetsToLNu_HT-800To1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'   :      5.501    * PB * 1.214,
    'WJetsToLNu_HT-1200To2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'  :      1.329    * PB * 1.214,
    'WJetsToLNu_HT-2500ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'   :      0.03216  * PB * 1.214,
                 
    # VG                                                                               
    'ZGTo2LG_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'                  :    117.864    * PB,    
    'WGToLNuG_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'                 :    489.       * PB,
    'WGToLNuG_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'                  :    405.271    * PB,

    # https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageAt1314TeV2014
    # https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageBR
    # PDG
    'WH_HToBB_WToLNu_M125_13TeV_amcatnloFXFX_madspin_pythia8'          :      1.380  * 0.5824 * (0.108*3)    * PB, # WH * H->bb * W->lnu
    'ZH_HToBB_ZToLL_M125_13TeV_amcatnloFXFX_madspin_pythia8'           :      0.8696 * 0.5824 * (0.033658*3) * PB, # ZH * H->bb * Z->ll
    'ZH_HToBB_ZToNuNu_M125_13TeV_amcatnloFXFX_madspin_pythia8'         :      0.8696 * 0.5824 * 0.2          * PB, # ZH * H->bb * Z->inv
    'ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8'                         :      0.8696 * 0.5824 * 0.6991       * PB, # ZH * H->bb * Z->had
    'ZH_HToGG_ZToAll_M125_13TeV_powheg_pythia8'                        :      0.8696 * 0.00227               * PB, # ZH * H->gamgam
    'ZH_HToZG_ZToAll_M-125_13TeV_powheg_pythia8'                       :      0.8696 * 0.001533              * PB, # ZH * H->Zgam
    'ZHToTauTau_M125_13TeV_powheg_pythia8'                             :      0.8696 * 0.006272              * PB, # ZH * H->tautau
    'ZH_HToZZ_4LFilter_M125_13TeV_powheg2-minlo-HZJ_JHUgenV6_pythia8'  :      0.147 * PB, # MCM , 0.8696 * 0.02619 * (0.033658*3)**2 # ZH * H->ZZ * Z->ll^2 
    'ZH_HToBB_ZToLL_M125_13TeV_powheg_herwigpp'                        :      0.07495  * PB,
    'ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8'                       :      0.8696 * 0.5824 * 0.2          * PB, # ZH * H->bb * Z->inv
    'ZH_HToZZ_4LFilter_M126_13TeV_powheg2-minlo-HZJ_JHUgenV6_pythia8'  :      0.147 * PB,

    # WW
    'WWTo2L2Nu_13TeV-powheg'                                           :     10.481    * PB,
    'WWTo4Q_13TeV-powheg'                                              :     45.20     * PB,
    'WWToLNuQQ_13TeV-powheg'                                           :     43.53     * PB,
    'WWTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8'                   :     45.85     * PB,
    'WWTo4Q_4f_13TeV_amcatnloFXFX_madspin_pythia8'                     :     45.31     * PB,
    'WW_TuneCUETP8M1_13TeV-pythia8'                                    :     63.21     * PB,
    'GluGluWWTo2L2Nu_MCFM_13TeV'                                       :      0.39     * PB,

    # WZ
    'WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8'                   :     10.71     * PB,
    'WZTo1L3Nu_13TeV_amcatnloFXFX_madspin_pythia8'                     :      3.05     * PB,
    'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8'                      :      5.60     * PB,
    'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8'                       :      4.42965  * PB,
    'WZJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'                   :      4.71     * PB,
    'WZ_TuneCUETP8M1_13TeV-pythia8'                                    :     47.13     * PB,
    'WZJToLLLNu_TuneCUETP8M1_13TeV-amcnlo-pythia8'                     :      4.715    * PB,
    'WZTo3LNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'                 :      4.712    * PB,

    'WLLJJ_WToLNu_EWK_TuneCUETP8M1_13TeV_madgraph-madspin-pythia8'           :  0.01763  * PB,
    'WLLJJ_WToLNu_EWK_aQGC-FM_TuneCUETP8M1_13TeV_madgraph-madspin-pythia8'   :  0.01412  * PB,
    'WLLJJ_WToLNu_EWK_aQGC-FS_TuneCUETP8M1_13TeV_madgraph-madspin-pythia8'   :  0.04543  * PB,
    'WLLJJ_WToLNu_EWK_aQGC-FT_TuneCUETP8M1_13TeV_madgraph-madspin-pythia8'   :  0.4968   * PB,
    'WLLJJ_WToLNu_MLL-4To60_EWK_TuneCUETP8M1_13TeV_madgraph-madspin-pythia8' :  0.005485 * PB,

    'WZJJ_EWK_13TeV-madgraph-pythia8'                                  :      0.039    * PB, # ??
    'WZJJ_EWK_QCD_13TeV-madgraph-pythia8'                              :      0.5      * PB, # ??
    'WZJJ_QCD_13TeV-madgraph-pythia8'                                  :      0.47     * PB, # ??

    'WZTo3LNu_0Jets_MLL-4To50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'  :      2.3011   * PB,
    'WZTo3LNu_0Jets_MLL-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     :      0.5771   * PB,
    'WZTo3LNu_1Jets_MLL-4To50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'  :      0.5291   * PB,
    'WZTo3LNu_1Jets_MLL-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     :      0.3446   * PB,
    'WZTo3LNu_2Jets_MLL-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     :      0.07684  * PB,
    'WZTo3LNu_3Jets_MLL-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     :      0.1112   * PB,

    'WZToLNu2Q_13TeV_powheg_pythia8'                                   :      9.877    * PB,

    # ZZ
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
    'GluGluToContinToZZTo4e_13TeV_DefaultShower_MCFM701_pythia8'       :      1.575    * PB, # ??
    'GluGluToContinToZZTo4mu_13TeV_DefaultShower_MCFM701_pythia8'      :      1.575    * PB, # ??

    'ZZJJTo4L_EWK_13TeV-madgraph-pythia8'                              :      0.0004404* PB,
    'ZZJJTo4L_QCD_13TeV-madgraph-pythia8'                              :      0.009335 * PB,

    'ZZTo2L2Nu_0Jets_ZZOnShell_13TeV-amcatnloFXFX-madspin-pythia8'     :      0.3916   * PB * 0.613, # match efficiency 0.613
    'ZZTo2L2Nu_1Jets_ZZOnShell_13TeV-amcatnloFXFX-madspin-pythia8'     :      0.2453   * PB * 0.333, # match efficiency 0.333
    'ZZTo2L2Q_13TeV_powheg_pythia8'                                    :      1.999    * PB,
    'ZZTo2Q2Nu_13TeV_powheg_pythia8'                                   :      3.824    * PB,
    'ZZTo4L_0Jets_ZZOnShell_13TeV-amcatnloFXFX-madspin-pythia8'        :      0.042    * PB * 0.620, # match efficiency 0.620
    'ZZTo4L_1Jets_ZZOnShell_13TeV-amcatnloFXFX-madspin-pythia8'        :      0.0215   * PB * 0.297, # match efficiency 0.297
    'ZZTo4L_2Jets_ZZOnShell_13TeV-amcatnloFXFX-madspin-pythia8'        :      0.0086   * PB * 0.187, # match efficiency 0.187

    # VVV
    'WWW_TuneCUETP8M1_13TeV-amcatnlo-pythia8'                          :      0.1651   * PB,
    'WWW_4F_TuneCUETP8M1_13TeV-amcatnlo-pythia8'                       :      0.2086   * PB,
    'WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8'                          :      0.1651   * PB,
    'WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8'                          :      0.05565  * PB,
    'ZZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8'                          :      0.01398  * PB,
    'WWG_TuneCUETP8M1_13TeV-amcatnlo-pythia8'                          :      0.2147   * PB,
    'WZG_TuneCUETP8M1_13TeV-amcatnlo-pythia8'                          :      0.04123  * PB,
    'WGGJets_TuneCUETP8M1_13TeV_madgraphMLM_pythia8'                   :      1.       * PB, # ??
    'WGG_5f_TuneCUETP8M1_13TeV-amcatnlo-pythia8'                       :      1.869    * PB,
    'ZGGJetsToLLGG_5f_LO_amcatnloMLM_pythia8'                          :      1.       * PB, # ??
    'ZGGJets_ZToHadOrNu_5f_LO_madgraph_pythia8'                        :      1.       * PB, # ??
    'ZGGToLLGG_5f_TuneCUETP8M1_13TeV-amcatnlo-pythia8'                 :      0.6257   * PB,
    'ZGGToNuNuGG_5f_TuneCUETP8M1_13TeV-amcatnlo-pythia8'               :      0.07477  * PB,


    # H++
    'HPlusPlusHMinusHTo3L_M-200_TuneCUETP8M1_13TeV_calchep-pythia8'    :      0.12572    * PB * xsecs_4l_kfactor[200], # LO from calchep * kfactor from PP
    'HPlusPlusHMinusHTo3L_M-300_TuneCUETP8M1_13TeV_calchep-pythia8'    :      0.026895   * PB * xsecs_4l_kfactor[300],
    'HPlusPlusHMinusHTo3L_M-400_TuneCUETP8M1_13TeV_calchep-pythia8'    :      0.0083070  * PB * xsecs_4l_kfactor[400],
    'HPlusPlusHMinusHTo3L_M-500_TuneCUETP8M1_13TeV_calchep-pythia8'    :      0.0031227  * PB * xsecs_4l_kfactor[500],
    'HPlusPlusHMinusHTo3L_M-600_TuneCUETP8M1_13TeV_calchep-pythia8'    :      0.0013286  * PB * xsecs_4l_kfactor[600],
    'HPlusPlusHMinusHTo3L_M-700_TuneCUETP8M1_13TeV_calchep-pythia8'    :      0.00061233 * PB * xsecs_4l_kfactor[700],
    'HPlusPlusHMinusHTo3L_M-800_TuneCUETP8M1_13TeV_calchep-pythia8'    :      0.00029918 * PB * xsecs_4l_kfactor[800],
    'HPlusPlusHMinusHTo3L_M-900_TuneCUETP8M1_13TeV_calchep-pythia8'    :      0.00015252 * PB * xsecs_4l_kfactor[900],
    'HPlusPlusHMinusHTo3L_M-1000_TuneCUETP8M1_13TeV_calchep-pythia8'   :      8.0121e-05 * PB * xsecs_4l_kfactor[1000],
    'HPlusPlusHMinusHTo3L_M-1100_TuneCUETP8M1_13TeV_calchep-pythia8'   :      4.3159e-05 * PB * xsecs_4l_kfactor[1100],
    'HPlusPlusHMinusHTo3L_M-1200_TuneCUETP8M1_13TeV_calchep-pythia8'   :      2.3647e-05 * PB * xsecs_4l_kfactor[1200],
    'HPlusPlusHMinusHTo3L_M-1300_TuneCUETP8M1_13TeV_calchep-pythia8'   :      1.3142e-05 * PB * xsecs_4l_kfactor[1300],
    'HPlusPlusHMinusHTo3L_M-1400_TuneCUETP8M1_13TeV_calchep-pythia8'   :      7.3782e-06 * PB * xsecs_4l_kfactor[1400],
    'HPlusPlusHMinusHTo3L_M-1500_TuneCUETP8M1_13TeV_calchep-pythia8'   :      4.1720e-06 * PB * xsecs_4l_kfactor[1500],

    'HPlusPlusHMinusHTo3L_M-200_13TeV-calchep-pythia8'                 :      0.12572    * PB * xsecs_4l_kfactor[200], # LO from calchep * kfactor from PP
    'HPlusPlusHMinusHTo3L_M-300_13TeV-calchep-pythia8'                 :      0.026895   * PB * xsecs_4l_kfactor[300],
    'HPlusPlusHMinusHTo3L_M-400_13TeV-calchep-pythia8'                 :      0.0083070  * PB * xsecs_4l_kfactor[400],
    'HPlusPlusHMinusHTo3L_M-500_13TeV-calchep-pythia8'                 :      0.0031227  * PB * xsecs_4l_kfactor[500],
    'HPlusPlusHMinusHTo3L_M-600_13TeV-calchep-pythia8'                 :      0.0013286  * PB * xsecs_4l_kfactor[600],
    'HPlusPlusHMinusHTo3L_M-700_13TeV-calchep-pythia8'                 :      0.00061233 * PB * xsecs_4l_kfactor[700],
    'HPlusPlusHMinusHTo3L_M-800_13TeV-calchep-pythia8'                 :      0.00029918 * PB * xsecs_4l_kfactor[800],
    'HPlusPlusHMinusHTo3L_M-900_13TeV-calchep-pythia8'                 :      0.00015252 * PB * xsecs_4l_kfactor[900],
    'HPlusPlusHMinusHTo3L_M-1000_13TeV-calchep-pythia8'                :      8.0121e-05 * PB * xsecs_4l_kfactor[1000],
    'HPlusPlusHMinusHTo3L_M-1100_13TeV-calchep-pythia8'                :      4.3159e-05 * PB * xsecs_4l_kfactor[1100],
    'HPlusPlusHMinusHTo3L_M-1200_13TeV-calchep-pythia8'                :      2.3647e-05 * PB * xsecs_4l_kfactor[1200],
    'HPlusPlusHMinusHTo3L_M-1300_13TeV-calchep-pythia8'                :      1.3142e-05 * PB * xsecs_4l_kfactor[1300],
    'HPlusPlusHMinusHTo3L_M-1400_13TeV-calchep-pythia8'                :      7.3782e-06 * PB * xsecs_4l_kfactor[1400],
    'HPlusPlusHMinusHTo3L_M-1500_13TeV-calchep-pythia8'                :      4.1720e-06 * PB * xsecs_4l_kfactor[1500],

}

for mass in xsecs_4l_NLO:
    xsecs['HPlusPlusHMinusMinusHTo4L_M-{0}_TuneCUETP8M1_13TeV_pythia8'.format(mass)] = xsecs_4l_NLO[mass]
    xsecs['HPlusPlusHMinusMinusHTo4L_M-{0}_13TeV-pythia8'.format(mass)] = xsecs_4l_NLO[mass]
    xsecs['HPlusPlusHMinusMinusHRTo4L_M-{0}_TuneCUETP8M1_13TeV_pythia8'.format(mass)] = xsecs_r4l_NLO[mass]
    xsecs['HPlusPlusHMinusMinusHRTo4L_M-{0}_13TeV-pythia8'.format(mass)] = xsecs_r4l_NLO[mass]


def getXsec(sample):
    if sample in xsecs:
        return xsecs[sample]
    else:
        logging.error('Failed to find cross section for {0}.'.format(sample))
        return 0.
