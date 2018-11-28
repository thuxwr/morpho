'''
Extract correlation matrix for interested parameters from stan result.
Authors: W. Xu
Date: 11/26/2018
'''

from __future__ import absolute_import
import math

from morpho.utilities import morphologging, reader, pystanLoader
from morpho.processors import BaseProcessor
logger = morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)

class correlation(BaseProcessor):
    '''
    Analysis processor to calculate the correlation matrix for interested parameters.

    Parameters:
        interestParams (required): interested parameters
        isOutput : False for no output. True by default.

    Input:
        data: dictionary containing stan output

    Results:
        results: list containing correlation matrix
    '''

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    def InternalConfigure(self, param_dict):
        self.namedata = reader.read_param(param_dict, 'interestParams', "required")
        self.isOutput = reader.read_param(param_dict, 'isOutput', True)
        return True

    def InternalRun(self):

        mean = []
        meanmean = []
        sd = []
        for iName, name1 in enumerate(self.namedata):
            subdata1 = self.data[str(name1)]
            is_sample = self.data["is_sample"]
            onedimsum = 0
            isample = 0
            for iValue, value in enumerate(subdata1):
                if is_sample[iValue]:
                    onedimsum += value
                    isample += 1
            mean.append(float(onedimsum)/isample)
            meanmean.append([])
            # Calculate E(xy).
            for jName, name2 in enumerate(self.namedata):
                subdata2 = self.data[str(name2)]
                twodimsum = 0
                for iValue in range(len(subdata2)):
                    if is_sample[iValue]:
                        twodimsum += subdata1[iValue]*subdata2[iValue]
                meanmean[iName].append(float(twodimsum)/isample)

            sd.append(math.sqrt(meanmean[iName][iName] - mean[iName]**2))
        
        # Calculate correlation matrix.
        correlation = []
        for iName in range(len(mean)):
            correlation.append([])
            for jName in range(len(mean)):
                rho = (meanmean[iName][jName]-mean[iName]*mean[jName])/sd[iName]/sd[jName]
                correlation[iName].append(rho)
        logger.debug("Correlation matrix calculated successfully for interested parameters.")
        if self.isOutput:
            print("{:10}".format(""), end='')
            for iName, name in enumerate(self.namedata):
                print("{:10}".format(name), end='')
            print("")

            for iName, name1 in enumerate(self.namedata):
                print("{:10}".format(name1), end='')
                for jName, name2 in enumerate(self.namedata):
                    print("{:10}".format("%.4f"%correlation[iName][jName]), end='')
                print('')

        return correlation






                






