# Rotary Dial plugin for POTSBLIZ
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

import dbus.mainloop.glib
import gobject
import signal
from potsbliz.logger import Logger
from potsbliz.plugin.rotary.rotary import Anip


if __name__ == '__main__':
    with Logger('rotary::__main__') as log:
        
        log.info('Starting rotary dial plugin for POTSBLIZ ...')

        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    
        loop = gobject.MainLoop()
        gobject.threads_init()
        dbus.mainloop.glib.threads_init()
    
        # register for SIGTERM
        signal.signal(signal.SIGTERM, lambda signum, frame: loop.quit())
    
        with Anip():
            loop.run()
