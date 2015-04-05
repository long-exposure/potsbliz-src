# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

# Generic user part
# Abstract base class for concrete user parts

from potsbliz.logger import Logger

INHERITANCE_ERROR = 'UserPart subclass implemented wrong! Subclasses have to implement this method!'

class UserPart(object):

    TOPIC_INCOMING_CALL = 'topic_incoming_call'
    TOPIC_TERMINATE = 'topic_terminate'    
    TOPIC_BUSY = 'topic_busy'    

    def __init__(self, pub):
        with Logger(__name__ + '.__init__'):
            self._pub = pub


    def start(self):
        raise NotImplementedError(INHERITANCE_ERROR)

    
    def stop(self):
        raise NotImplementedError(INHERITANCE_ERROR)

    
    def make_call(self, called_number):
        raise NotImplementedError(INHERITANCE_ERROR)
        # must return True in case of success and False otherwise
        
    def answer_call(self):
        raise NotImplementedError(INHERITANCE_ERROR)
        
        
    def send_dtmf(self, digit):
        raise NotImplementedError(INHERITANCE_ERROR)
        
        
    def terminate_call(self):
        raise NotImplementedError(INHERITANCE_ERROR)
