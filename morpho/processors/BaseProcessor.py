'''
Base processor for sampling-type operations
'''

from __future__ import absolute_import

from morpho.utilities import morphologging
logger=morphologging.getLogger(__name__)

import abc

__all__ = []
__all__.append(__name__)

class BaseProcessor(metaclass=abc.ABCMeta):
    '''
    Base Processor
    All Processors will be implemented in a child class where the
    specifics are encoded by overwriting Configure and Run.
    '''
    def __init__(self, name, *args, **kwargs):
        self._procName = name

    @property
    def name(self):
        return self._procName

    def Configure(self, params):
        '''
        This method will be called by nymph to configure the processor
        '''
        logger.info("Configure <{}>".format(self.name))
        if not self.InternalConfigure(params):
            logger.error("Error while configuring <{}>".format(self.name))
            return False
        return True

    @abc.abstractmethod
    def InternalConfigure(self, params):
        '''
        Method called by Configure() to set up the object. Must be
        overridden by child class.
        '''
        return

    def Run(self):
        '''
        This method will be called by nymph to run the processor
        '''
        logger.info("Run <{}>...".format(self.name))
        if not self.InternalRun():
            logger.error("Error while running <{}>".format(name))
            return False
        logger.info("Done with <{}>".format(self.name))
        return True

    @abc.abstractmethod
    def InternalRun(self):
        '''
        Method called by Run() to run the object. Must be
        overridden by child class.
        '''
        return


