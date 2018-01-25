from Axon.Component import *
import BaseProcessor

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