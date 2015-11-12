# Console demo plugin for POTSBLIZ
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

import dbus
import dbus.service
import dbus.mainloop.glib
import gobject
import potsbliz.state_machine
import re
import sys
from enum import IntEnum
from threading import Thread


def console_worker():
    
    global mainloop, state_machine       
    
    while True:
        print('Enter on of these commands: onhook | offhook | dial <number> | dtmf <digit> | quit')
        cmd = raw_input("> ")
        
        if (cmd == 'onhook'):
            state_machine.Onhook()
            
        elif (cmd == 'offhook'):
            state_machine.Offhook()
          
        elif (cmd.startswith('dial')):
            match = re.match("^dial ([0-9#*]+)$", cmd)
            if (match):
                if (state_machine.GetState() == potsbliz.state_machine.State.IDLE):
                    state_machine.Offhook()
                    
                for digit in match.group(1):
                    state_machine.DigitDialed(digit)
                    #print('Send digit ' + digit)
            else:
                print('Invalid dial command!')

        elif (cmd.startswith('dtmf')):
            match = re.match("^dtmf ([0-9#*])$", cmd)
            if (match):
                if (state_machine.GetState() == potsbliz.state_machine.State.TALK):
                    state_machine.DigitDialed(match.group(1))
                else:
                    print('Invalid state for dtmf command!')
            else:
                print('Invalid dtmf command!')

        elif (cmd == 'quit'):
            break
        
        else:
            print('Invalid command!')
        
    # we're done
    mainloop.quit()


def state_changed(state):
    # notify user about internal potsbliz state change
    print('State changed: ' + str(potsbliz.state_machine.State(state))[6:])
    sys.stdout.write('> ')
    sys.stdout.flush()
    

if __name__ == '__main__':

        # init dbus stuff and register for notification of state change events
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        mainloop = gobject.MainLoop()
        gobject.threads_init()
        dbus.mainloop.glib.threads_init()
        bus = dbus.SystemBus()
        state_machine = dbus.Interface(bus.get_object('net.longexposure.potsbliz', '/StateMachine'), 'net.longexposure.potsbliz.statemachine')
        state_machine.connect_to_signal('StateChanged', state_changed)

        # start thread for console input/output
        Thread(target=console_worker).start()
        
        # enter main loop and wait until <quit> command is entered on console
        mainloop.run()
        
        print('Goodbye!')
