#======================================================
# histo.py
#
# Author: M. Guigue, T. E. Weiss
# Date: Aug. 4, 2016
#
# Description:
#
# Generic methods to display histograms with ROOT
#=======================================================

"""
Contains generic methods to plot ROOT histograms (1D and 2D)
List of methods:
- histo: plot a 1D histogram using a list of data (x)
- spectra: plot a 1D histogram using two lists of data (x,bin_content)
- histo2D: plot a 2D histogram using two lists of data (x,y)
- aposteriori_distribution: plot a serie of 2D histograms using a list of data names (>=3).
It will form pairs of variables (x,y) and arrange the 2D histograms to get a view
of the aposteriori distributio for these parameters
"""

import logging
logger = logging.getLogger(__name__)

import ROOT as ROOT
import cmath as math
from array import array
import re
import uuid


def histo(param_dict):
    '''
    Create a histogram using a list of X
    '''

    # Preparing the canvas
    logger.debug("Preparing Canvas")
    title, width, height = _preparingCanvas(param_dict)
    can = ROOT.TCanvas(title,title,width,height)
    if 'options' in param_dict.keys():
        if any("logy" in s for s in param_dict['options']):
            logger.debug("Setting Log Y")
            can.SetLogy()
    # Setting the titles
    logger.debug("Preparing Titles")
    xtitle, ytitle = _preparingTitles(param_dict)

    gSave = []
    j = 0

    if isinstance(param_dict['data'],list):

        if 'n_bins' in param_dict:
            nbins = param_dict['n_bins']
        else:
            nbins = 100
        list_histo = []

        myfile = ROOT.TFile(param_dict['input_file_name'],"READ")
        for namedata in param_dict['data']:
            list_data = []
            # myfile.Close()
            tree = myfile.Get(param_dict['input_tree'])
            n = tree.GetEntries()
            for i in range(0,n):
                tree.GetEntry(i)
                list_data.append(getattr(tree,namedata))
                # list_data.append(20*j+18510)

            # list_histo.append()
            if 'x_range' in param_dict:
                if isinstance(param_dict['x_range'],list):

                    if (isinstance(param_dict['x_range'][0],float) or isinstance(param_dict['x_range'][0],int)) and (isinstance(param_dict['x_range'][1],float) or isinstance(param_dict['x_range'][1],int)):
                        if  param_dict['x_range'][0] < param_dict['x_range'][1]:
                            xmin = param_dict['x_range'][0]
                            xmax = param_dict['x_range'][1]
                        else:
                            xmin,xmax = _autoRangeList(list_data)
                    elif isinstance(param_dict['x_range'][0],float):
                        xtemp,xmax = _autoRangeList(list_data)
                        xmin = param_dict['x_range'][0]
                    elif isinstance(param_dict['x_range'][1],float):
                        xmin,xtemp = _autoRangeList(list_data)
                        xmax = param_dict['x_range'][1]
                    else:
                        xmin,xmax = _autoRangeList(list_data)
                else:
                    xmin,xmax = _autoRangeList(list_data)
            else:
                xmin,xmax = _autoRangeList(list_data)
            list_histo.append(ROOT.TH1F(namedata,namedata,nbins,xmin,xmax))
            for i in range(0,n):
                list_histo[j].Fill(list_data[i])
            can.cd()
            if (j==0):
                list_histo[j].Draw('hist')
                list_histo[j].GetXaxis().SetTitle(xtitle);
                list_histo[j].SetTitle(title)
                if 'y_range' in param_dict and isinstance(param_dict['y_range'],list):
                    if (isinstance(param_dict['y_range'][0],float) or isinstance(param_dict['y_range'][0],int)) and (isinstance(param_dict['y_range'][1],float) or isinstance(param_dict['y_range'][1],int)):
                        if  param_dict['y_range'][0] < param_dict['y_range'][1]:
                            list_histo[j].GetYaxis().SetRangeUser(param_dict['y_range'][0],param_dict['y_range'][1])
                    elif isinstance(param_dict['y_range'][0],float):
                        ytemp,ymax = _autoRangeContent(list_histo[j])
                        ymin = param_dict['y_range'][0]
                        list_histo[j].GetYaxis().SetRangeUser(ymin,ymax)
                    elif isinstance(param_dict['y_range'][1],float):
                        ymin,ytemp = _autoRangeContent(list_histo[j])
                        ymax = param_dict['y_range'][1]
                        list_histo[j].GetYaxis().SetRangeUser(ymin,ymax)
            else:
                list_histo[j].Draw("SAME")
            # gSave.append(list_histo[j])
            can.Update()


            j=j+1
    gSave.append(can)

    # Setting the picture file name
    if 'output_path' in param_dict:
        path = param_dict['output_path']
    else:
        path = "./"
    if path.endswith('/')==False:
        path = path + '/'
    if title!=' ':
        figurefullpath = path+title+'_'
    else:
        figurefullpath = path
    for namedata in param_dict['data']:
        figurefullpath += namedata + '_'
    if figurefullpath.endswith('_'):
        figurefullpath = figurefullpath[:-1]
    if 'output_format' in param_dict:
        figurefullpath += '.' + param_dict['output_format']
    else:
        figurefullpath += '.pdf'
    can.SaveAs(figurefullpath)

    return can


