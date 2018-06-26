'''
'''

from __future__ import absolute_import

import csv
import os

from morpho.utilities import morphologging
logger=morphologging.getLogger(__name__)

from morpho.processors.IO import IOProcessor

__all__ = []
__all__.append(__name__)

class IOCVSProcessor(IOProcessor):
    '''
    Base IO CVS Processor
    The CVS Reader and Writer
    '''

    # def Configure(self, params):
    #     super().Configure(params)

    def Reader(self):
        logger.debug("Reading {}".format(self.file_name))
        if os.path.exists(self.file_name):
            with open(self.file_name, 'r') as csv_file:
                try:
                    reader = csv.reader(csv_file)
                    theData = dict(reader)
                except:
                    logger.error("Error while reading {}".format(self.file_name))
                    raise
        else:
            logger.error("File {} does not exist".format(self.file_name))
            raise FileNotFoundError(self.file_name)

        logger.debug("Extracting {}".format(self.variables))
        for var in self.variables:
            if var in theData.keys():
                self.data.update({str(var):theData[var]})
            else:
                logger.error("Variable {} does not exist in {}".format(self.variables,self.file_name))
        return True


    def Writer(self):

        logger.debug("Saving data in {}".format(self.file_name))
        rdir = os.path.dirname(self.file_name)
        if rdir != '' and not os.path.exists(rdir):
            os.makedirs(rdir)
            logger.debug("Creating folder: {}".format(rdir))
        with open(self.file_name, 'w') as csv_file:
            try:
                writer = csv.writer(csv_file)
                for key in self.variables:
                    writer.writerow([key, self.data[key]])
            except:
                logger.error("Error while writing {}".format(self.file_name))
                raise
        logger.debug("File saved!")
        return True

