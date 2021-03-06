# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

import dbus
import dbus.mainloop.glib
import dbus.service
import gobject
import json
import re
from potsbliz.state_machine import State as State


def onhook(req):
    
    bus = dbus.SystemBus()
    state_machine = dbus.Interface(bus.get_object('net.longexposure.potsbliz', '/StateMachine'),
                                                  'net.longexposure.potsbliz.statemachine')
    state_machine.Onhook()


def offhook(req):
    
    bus = dbus.SystemBus()
    state_machine = dbus.Interface(bus.get_object('net.longexposure.potsbliz', '/StateMachine'),
                                                  'net.longexposure.potsbliz.statemachine')
    state_machine.Offhook()


def dialed_digits(req): 

    bus = dbus.SystemBus()
    state_machine = dbus.Interface(bus.get_object('net.longexposure.potsbliz', '/StateMachine'),
                                                  'net.longexposure.potsbliz.statemachine')
    for digit in req.form.getfirst('digits'):
        if (re.match("^[0-9#\*]$", digit) != None): # check for allowed digits
            state_machine.DigitDialed(digit)


def get_state(req): 

    try:
        
        req.content_type = 'application/json; charset=UTF8'
    
        bus = dbus.SystemBus()
        state_machine = dbus.Interface(bus.get_object('net.longexposure.potsbliz', '/StateMachine'),
                                                      'net.longexposure.potsbliz.statemachine')
        state = State(state_machine.GetState())
        
        return json.dumps({ 'State': state.name })
    
    except Exception, e:
        return json.dumps({ 'Error': str(e) })


def longpoll_state(req):
    
    req.content_type = 'application/json; charset=UTF8'

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    loop = gobject.MainLoop()
    gobject.threads_init()
    dbus.mainloop.glib.threads_init()

    bus = dbus.SystemBus()
    state_machine = dbus.Interface(bus.get_object('net.longexposure.potsbliz', '/StateMachine'),
                                                  'net.longexposure.potsbliz.statemachine')
    state_machine.connect_to_signal('StateChanged', lambda state: loop.quit())
    loop.run()

    # TODO: How to reuse signal info here???
    state = State(state_machine.GetState())
    
    return json.dumps({ 'State': state.name })