def spectra(param_dict):
    '''
    Create a spectrum using a (X,Y) list
    '''
    # Preparing the canvas
    logger.debug("Preparing Canvas")
    title, width, height = _preparingCanvas(param_dict)
    can = ROOT.TCanvas(title,title,width,height)
    if "logy" in param_dict.options:
        can.SetLogy()

    # Setting the titles
    logger.debug("Preparing Titles")
    xtitle, ytitle = _preparingTitles(param_dict)

    gSave = []
    j = 0

    if isinstance(param_dict['data'],list):

        if 'n_bins' in param_dict:
            nbins = param_dict['n_bins']
        else:
            nbins = 100
        list_histo = []

        myfile = ROOT.TFile(param_dict['input_file_name'],"READ")
        for namedata in param_dict['data']:
            if not isinstance(namedata, list):
                logger.critical(' {} is not a list of list; required for spectra ploting; skipping'.format(namedata))
                continue
            list_dataX = []
            list_dataY = []
            # myfile.Close()
            tree = myfile.Get(param_dict['input_tree'])
            n = tree.GetEntries()
            for i in range(0,n):
                tree.GetEntry(i)
                list_dataX.append(getattr(tree,namedata[0]))
                list_dataY.append(getattr(tree,namedata[1]))

            # list_histo.append()
            # logger.debug('Setting x axis')
            if 'x_range' in param_dict:
                if isinstance(param_dict['x_range'],list):

                    if (isinstance(param_dict['x_range'][0],float) or isinstance(param_dict['x_range'][0],int)) and (isinstance(param_dict['x_range'][1],float) or isinstance(param_dict['x_range'][1],int)):
                        if  param_dict['x_range'][0] < param_dict['x_range'][1]:
                            xmin = param_dict['x_range'][0]
                            xmax = param_dict['x_range'][1]
                        else:
                            xmin,xmax = _autoRangeList(list_dataX)
                    elif isinstance(param_dict['x_range'][0],float):
                        xtemp,xmax = _autoRangeList(list_dataX)
                        xmin = param_dict['x_range'][0]
                    elif isinstance(param_dict['x_range'][1],float):
                        xmin,xtemp = _autoRangeList(list_dataX)
                        xmax = param_dict['x_range'][1]
                    else:
                        xmin,xmax = _autoRangeList(list_dataX)
                else:
                    xmin,xmax = _autoRangeList(list_dataX)
            else:
                xmin,xmax = _autoRangeList(list_dataX)
            histo_title = '{}_vs_{}'.format(namedata[1],namedata[0])
            list_histo.append(ROOT.TH1F(histo_title,histo_title,nbins,xmin,xmax))
            for i in range(0,n):
                list_histo[j].Fill(list_dataX[i],list_dataY[i])
            can.cd()
            if (j==0):
                list_histo[j].Draw('hist')
                list_histo[j].GetXaxis().SetTitle(xtitle);
                list_histo[j].SetTitle(title)
                if 'y_range' in param_dict and isinstance(param_dict['y_range'],list):
                    if (isinstance(param_dict['y_range'][0],float) or isinstance(param_dict['y_range'][0],int)) and (isinstance(param_dict['y_range'][1],float) or isinstance(param_dict['y_range'][1],int)):
                        if  param_dict['y_range'][0] < param_dict['y_range'][1]:
                            list_histo[j].GetYaxis().SetRangeUser(param_dict['y_range'][0],param_dict['y_range'][1])
                    elif isinstance(param_dict['y_range'][0],float):
                        ytemp,ymax = _autoRangeContent(list_histo[j])
                        ymin = param_dict['y_range'][0]
                        list_histo[j].GetYaxis().SetRangeUser(ymin,ymax)
                    elif isinstance(param_dict['y_range'][1],float):
                        ymin,ytemp = _autoRangeContent(list_histo[j])
                        ymax = param_dict['y_range'][1]
                        list_histo[j].GetYaxis().SetRangeUser(ymin,ymax)
            else:
                list_histo[j].Draw("SAME")
            # gSave.append(list_histo[j])
            can.Update()


            j=j+1
    gSave.append(can)

    # Setting the picture file name
    if 'output_path' in param_dict:
        path = param_dict['output_path']
    else:
        path = "./"
    if path.endswith('/')==False:
        path = path + '/'
    if title!=' ':
        figurefullpath = path+title+'_'
    else:
        figurefullpath = path
    for namedata in param_dict['data']:
        figurefullpath += namedata[1] + '_vs_'
        figurefullpath += namedata[0] + '_'
    if figurefullpath.endswith('_'):
        figurefullpath = figurefullpath[:-1]
    if 'output_format' in param_dict:
        figurefullpath += '.' + param_dict['output_format']
    else:
        figurefullpath += '.pdf'
    can.SaveAs(figurefullpath)

    return can

