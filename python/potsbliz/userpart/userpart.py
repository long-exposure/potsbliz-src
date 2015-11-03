# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

# Generic user part
# Abstract base class for concrete user parts

import dbus
import dbus.mainloop.glib
import dbus.service
import gobject
import signal
from potsbliz.logger import Logger

INHERITANCE_ERROR = 'UserPart subclass implemented wrong! Subclasses have to implement this method!'

class UserPart(dbus.service.Object):

    def __init__(self, service_name):
        with Logger(__name__ + '.__init__') as log:
            
            self._service_name = service_name
            
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            busName = dbus.service.BusName(service_name, bus = dbus.SystemBus())
            dbus.service.Object.__init__(self, busName, '/Userpart')
            
            self._is_registered = False


    def run(self):
        with Logger(__name__ + '.run'):
            
            loop = gobject.MainLoop()
            gobject.threads_init()
            dbus.mainloop.glib.threads_init()
        
            # register for SIGTERM
            signal.signal(signal.SIGTERM, lambda signum, frame: loop.quit())
            
            # start main loop
            loop.run()


    @dbus.service.method(dbus_interface='net.longexposure.potsbliz.userpart',
                         in_signature='s', out_signature='b')
    def CanCall(self, called_number):
        raise NotImplementedError(INHERITANCE_ERROR)


    @dbus.service.method(dbus_interface='net.longexposure.potsbliz.userpart',
                         in_signature='s', out_signature='')
    def MakeCall(self, called_number):
        raise NotImplementedError(INHERITANCE_ERROR)


    @dbus.service.method(dbus_interface='net.longexposure.potsbliz.userpart',
                         in_signature='', out_signature='')
    def TerminateCall(self):
        raise NotImplementedError(INHERITANCE_ERROR)


    @dbus.service.method(dbus_interface='net.longexposure.potsbliz.userpart',
                         in_signature='', out_signature='')
    def AnswerCall(self):
        raise NotImplementedError(INHERITANCE_ERROR)
        
        
    @dbus.service.method(dbus_interface='net.longexposure.potsbliz.userpart',
                         in_signature='s', out_signature='')
    def SendDtmf(self, digit):
        raise NotImplementedError(INHERITANCE_ERROR)

    @dbus.service.signal(dbus_interface='net.longexposure.potsbliz.userpart', signature='')
    def IncomingCall(self):
        with Logger(__name__ + '.IncomingCall'):
            pass


    @dbus.service.signal(dbus_interface='net.longexposure.potsbliz.userpart', signature='')
    def Release(self):
        with Logger(__name__ + '.Release'):
            pass


    @dbus.service.signal(dbus_interface='net.longexposure.potsbliz.userpart', signature='')
    def Busy(self):
        with Logger(__name__ + '.Busy'):
            pass


    def register(self):
        with Logger(__name__ + '.register'):
            if (self._is_registered == False):
                bus = dbus.SystemBus()
                state_machine = dbus.Interface(bus.get_object('net.longexposure.potsbliz', '/StateMachine'),
                                                              'net.longexposure.potsbliz.statemachine')
                state_machine.Register()
                self._is_registered = True


    def unregister(self):
        with Logger(__name__ + '.unregister'):
            if (self._is_registered == True):
                bus = dbus.SystemBus()
                state_machine = dbus.Interface(bus.get_object('net.longexposure.potsbliz', '/StateMachine'),
                                                              'net.longexposure.potsbliz.statemachine')
                state_machine.Unregister()
                self._is_registered = False
             