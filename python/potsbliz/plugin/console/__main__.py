#!/usr/bin/env python

# Console demo for POTSBLIZ
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

import argparse
import dbus
import dbus.mainloop.glib
import dbus.service
import gobject
import os
import potsbliz.state_machine
import re
from enum import IntEnum


def state_changed(state):
    print('State changed: ' + potsbliz.state_machine.State(state).name)
    

def show_error(msg, parser):
    print(msg)
    if (parser.parse_args().verbose):
        parser.print_help()


if __name__ == '__main__':

    # handle command line arguments
    parser = argparse.ArgumentParser(description='Execute a POTSBLIZ command.',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog='''
Example:
$ potsbliz offhook
$ potsbliz dial 08154711
$ potsbliz onhook''')
    parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true')
    parser.add_argument('command', help='POTSBLIZ command to execute', choices=['onhook', 'offhook', 'dial', 'dtmf', 'monitor'])
    parser.add_argument('arg', help='additional argument for <dial> or <dtmf> command', nargs='?')
    args = parser.parse_args()

    if (os.geteuid() != 0):
        exit('This program requires root privileges!') 
    
    # init dbus stuff
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    mainloop = gobject.MainLoop()
    gobject.threads_init()
    dbus.mainloop.glib.threads_init()
    bus = dbus.SystemBus()
    state_machine = dbus.Interface(bus.get_object('net.longexposure.potsbliz',
                                                  '/StateMachine'),
                                                  'net.longexposure.potsbliz.statemachine')
    # determine current POTSBLIZ state
    state = state_machine.GetState()

    if (args.verbose):
        print('State at begin: ' + potsbliz.state_machine.State(state).name)

    if (args.command == 'onhook'):
        state_machine.Onhook()
        
    elif (args.command == 'offhook'):
        state_machine.Offhook()
        
    elif (args.command == 'dial'):
        if (args.arg):
            match = re.match("^([0-9#*]+)$", args.arg)
            if (match):
                if (state == potsbliz.state_machine.State.IDLE):
                    state_machine.Offhook()
                for digit in match.group(1):
                    state_machine.DigitDialed(digit)
            else:
                show_error('Invalid dial command!', parser)
        else:
            show_error('Missing dial number argument!', parser)

    elif (args.command == 'dtmf'):
        if (args.arg):
            match = re.match("^([0-9#*]+)$", args.arg)
            if (match):
                if (state == potsbliz.state_machine.State.TALK):
                    for digit in match.group(1):
                        state_machine.DigitDialed(digit)
                else:
                    show_error('Invalid state for dtmf command!', parser)
            else:
                show_error('Invalid dtmf command!', parser)
        else:
            show_error('Missing dtmf digit(s) argument!', parser)

    elif (args.command == 'monitor'):
        try:
            state_machine.connect_to_signal('StateChanged', state_changed)
            print('Waiting for state changes (press CTRL-C to terminate) ...')
            mainloop.run()
        except (KeyboardInterrupt):
            print(' Goodbye!')

    state = state_machine.GetState()
    if (args.verbose):
        print('State at end: ' + potsbliz.state_machine.State(state).name)
