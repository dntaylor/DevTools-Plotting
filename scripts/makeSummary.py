#!/usr/bin/env python
import argparse
import sys
import os
import glob
import logging

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def getContents(baseDir):
    contents = {'png':[],}
    for f in glob.glob('{0}/*'.format(baseDir)):
        if os.path.isdir(f): # directory
            contents[os.path.basename(f)] = getContents(f)
        elif f.endswith('.png'): # png
            contents['png'] += [os.path.basename(os.path.splitext(f)[0])]
    return contents

def getRows(plotDir,images,width=3):
    allRows = ''
    currentRow = ''
    for i,image in enumerate(images):
        currentRow += HTML.plot.format(plotName=os.path.join(plotDir,image))
        if i%width==width-1: # start a new row
            if currentRow:
                allRows += HTML.plotRow.format(rowCells=currentRow)
            currentRow = ''
    if currentRow: allRows += currentRow
    return allRows

def addPlotSet(plotMap,curDir,rows):
    if len(plotMap['png']):
        images = sorted(plotMap['png'])
        label = curDir if curDir else 'Default'
        navcontent = HTML.navelement.format(
            label=label.replace('/','_'),
            dirName=label,
        )
        tabcontent = HTML.plotSet.format(
            label=label.replace('/','_'),
            dirName=label,
            tableRows=getRows(curDir,images,width=3),
        )

        rows[label] = [navcontent,tabcontent]

    for nextDir in sorted(plotMap):
        if nextDir=='png': continue
        addPlotSet(plotMap[nextDir],os.path.join(curDir,nextDir),rows)


def getSubDirs(curDir,plotMap):
    fullDirs = []
    for subDir in plotMap:
        if subDir=='png' and len(plotMap[subDir]):
            fullDirs += [curDir]
            continue
        subDirs = getSubDirs(subDir,plotMap[subDir])
        fullDirs += [os.path.join(curDir,x) for x in subDirs]
    return fullDirs

def buildMenu(plotMap,rows):
    '''Build the naviagtion menu'''
    menu = ''
    topDirs = {}
    for plotDir in plotMap:
        if plotDir=='png':
            if len(plotMap['png']): topDirs['Default'] = ['Default']
            continue
        topDirs[plotDir] = getSubDirs(plotDir,plotMap[plotDir])
    for topDir in sorted(topDirs):
        thisnav = ''
        thisnav += ''.join([rows[x][0] for x in sorted(topDirs[topDir])])
        menu += HTML.navdropdown.format(
            navelements=thisnav,
            label=topDir,
        )
    fullmenu = HTML.navbar.format(navelements=menu)
    return fullmenu
        
    #return HTML.navbar.format(navelements=''.join([x[0] for x in rows]))

def buildHTML(plotDir):
    if not os.path.exists(plotDir):
        logging.warning('{0} is not a directory'.format(plotDir))
        return
    logging.info('Building HTML for {0}'.format(plotDir))
    analysis = os.path.basename(plotDir)
    allPlots = getContents('{0}/png'.format(plotDir))
    with open(os.path.join(plotDir,'index.html'),'w') as index:
        rows = {}
        addPlotSet(allPlots,'',rows)
        index.write(
            HTML.header.format(
                analysis=analysis,
                navbar=buildMenu(allPlots,rows),
            )
        )
        for row in sorted(rows):
            index.write(rows[row][1])
        index.write(
            HTML.footer
        )



# HTML Templates
class HTML :
    header = '''<html>
<head>
    <title>{analysis} Plots</title>
    <style type="text/css">
        div.plotSet {{
            margin: auto;
            width: 90%;
            max-width: 1200px;
            border: 2px solid #888888;
        }}
        img.plot {{
            max-width: 100%;
            height: auto;
            width: 100%;
        }}

        table {{
            width: 100%;
        }}
    </style>
    <link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.2/jquery.min.js"></script>
    <script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
</head>
<body>
{navbar}
<div class="tab-content">
'''

    navbar = '''<ul class="nav nav-tabs">
  {navelements}
</ul>
'''

    navelement = '''<li><a data-toggle="tab" href="#{label}">{label}</a></li>
'''

    navdropdown = '''<li class="dropdown">
  <a class="dropdown-toggle" data-toggle="dropdown" href="#">{label}
  <span class="caret"></span></a>
  <ul class="dropdown-menu">
    {navelements}
  </ul>
</li>
'''

    plotSet = '''<div id="{label}" class="tab-pane fade in">
  <div class="plotSet">
    <div style="text-align: center;"><b>{dirName}</b></div>
    <table>
      {tableRows}
    </table>
  </div>
  <br/>
  </div>
'''

    plotRow = '''
      <tr style="text-align: center; max-width: 90%;">
        {rowCells}
      </tr>
'''

    plot = '''
        <td style="text-align: center;">
          {plotName}<br/>
          <img src="png/{plotName}.png" class="plot" /><br/>
          <a href="pdf/{plotName}.pdf">[pdf]</a> - <a href="root/{plotName}.root">[root]</a>
        </td>
'''

    emptyPlot = '''<td style="text-align: center;"></td>
'''

    footer = '''
</div>
</body>
</html>
'''

def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Produce HTML output')

    parser.add_argument('directories', type=str, nargs='+', help='Directories to process')

    return parser.parse_args(argv)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)
    for directory in args.directories:
        for thisDir in glob.glob(directory):
            buildHTML(thisDir)

if __name__ == "__main__":
    status = main()
    sys.exit(status)


