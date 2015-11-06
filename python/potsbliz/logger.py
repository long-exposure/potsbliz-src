# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

import logging.handlers


class Logger(object):

    def __init__(self, name):
        self.__name = name
        self.__log = logging.getLogger(name + '_logger')
        if (self.__log.handlers == []):
            # avoid multiple adding of handlers
            
            # common logging handler
            logHandler = logging.handlers.SysLogHandler(address = '/dev/log')
            self.__log.addHandler(logHandler)
            
            #persistent error notebook
            errorLogHandler = logging.FileHandler('/var/log/potsbliz-error.log')
            errorLogHandler.setLevel(logging.ERROR)
            frm = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", 
                                    "%d.%m.%Y %H:%M:%S") 
            errorLogHandler.setFormatter(frm)
            self.__log.addHandler(errorLogHandler)

        self.__log.setLevel(logging.DEBUG)


    def __enter__(self):
        self.__log.debug(self.__name + ': Enter')
        return self

    
    def __exit__(self, type, value, traceback):
        if (value != None):
            self.__log.error(self.__name + ": " + str(value))
        self.__log.debug(self.__name + ': Exit')
        return False

        
    def debug(self, message):
        self.__log.debug(self.__name + ": " + message)

        
    def info(self, message):
        self.__log.info(self.__name + ": " + message)

        
    def warning(self, message):
        self.__log.warning(self.__name + ": " + message)

        
    def error(self, message):
        self.__log.error(self.__name + ": " + message)