def histo2D(param_dict):
    '''
    Plot 2D histogram
    '''
    # Preparing the canvas
    logger.debug("Preparing Canvas")
    title, width, height = _preparingCanvas(param_dict)
    can = ROOT.TCanvas(title,title,width,height)

    if 'options' in param_dict:
        if "logy" in param_dict['options']:
            can.SetLogy()
        if "logx" in param_dict['options']:
            can.SetLogx()

    # Setting the titles
    logger.debug("Preparing Titles")
    xtitle, ytitle = _preparingTitles(param_dict)

    gSave = []
    j = 0

    if 'n_bins_x' in param_dict:
        nbins_x = param_dict['n_bins_x']
    else:
        nbins_x = 100
    if 'n_bins_y' in param_dict:
        nbins_y = param_dict['n_bins_y']
    else:
        nbins_y = 100

    myfile = ROOT.TFile(param_dict['input_file_name'],"READ")
    if 'data' in param_dict:
        namedata = param_dict['data']
    if not isinstance(namedata, list):
        logger.critical(' {} is not a list of list; required for spectra ploting; skipping'.format(namedata))
        return
    list_dataX = []
    list_dataY = []
    # myfile.Close()
    tree = myfile.Get(param_dict['input_tree'])
    n = tree.GetEntries()
    for i in range(0,n):
        tree.GetEntry(i)
        list_dataX.append(getattr(tree,namedata[0]))
        list_dataY.append(getattr(tree,namedata[1]))
    histo = _get2Dhisto(list_dataX, list_dataY, [nbins_x,nbins_y], [0,0], title)
    histo.GetXaxis().SetTitle(namedata[0])
    histo.GetYaxis().SetTitle(namedata[1])

    if 'root_plot_option' in param_dict:
        histo.Draw(param_dict['root_plot_option'])
    else:
        histo.Draw('contz')
    # Setting the picture file name
    if 'output_path' in param_dict:
        path = param_dict['output_path']
    else:
        path = "./"
    if path.endswith('/')==False:
        path = path + '/'
    if title!=' ':
        figurefullpath = path+title+'_'
    else:
        figurefullpath = path
    for namedata in param_dict['data']:
        figurefullpath += namedata + '_'
    if figurefullpath.endswith('_'):
        figurefullpath = figurefullpath[:-1]
    if 'output_format' in param_dict:
        figurefullpath += '.' + param_dict['output_format']
    else:
        figurefullpath += '.pdf'
    can.SaveAs(figurefullpath)

    return can


