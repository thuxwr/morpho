from dungfly.Axon.Component import *

from ..Logger import GetLoggerStdErr, GetFormatter
import logging, sys
reload(sys)
sys.setdefaultencoding("utf-8")

logger = GetLoggerStdErr('BaseProcessor', GetFormatter(),
                           stderr_lb=logging.WARNING,
                           propagate=False)

class BaseProcessor(component):
    
    '''    
    Definition of the BaseProcessor: all processors should inherit from this one
    This base processor class defines the connections from slots to methods and to signals
    Inbox = Slot
    Outbox = Signal
    '''
    Inboxes = []
    Outboxes = []
    def __init__(self, name = "testProcessor",
                       queue_starter =True,
                       connections = {"slot": "default",
                                      "signal": ["type1","type2"]},
                       *args,**kwargs):

        logger.info("Initializing processor...")
        # if processor_config == {}:
        #     self._processor_config = default_processor_config
        # else:
        #     self._processor_config = processor_config
        self._name = name
        self._queue_starter = queue_starter
        self._connections = connections
        # print(name,queue_starter,connections,args,kwargs)

        self.Inboxes.extend(self._activeSlots) 
        self.Outboxes.extend(self._activeSignals) 
        logger.debug("Activating slots for {} <{}>: ".format(self._name,self.__class__.__name__) + str(self._activeSlots))
        logger.debug("Activating signals for {} <{}>: ".format(self._name,self.__class__.__name__) + str(self._activeSignals))
        super(BaseProcessor, self).__init__()
        logger.info("Initialization of {} done".format(self._name))

        logger.info("Configuring processor...")
        self.configure(**kwargs)
        logger.info("Configuration of {} done".format(self._name))

    def configure(self,config_dictionary={}):
        '''
        Configure the processor by assigning all the parameters of the configuration dictionary as variables of the object
        '''
        for key, value in config_dictionary.iteritems():
            if key in  ["name", "queue_starter", "connections"]:
                continue
            setattr(self, "_" + key,value)

    @property
    def _activeSlots(self):
        '''
        Get the list of slots to activate (from processor_config)
        '''
        listActiveSlots = self._connections['slot']
        if not isinstance(listActiveSlots,list):
            return [listActiveSlots]
        return listActiveSlots

    @property
    def _activeSignals(self):
        '''
        Get the list of signals to activate (from processor_config)
        '''
        listActiveSignals = self._connections['signal']
        if not isinstance(listActiveSignals,list):
            return [listActiveSignals]
        return listActiveSignals

    def _getMethodFromSlotName(self,name):
        nameMethod = "slot_" + name
        # logger.debug("Trying to get {}".format(nameMethod))
        try:
            function = getattr(self, nameMethod)
        except:
            logger.error("Couldn't find {}: using default".format(nameMethod))
            return self.default
        return function

    def _getMethodFromSignalName(self,name):
        # try:
        nameMethod = "signal_" + name
        # logger.debug("Trying to get {}".format(nameMethod))
        try:
            function = getattr(self, nameMethod)
        except :
            logger.error("Couldn't find {}: using default".format(nameMethod))
            return self.default
        return function

    def _dataReadyOnSlots(self):
        # Look if data are ready on the configured slots
        isDataReady = False
        listInboxes = []
        # print(self._activeSlots)
        for box in self._activeSlots:
            if self.dataReady(box):
                isDataReady = True
                listInboxes.append(box)
        return isDataReady, listInboxes

    def default(self, input = []):
        logger.warning("Using Default Method of BaseProcessor class")
        return input

    def main(self):
        listIntermediateObjects = {}
        if not self._queue_starter:
            keepLooping = True
            while keepLooping:
                isDataReady, listInboxes = self._dataReadyOnSlots()
                # print("isDataReady? " + str(isDataReady))
                if isDataReady:
                    keepLooping = False
                yield 1
        logger.debug("{}: About to send signal".format(self._name))
        for box in self._activeSignals:
            method = self._getMethodFromSignalName(box)
            self.send(method(listIntermediateObjects),box)
        yield 1
