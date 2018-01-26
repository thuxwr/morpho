from dungfly.Processor import BaseProcessor

import logging, sys
reload(sys)
sys.setdefaultencoding("utf-8")

from dungfly.Logger import GetLoggerStdErr, GetFormatter
logger = GetLoggerStdErr('BaseProcessor', GetFormatter(),
                           stderr_lb=logging.WARNING,
                           propagate=False)

class Printer(BaseProcessor):
    
    '''
    '''
    
    def __init__(self,*args,**kwargs):
        super(Printer, self).__init__(*args,**kwargs)

    def signal_printed_text(self,input):
        logger.debug(self.name +  " Woo " + str(msg))
        return output