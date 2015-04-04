#!/usr/bin/env python

# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

import dbus
import dbus.service
import gobject
import signal
from dbus.mainloop.glib import DBusGMainLoop
from potsbliz.logger import Logger
from potsbliz.state_machine import StateMachine

class Potsbliz(object):

    def run(self):
        with Logger(__name__ + '.run') as log:
            
            log.info('Starting POTSBLIZ ...')
            
            DBusGMainLoop(set_as_default=True)
            with StateMachine():

                self._loop = gobject.MainLoop()
                gobject.threads_init()

                # register for SIGTERM
                signal.signal(signal.SIGTERM, lambda signum, frame: self._loop.quit())

                self._loop.run()
                
                log.info('SIGTERM event received. Shutting down ...')


if __name__ == '__main__':
    
    app = Potsbliz()
    app.run()
