# Generic user part
# Abstract base class for concrete user parts
# (C) 2015 - Norbert Huffschmid

from potsbliz.logger import Logger

INHERITANCE_ERROR = 'UserPart subclass implemented wrong! Subclasses have to implement this method!'

class UserPart(object):

    TOPIC_INCOMING_CALL = 'topic_incoming_call'
    TOPIC_TERMINATE = 'topic_terminate'    

    def __init__(self, pub):
        with Logger(__name__ + '.__init__'):
            self._pub = pub


    def __enter__(self):
        raise NotImplementedError(INHERITANCE_ERROR)

    
    def __exit__(self, type, value, traceback):
        raise NotImplementedError(INHERITANCE_ERROR)

    
    def make_call(self, called_number):
        raise NotImplementedError(INHERITANCE_ERROR)
        
        
    def answer_call(self):
        raise NotImplementedError(INHERITANCE_ERROR)
        
        
    def send_dtmf(self, digit):
        raise NotImplementedError(INHERITANCE_ERROR)
        
        
    def terminate_call(self):
        raise NotImplementedError(INHERITANCE_ERROR)