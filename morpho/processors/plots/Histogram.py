'''
Plot an histogram of the variables of interest
Authors: M. Guigue
Date: 06/26/18
'''

from __future__ import absolute_import

from morpho.utilities import morphologging, reader
from morpho.processors import BaseProcessor
from . import RootCanvas, RootHistogram
logger = morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)


class Histogram(BaseProcessor):
    '''
    Processor that generates a canvas and a histogram and saves it.
    TODO:
    - Add the possibility to plot several histograms with the same binning on the same canvas
    - Generalize this processor so it understands if if should be a 1D or a 2D histogram

    Parameters:
        n_bins_x: number of bins (default=100)
        range: range of x (list)
        variables (required): name(s) of the variable in the data
        width: window width (default=600)
        height: window height (default=400)
        title: canvas title
        x_title: title of the x axis
        y_title: title of the y axis
        options: other options (logy, logx)
        output_path: where to save the plot
        output_pformat: plot format (default=pdf)

    Input:
        data: dictionary containing model input data

    Results:
        None
    '''

    def InternalConfigure(self, params):
        '''
        Configure
        '''
        # Initialize Canvas
        self.rootcanvas = RootCanvas.RootCanvas(params, optStat=0)
        self.histo = RootHistogram.RootHistogram(params, optStat=0)

        # Read other parameters
        self.namedata = reader.read_param(params, 'variables', "required")
        return True

    def InternalRun(self):
        self.histo.Fill(self.data.get(self.namedata))
        self.rootcanvas.cd()
        self.histo.Draw("hist")
        self.rootcanvas.Save()
        return True
