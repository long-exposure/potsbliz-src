#!/usr/bin/env python

import signal
import sys
import time
from threading import Event
from potsbliz.logger import Logger
from potsbliz.state_machine import StateMachine


class Potsbliz(object):

    def run(self):
        with Logger(__name__ + '.run') as log:
            
            with StateMachine():
                
                # register for SIGTERM
                self._sigterm_event = Event()
                signal.signal(signal.SIGTERM, lambda signum, frame: self._sigterm_event.set())
                # only presence of timeout allows SIGTERM event to be received!
                self._sigterm_event.wait(sys.maxint)
                
                log.info('SIGTERM event received. Shutting down ...')


if __name__ == '__main__':
    
    app = Potsbliz()
    app.run()