def aposteriori_distribution(param_dict):
    '''
    Plot a disposition of 2D histogram
    '''
    # Preparing the canvas
    logger.debug("Preparing Canvas")
    title, width, height = _preparingCanvas(param_dict)
    can = ROOT.TCanvas(title,title,width,height)
    can.Draw()
    if 'options' in param_dict:
        if "logy" in param_dict['options']:
            can.SetLogy()

    # Setting the titles
    logger.debug("Preparing Titles")
    xtitle, ytitle = _preparingTitles(param_dict)

    gSave = []
    j = 0

    if 'n_bins_x' in param_dict:
        nbins_x = param_dict['n_bins_x']
    else:
        nbins_x = 100
    if 'n_bins_y' in param_dict:
        nbins_y = param_dict['n_bins_y']
    else:
        nbins_y = 100
    list_histo = []

    myfile = ROOT.TFile(param_dict['input_file_name'],"READ")
    if 'data' in param_dict:
        namedata = param_dict['data']
    list_2Dhisto = _prepare_couples(namedata)
    list_histo = []
    for item in list_2Dhisto:
        if not isinstance(item, list):
            logger.critical(' {} is not a list of list; required for spectra ploting; skipping'.format(namedata))
            return
        list_dataX = []
        list_dataY = []
        # myfile.Close()
        tree = myfile.Get(param_dict['input_tree'])
        n = tree.GetEntries()
        for i in range(0,n):
            tree.GetEntry(i)
            list_dataX.append(getattr(tree,item[0]))
            list_dataY.append(getattr(tree,item[1]))
        histo = _get2Dhisto(list_dataX, list_dataY, [nbins_x,nbins_y], [0,0], '{}_{}'.format(item[0],item[1]))
        histo.SetTitle("")
        histo.GetXaxis().SetTitle(item[0])
        histo.GetYaxis().SetTitle(item[1])
        list_histo.append(histo)

    Ndiv = len(namedata)-1
    ROOT.gStyle.SetOptStat(0)
    can.Divide(Ndiv,Ndiv)
    ix = 0
    iy = 1
    for hist in list_histo:
        ix = ix + 1
        ican = (iy-1)*Ndiv + ix
        can.cd(ican)
        if 'root_plot_option' in param_dict:
            hist.Draw(param_dict['root_plot_option'])
        else:
            hist.Draw('contz')
        if (ix==iy):
            iy = iy+1
            ix = 0

    # Setting the picture file name
    if 'output_path' in param_dict:
        path = param_dict['output_path']
    else:
        path = "./"
    if path.endswith('/')==False:
        path = path + '/'
    if title!=' ':
        figurefullpath = path+title+'_'
    else:
        figurefullpath = path
    for namedata in param_dict['data']:
        figurefullpath += namedata + '_'
    if figurefullpath.endswith('_'):
        figurefullpath = figurefullpath[:-1]
    if 'output_format' in param_dict:
        figurefullpath += '.' + param_dict['output_format']
    else:
        figurefullpath += '.pdf'
    can.Update()

    can.SaveAs(figurefullpath)

    return can


def _set_style_options( rightMargin,  leftMargin,  topMargin,  botMargin):
    '''
    Change ROOT Style of the canvas
    '''
    style = ROOT.TStyle(ROOT.gStyle)
    style.SetOptStat("emr")
    style.SetLabelOffset(0.01,'xy')
    style.SetLabelSize(0.05,'xy')
    style.SetTitleOffset(0.8,'y')
    style.SetTitleSize(0.05,'x')
    style.SetTitleSize(0.05,'y')
    # style.SetLabelSize(0.05,'y')
    # style.SetLabelOffset(0,'y')
    # style.SetLabelSize(0.05,'x')
    style.SetTitleOffset(1.02,'x')

    style.SetPadRightMargin(rightMargin)
    style.SetPadTopMargin(topMargin)
    style.SetPadBottomMargin(botMargin)
    style.SetPadLeftMargin(leftMargin)
    style.cd()

