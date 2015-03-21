import dbus
import re

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
