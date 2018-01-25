from Axon.Component import *

from Logger import GetLoggerStdErr, GetFormatter
import logging, sys
reload(sys)
sys.setdefaultencoding("utf-8")

logger = GetLoggerStdErr('BaseProcessor', GetFormatter(),
                           stderr_lb=logging.WARNING,
                           propagate=False)

default_processor_config = {
    "name": "testProcessor",
    "queue_starter": True,
    "connections":
        {
            "slot": "default",
            "signal": ["type1","type2"]
        }
}

class BaseProcessor(component):
    
    '''    
    Definition of the BaseProcessor: all processors should inherit from this one
    This base processor class defines the connections from slots to methods and to signals
    Inbox = Slot
    Outbox = Signal
    '''
    Inboxes = []
    Outboxes = []
    def __init__(self,processor_config):

        logger.info("Initializing processor...")
        self._processor_config = processor_config
        self._name = self._processor_config['name']
        self._queue_starter = self._processor_config['queue_starter']
        self._activeSlots = self._getListActiveSlots()
        self._activeSignals = self._getListActiveSignals()
        self.Inboxes.extend(self._activeSlots) 
        self.Outboxes.extend(self._activeSignals) 
        logger.debug("Activating slots for {} <{}>: ".format(self._name,self.__class__.__name__) + str(self._activeSlots))
        logger.debug("Activating signals for {} <{}>: ".format(self._name,self.__class__.__name__) + str(self._activeSignals))
        super(BaseProcessor, self).__init__()
        logger.info("Initialization of {} done".format(self._name))

        logger.info("Configuring processor...")
        self.configure()
        logger.info("Configuration of {} done".format(self._name))

    def configure(self):
        '''
        Configure the processor by assigning all the parameters of the configuration dictionary as variables of the object
        '''
        for key, value in self._processor_config.iteritems():
            if key in  ["name", "queue_starter", "connections"]:
                continue
            setattr(self, "_" + key,value)

    def _getListActiveSlots(self):
        '''
        Get the list of slots to activate (from processor_config)
        '''
        listActiveSlots = self._processor_config['connections']['slot']
        if not isinstance(listActiveSlots,list):
            return [listActiveSlots]
        return listActiveSlots

    def _getListActiveSignals(self):
        '''
        Get the list of signals to activate (from processor_config)
        '''
        listActiveSignals = self._processor_config['connections']['signal']
        if not isinstance(listActiveSignals,list):
            return [listActiveSignals]
        return listActiveSignals

    def _getMethodFromSlotName(self,name):
        nameMethod = "slot_" + name
        logger.debug("Trying to get {}".format(nameMethod))
        try:
            function = getattr(self, nameMethod)
        except ImportError as e:
            import inspect
            listMethods = inspect.getmembers(self, predicate=inspect.ismethod)
            logger.error("Couldn't find {} among:")
            logger.error(listMethods)
        return function

    def _getMethodFromSignalName(self,name):
        # try:
        nameMethod = "signal_" + name
        logger.debug("Trying to get {}".format(nameMethod))
        try:
            function = getattr(self, nameMethod)
        except ImportError as e:
            import inspect
            listMethods = inspect.getmembers(self, predicate=inspect.ismethod)
            logger.error("Couldn't find {} among:")
            logger.error(listMethods)
        return function

    def _dataReadyOnSlots(self):
        # Look if data are ready on the configured slots
        isDataReady = False
        listInboxes = []
        for box in self._activeSlots.iteritems():
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
                print("isDataReady? " + str(isDataReady))
                # if isDataReady:
                yield 1
        logger.debug("About to send signal")
        for box in self._activeSignals:
            method = self._getMethodFromSignalName(box)
            self.send(method(listIntermediateObjects),box)
        # self.send("prout","signal")
        yield 1
                
        # while not self.dataReadyOnSlots("_input"):
        #     yield 1
        
class MyFirstProcessor(BaseProcessor):
    
    '''
    A new processor should be written to define all the slots/signals and associated methods within the class.
    Then during initialization of the object by the framework, 
    a dictionary/list of the slots to use and connect will be given (by the framework/user), 
    passed down to the BaseProcessor which will know which slots/signals to activate.
    '''
    
    def __init__(self,processor_config=default_processor_config):
        '''
        NB: this method should not be changed.
        Define the actual processor configuration e.g. connections between slots and signals the user is interested in.
        The _configure method in the base class will use this dictionary during configuration 
        (either in the init or in the main) ?
        The processor_config shall contain:
        - the name for the object/processor ("name")
        - a bool ("queue_starter") stating whether this processor is the first one from the chain (determined by the main executable/toolbox)        
        - list of slot to signals connections and the order
        - all the parameters required to configure/parametrize the processor for its execution
        An example of such dictionary is:
            name: "firstProcessor"
            queue_starter: True
            connections:
                - slot: input1
                  signal: output1
                - slot: input2
                  signal: output2
            processor_param1: 1
            processor_param2: [ "blue", "white", "red" ]
        '''
        super(MyFirstProcessor, self).__init__(processor_config)


    def slot_type1(self, input = {}):
        logger.debug("I am method 1")
        return "I am method 1"
         
    def signal_type1(self, input = {}):
        logger.debug("I am method 2")
        return "I am method 2"

    def signal_type2(self, input = {}):
        logger.warning('hello I am method 3')
        return "I am method 3"

class Consumer(component):
    Inboxes=["source"]
    Outboxes=["result"]
    def __init__(self):
        super(Consumer, self).__init__()
        self.count = 0
        self.i = 5
    def doSomething(self):
        if self.dataReady("source"):
            msg = self.recv("source")
            logger.debug(self.name +  " Woo " + str(msg))
            self.count = self.count +1
        if self.count >=2:
            self.send(self.count, "result")

    def main(self):
        yield 1
        while(self.i):
            self.i = self.i -1
            self.doSomething()
            yield 1

class testComponent(component):
    Inboxes=["_input"]
    Outboxes=[]
    def __init__(self):
        super(testComponent, self).__init__()
        prod_outboxes= ["result","result2"]
        self.producer = MyFirstProcessor()
        self.consumer = Consumer()
        # self.consumer2 = Consumer()
        # self.consumer3 = Consumer()
        # self.addChildren(self.producer, self.consumer)
        self.link((self.producer, "type3"), (self.consumer, "source"))
        self.link((self.producer, "type2"), (self.consumer, "source"))
        # self.link((self.consumer, "result"), (self.consumer3, "source"))
        # self.link((self.producer, "result2"), (self.consumer, "source"))
        self.link((self.consumer, "result"), (self, "_input"))
        self.addChildren(self.producer,self.consumer)

    def main(self):
        yield newComponent(*self.childComponents())
        while not self.dataReady("_input"):
            yield 1
        result = self.recv("_input")
        logger.info("Consumer finished with result: " +  str(result) +  "!")

p = testComponent()
p.activate()
scheduler.run.runThreads(slowmo=0)# context = r.runThreads()



# myFirstProcessor = MyFirstProcessor()
# myFirstProcessor.main()
# print(myFirstProcessor._getMethodFromSignalName("signal"))
# print(myFirstProcessor._getMethodFromSignalName("signal")())

# def getObjAsList(obj):
#     if not isinstance(obj,list):
#         return [obj]
#     else:
#         return obj
# print(getObjAsList(1))
# print(getObjAsList([1,2]))