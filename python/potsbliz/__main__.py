#!/usr/bin/env python

#import dbus
#import dbus.mainloop.glib
from dbus.mainloop.glib import DBusGMainLoop
import gobject

import signal
import sys
import time
#from gi.repository import GLib
from threading import Event
from potsbliz.logger import Logger
from potsbliz.state_machine import StateMachine


class Potsbliz(object):

    def run(self):
        with Logger(__name__ + '.run') as log:
            
            gobject.threads_init()
            DBusGMainLoop(set_as_default=True)
            #dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

            with StateMachine():
                '''
                # register for SIGTERM
                self._sigterm_event = Event()
                signal.signal(signal.SIGTERM, lambda signum, frame: self._sigterm_event.set())
                # only presence of timeout allows SIGTERM event to be received!
                self._sigterm_event.wait(sys.maxint)
                
                log.info('SIGTERM event received. Shutting down ...')
                '''
                
                # register for SIGTERM
                signal.signal(signal.SIGTERM, lambda signum, frame: self._mainloop.quit())

                #self._mainloop = GLib.MainLoop()
                self._mainloop = gobject.MainLoop()
                #GLib.threads_init()
                log.debug('Run mainloop ...')
                self._mainloop.run() 
                log.debug('Mainloop terminated.')


if __name__ == '__main__':
    
    app = Potsbliz()
    app.run()
