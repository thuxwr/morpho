'''
Plot a diagnostic scattering plot for Z score versus posterior shrinkage.
Authors: W. Xu
Date: 11/21/18
'''

from __future__ import absolute_import

from morpho.utilities import morphologging, reader
from morpho.processors import BaseProcessor
from morpho.processors.plots import RootCanvas
logger = morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)


class ScatterPlot(BaseProcessor):
    '''
    Scattering plot generator, x axis: posterior shrinkage; y axis: Z-score.

    Parameters:
        variables (required): name(s) of the variable in the data
        width: window width (default=600)
        height: window height (default=400)
        output_path: where to save the plot
        output_pformat: plot format (default=pdf)

    Input:
        data: list containing dictionaries for prior sampling result and all posterior sampling results.

    Results:
        None
    '''

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    def InternalConfigure(self, param_dict):
        try:
            self.rootcanvas = RootCanvas(param_dict, optStat=0)
        except:
            self.rootcanvas = RootCanvas.RootCanvas(param_dict, optStat=0)

        # Read other parameters
        self.namedata = reader.read_param(param_dict, 'variables', "required")
        return True

    def InternalRun(self):
        self.rootcanvas.Draw()
        if len(self.namedata) < 2:
            self.rootcanvas.Divide(1, 1)
        elif len(self.namedata) < 3:
            self.rootcanvas.Divide(2, 1)
        elif len(self.namedata) < 5:
            self.rootcanvas.Divide(2, 2)
        elif len(self.namedata) < 7:
            self.rootcanvas.Divide(3, 2)
        elif len(self.namedata) < 10:
            self.rootcanvas.Divide(3, 3)
        else:
            self.rootcanvas.Divide(1, len(self.namedata))

        listGraph = []
        try:
            import ROOT
        except ImportError:
            pass

        for iName, name in enumerate(self.namedata):
            self.rootcanvas.cd(iName+1)
            listGraph.append(ROOT.TGraph())
            sd_prior = self.data[0]['sd'][str(name)]
            for nsample in range(1, len(self.data)):
                subdata = self.data[nsample]
                mean = subdata['mean'][str(name)]
                sd_post = subdata['sd'][str(name)]
                nwarmup = 0
                for niter in range(len(self.data[0]['is_sample'])):
                    if not self.data[0]['is_sample'][niter]:
                        nwarmup += 1
                truevalue = self.data[0][str(name)][nsample+nwarmup-1]
                Z = abs(mean - truevalue)/sd_post
                S = 1. - (sd_post / sd_prior)**2
                listGraph[iName].SetPoint(nsample-1, S, Z)
            listGraph[iName].SetTitle("Z-score versus posterior shrinkage for {}".format(name))
            listGraph[iName].GetXaxis().SetTitle("Shrinkage")
            listGraph[iName].GetYaxis().SetTitle("Z-score")
            listGraph[iName].SetMarkerStyle(7)
            listGraph[iName].Draw("ap")

        self.rootcanvas.Save()
        return True