def _preparingCanvas(param_dict):
    '''
    Extract the title, width and height of the TCanvas
    '''
    if 'output_width' in param_dict:
        width = param_dict['output_width']
    else:
        width = 600
    if 'output_height' in param_dict:
        height = param_dict['output_height']
    else:
        height = 400
    # Preparing the canvas
    if 'title' in param_dict and param_dict['title']!='':
        title = param_dict['title']
        _set_style_options(0.04,0.1,0.07,0.12)

    else:
        title = 'can_{}_{}'.format(height,width) #canvas_'+uuid.uuid4().get_hex()
        _set_style_options(0.04,0.1,0.03,0.12)

    return title, width, height

def _preparingTitles(param_dict):
    '''
    Extract the titles of the X and Y axis
    '''
    # Setting the titles
    if 'x_title' in param_dict:
        xtitle = param_dict['x_title']
    else:
        xtitle = ''
    if 'y_title' in param_dict:
        ytitle = param_dict['y_title']
    else:
        ytitle = ''
    return xtitle, ytitle


def _prepare_couples(list_data):
    '''
    Prepare a list of pairs of variables for the a posteriori distribution
    '''
    N = len(list_data)
    newlist = []
    for i in range(1,N): #y
        for j in range(0,i): #x
            newlist.append([list_data[j],list_data[i]])
    return newlist


def _get2Dhisto(list_dataX, list_dataY, nbins, ranges,histo_title):
    '''
    Internal function: return TH2F
    '''
    # logger.debug('Setting x axis')
    x_range = ranges[0]
    if isinstance(x_range,list):
        if isinstance(x_range[0],(float,int)) and isinstance(x_range[1],(float,int)):
            if  x_range[0] < x_range[1]:
                xmin = x_range[0]
                xmax = x_range[1]
            else:
                xmin,xmax = _autoRangeList(list_dataX)
        elif isinstance(x_range[0],(float,int)):
            xtemp,xmax = _autoRangeList(list_dataX)
            xmin = x_range[0]
        elif isinstance(x_range[1],(float,int)):
            xmin,xtemp = _autoRangeList(list_dataX)
            xmax = x_range[1]
        else:
            xmin,xmax = _autoRangeList(list_dataX)
    else:
        xmin,xmax = _autoRangeList(list_dataX)

    # logger.debug('Setting y axis')
    y_range = ranges[0]
    if isinstance(y_range,list):
        if isinstance(y_range[0],(float,int)) and isinstance(y_range[1],(float,int)):
            if  y_range[0] < y_range[1]:
                ymin = y_range[0]
                ymax = y_range[1]
            else:
                ymin,ymax = _autoRangeList(list_dataY)
        elif isinstance(y_range[0],(float,int)):
            ytemp,ymax = _autoRangeList(list_dataY)
            ymin = y_range[0]
        elif isinstance(y_range[1],(float,int)):
            ymin,ytemp = _autoRangeList(list_dataY)
            ymax = y_range[1]
        else:
            ymin,ymax = _autoRangeList(list_dataY)
    else:
        ymin,ymax = _autoRangeList(list_dataY)

    temphisto = ROOT.TH2F(histo_title,histo_title,nbins[0],xmin,xmax,nbins[1],ymin,ymax)
    if len(list_dataX)!=len(list_dataX):
        logger.critical("list of data does not have the same size. x: {}; y: {}".format(len(list_dataX),len(list_dataY)))
        return 0
    for i in range(0,len(list_dataX)):
        temphisto.Fill(list_dataX[i],list_dataY[i])
    return temphisto

def _autoRangeList(list):
    # logger.debug('Using autoRange')
    xmin = min(list)
    xmax = max(list)
    dx = xmax - xmin
    xmin = xmin - dx*0.05
    xmax = xmax + dx*0.05
    return xmin, xmax

def _autoRangeContent(hist):
    # logger.debug('Using autoRange')
    list = []
    for i in range(0,hist.GetNbinsX()):
        list.append(hist.GetBinContent(i))
    xmin = min(list)*0.9
    xmax = max(list)*1.1  # need to be done
    return xmin, xmax
