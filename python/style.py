import ROOT

# Some colors
colors = {
    'Gray'       : {'color' : ROOT.TColor.GetColor('#B8B8B8'), 'accent' : ROOT.TColor.GetColor('#C8C8C8')},
    'Purple'     : {'color' : ROOT.TColor.GetColor('#AD33FF'), 'accent' : ROOT.TColor.GetColor('#7924B2')},
    'Yellow'     : {'color' : ROOT.TColor.GetColor('#FFFF00'), 'accent' : ROOT.TColor.GetColor('#FFCC26')},
    'Gold'       : {'color' : ROOT.TColor.GetColor('#FFCC00'), 'accent' : ROOT.TColor.GetColor('#FFD633')},
    'DarkYellow' : {'color' : ROOT.TColor.GetColor('#FFCC00'), 'accent' : ROOT.TColor.GetColor('#E6B800')},
    'Orange'     : {'color' : ROOT.TColor.GetColor('#DC7612'), 'accent' : ROOT.TColor.GetColor('#BD3200')},
    'Blue'       : {'color' : ROOT.TColor.GetColor('#107FC9'), 'accent' : ROOT.TColor.GetColor('#0E4EAD')},
    'Navy'       : {'color' : ROOT.TColor.GetColor('#003399'), 'accent' : ROOT.TColor.GetColor('#00297A')},
    'Steel'      : {'color' : ROOT.TColor.GetColor('#9999FF'), 'accent' : ROOT.TColor.GetColor('#B8B8FF')},
    'DarkRed'    : {'color' : ROOT.TColor.GetColor('#A30000'), 'accent' : ROOT.TColor.GetColor('#8F0000')},
    'Red'        : {'color' : ROOT.TColor.GetColor('#F01800'), 'accent' : ROOT.TColor.GetColor('#780000')},
    'Green'      : {'color' : ROOT.TColor.GetColor('#36802D'), 'accent' : ROOT.TColor.GetColor('#234D20')},
    'BlueGreen'  : {'color' : ROOT.TColor.GetColor('#00CC99'), 'accent' : ROOT.TColor.GetColor('#00A37A')},
    'LightGreen' : {'color' : ROOT.TColor.GetColor('#66FF99'), 'accent' : ROOT.TColor.GetColor('#52CC7A')},
    'LightBlue'  : {'color' : ROOT.TColor.GetColor('#66CCFF'), 'accent' : ROOT.TColor.GetColor('#33BBFF')},
    'Lime'       : {'color' : ROOT.TColor.GetColor('#9ED54C'), 'accent' : ROOT.TColor.GetColor('#59A80F')},
    'Aqua'       : {'color' : ROOT.TColor.GetColor('#66FFFF'), 'accent' : ROOT.TColor.GetColor('#52CCCC')},
    'GreyBlue'   : {'color' : ROOT.TColor.GetColor('#99CCFF'), 'accent' : ROOT.TColor.GetColor('#CCE6FF')},
    'Pink'       : {'color' : ROOT.TColor.GetColor('#FF99DD'), 'accent' : ROOT.TColor.GetColor('#FFCCEE')},
}

colorMap = {
    'MC'        : 'Red',
    'BG'        : 'Blue',
    'EWK'       : 'Blue',
    'QCD'       : 'Pink',
    'datadriven': 'Gray',
    'ZZ'        : 'Blue',
    'ZG'        : 'Red',
    'WZ'        : 'LightBlue',
    'WW'        : 'GreyBlue',
    'VV'        : 'GreyBlue',
    'VH'        : 'Steel',
    'VVV'       : 'Navy',
    'VVG'       : 'Navy',
    'WWW'       : 'Navy',
    'WWZ'       : 'Navy',
    'WZZ'       : 'Navy',
    'ZZZ'       : 'Navy',
    'TTV'       : 'BlueGreen', 
    'TTG'       : 'BlueGreen', 
    'TTZ'       : 'BlueGreen', 
    'TTW'       : 'BlueGreen', 
    'Z'         : 'DarkYellow',
    'W'         : 'Aqua',
    'TT'        : 'Green',
    'T'         : 'LightGreen',
    'GG'        : 'LightBlue',
    'G'         : 'Blue',
    'HppHmm'    : 'Orange',
    'HppHmmR'   : 'Orange',
    'HppHm'     : 'Orange',
    'POWHEG'    : 'LightBlue',
    'AMCATNLO'  : 'Red',
    'SHERPA'    : 'Green',
    'PYTHIA'    : 'Purple',
}

labelMap = {
    'MC'        : 'Simulation',
    'BG'        : 'Background',
    'EWK'       : 'Electroweak',
    'QCD'       : 'QCD',
    'datadriven': 'Nonprompt',
    'ZZ'        : 'ZZ',
    'ZG'        : 'Z#gamma',
    'WZ'        : 'WZ',
    'WW'        : 'WW',
    'VH'        : 'VH',
    'VV'        : 'VV',
    'VVV'       : 'VVV',
    'VVG'       : 'VV#gamma+V#gamma#gamma',
    'WWW'       : 'WWW',
    'WWZ'       : 'WWZ',
    'WZZ'       : 'WZZ',
    'ZZZ'       : 'ZZZ',
    'TTV'       : 't#bar{t}V+tZ',
    'TTG'       : 't#bar{t}#gamma+t#bar{t}#gamma#gamma+t#gamma',
    'TTZ'       : 't#bar{t}Z',
    'TTW'       : 't#bar{t}W',
    'Z'         : 'Drell-Yan',
    'W'         : 'W',
    'TT'        : 't#bar{t}',
    'T'         : 'Single Top',
    'GG'        : '#gamma#gamma',
    'G'         : '#gamma',
    'HppHmm'    : '#Phi^{++}#Phi^{#font[122]{\55}#font[122]{\55}}',
    'HppHmmR'   : '#Phi_{R}^{++}#Phi_{R}^{#font[122]{\55}#font[122]{\55}}',
    'HppHm'     : '#Phi^{#pm#pm}#Phi^{#mp}',
    'AMCATNLO'  : 'amc@NLO',
    'SHERPA'    : 'Sherpa',
    'PYTHIA'    : 'Pythia',
    'POWHEG'    : 'POWHEG',
}

for sig in ['HppHmm','HppHm','HppHmmR']:
    for mass in [200,250,300,350,400,450,500,600,700,800,900,1000,1100,1200,1300,1400,1500]:
        key = '{0}{1}GeV'.format(sig,mass)
        colorMap[key] = colorMap[sig]
        labelMap[key] = '#splitline{{{0}}}{{({1} GeV)}}'.format(labelMap[sig],mass)



def getStyle(sample):
    style = {}
    if 'data'==sample:
        style['legendstyle'] = 'ep'
        style['drawstyle'] = 'ex0' # TH1
        #style['drawstyle'] = 'p0' # TGraph
        style['name'] = 'Observed'
    else:
        style['legendstyle'] = 'f'
        style['drawstyle'] = 'hist'
        style['fillstyle'] = 1001
        if sample in colorMap:
            style['linecolor'] = colors[colorMap[sample]]['accent']
            style['fillcolor'] = colors[colorMap[sample]]['color']
        else:
            style['linecolor'] = ROOT.kBlack
            style['fillcolor'] = ROOT.kBlack
        if sample in labelMap:
            style['name'] = labelMap[sample]
        else:
            style['name'] = sample
    return style
