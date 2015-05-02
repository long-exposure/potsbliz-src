# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

import dbus
import dbus.service
import subprocess
import time
import potsbliz.speeddial as speeddial
import potsbliz.tone_generator as tone_generator
from enum import IntEnum
from potsbliz.logger import Logger
from threading import Timer


EOD_TIMER = 5
#SETTINGS_EXTENSION = '#'
State = IntEnum('State', 'IDLE RINGING TALK OFFHOOK COLLECTING BUSY')


class StateMachine(dbus.service.Object):
    
    def __init__(self):
        with Logger(__name__ + '.__init__'):
        
            self._userparts = []
            
            busName = dbus.service.BusName('net.longexposure.potsbliz', bus = dbus.SystemBus())
            dbus.service.Object.__init__(self, busName, '/StateMachine')


    def __enter__(self):
        with Logger(__name__ + '.__enter__'):
        
            self._state_event_log = Logger(__name__)
            self._set_state(State.IDLE)

            tone_generator.play_ok_tone()


    def __exit__(self, type, value, traceback):
        with Logger(__name__ + '.__exit__'):
            pass


    def _set_state(self, state):
        with Logger(__name__ + '._set_state'):
            self._state_event_log.info(state.name)
            self.StateChanged(state)
            self._state = state


    def event_incoming_call(self, sender):
        with Logger(__name__ + '.event_incoming_call'):
            if (self._state == State.IDLE):
                self._up = dbus.Interface(dbus.SystemBus().get_object(sender, '/Userpart'),
                                          'net.longexposure.potsbliz.userpart')
                self._set_state(State.RINGING)
            else:
                sender.TerminateCall()
    
    
    def event_release(self, sender):
        with Logger(__name__ + '.event_release'):
            self._up = None
            if (self._state == State.RINGING):
                self._set_state(State.IDLE)
            elif (self._state == State.TALK):
                tone_generator.start_dialtone()
                self._set_state(State.OFFHOOK)

    
    def event_busy(self, sender):
        with Logger(__name__ + '.event_busy'):
            if (self._state == State.TALK):
                self._up = None
                tone_generator.start_busytone()
                self._set_state(State.BUSY)

    
    @dbus.service.method(dbus_interface='net.longexposure.potsbliz.statemachine',
                         in_signature='', out_signature='',
                         sender_keyword='sender')
    def Register(self, sender=None):
        with Logger(__name__ + '.Register') as log:
            if (sender != None):
                log.debug('Registering ' + sender)
                
                if (sender not in self._userparts):
                    # add sender to list of registered userparts            
                    self._userparts.append(sender)
                    bus = dbus.SystemBus()
                    userpart = dbus.Interface(bus.get_object(sender, '/Userpart'),
                                                             'net.longexposure.potsbliz.userpart')
                    userpart.connect_to_signal('IncomingCall', self.event_incoming_call, sender_keyword='sender')
                    userpart.connect_to_signal('Release', self.event_release, sender_keyword='sender')
                    userpart.connect_to_signal('Busy', self.event_busy, sender_keyword='sender')

                log.debug('Registered userparts: ' + str(len(self._userparts)))


    @dbus.service.method(dbus_interface='net.longexposure.potsbliz.statemachine',
                         in_signature='', out_signature='',
                         sender_keyword='sender')
    def Unregister(self, sender=None):
        with Logger(__name__ + '.Unregister') as log:
            if (sender != None):
                log.debug('Unregistering ' + sender)
                
                if (sender in self._userparts):
                    # remove sender from list of registered userparts            
                    self._userparts.remove(sender)

                log.debug('Registered userparts: ' + str(len(self._userparts)))


    @dbus.service.method(dbus_interface='net.longexposure.potsbliz.statemachine', in_signature='', out_signature='')
    def Onhook(self):
        with Logger(__name__ + '.Onhook') as log:
            try:
                if (self._state == State.OFFHOOK):
                    tone_generator.stop_dialtone()
                elif (self._state == State.BUSY):
                    tone_generator.stop_busytone()
                elif (self._state == State.TALK):
                    self._up.TerminateCall()
            except Exception, e:
                log.error(str(e))
                
            self._up = None
            self._set_state(State.IDLE)
    
    
    @dbus.service.method(dbus_interface='net.longexposure.potsbliz.statemachine', in_signature='', out_signature='')
    def Offhook(self):
        with Logger(__name__ + '.Offhook'):
            if (self._state == State.IDLE):
                tone_generator.start_dialtone()
                self._set_state(State.OFFHOOK)
            elif (self._state == State.RINGING):
                self._up.AnswerCall()
                self._set_state(State.TALK)


    @dbus.service.method(dbus_interface='net.longexposure.potsbliz.statemachine', in_signature='s', out_signature='')
    def DigitDialed(self, digit):
        with Logger(__name__ + '.DigitDialed') as log:
            
            log.info('Dialed digit: ' + digit)
            
            if (self._state == State.OFFHOOK):
                tone_generator.stop_dialtone()
                self._collected_digits = digit
                self._eod_timer = Timer(EOD_TIMER, self._end_of_dialing)
                self._eod_timer.start()
                self._set_state(State.COLLECTING)
            elif (self._state == State.COLLECTING):
                self._eod_timer.cancel()
                if (digit == '#'):
                    # end od dialing explicitely requested, e.g. via flash key
                    self._end_of_dialing()
                else:
                    # add digit to collection and wait
                    self._collected_digits += digit
                    self._eod_timer = Timer(EOD_TIMER, self._end_of_dialing)
                    self._eod_timer.start()
            elif (self._state == State.TALK):
                log.info('Send DTMF digit: ' + digit)
                self._up.SendDtmf(digit)


    @dbus.service.method(dbus_interface='net.longexposure.potsbliz.statemachine', in_signature='', out_signature='i')
    def GetState(self):
        with Logger(__name__ + '.GetState'):
            return self._state


    @dbus.service.signal(dbus_interface='net.longexposure.potsbliz.statemachine', signature='i')
    def StateChanged(self, state):
        with Logger(__name__ + '.StateChanged'):
            pass


    def _end_of_dialing(self):
        with Logger(__name__ + '._end_of_dialing') as log:
            if (self._state == State.COLLECTING):
                try:
                    called_number = speeddial.convert(self._collected_digits)
                    
                    for registered_userpart in self._userparts:
                        userpart = dbus.Interface(dbus.SystemBus().get_object(registered_userpart, '/Userpart'),
                                                  'net.longexposure.potsbliz.userpart')
                        if (userpart.CanCall(called_number)):
                            self._up = userpart
                            log.info('Make call to: %s' % called_number)
                            userpart.MakeCall(called_number)
                            self._set_state(State.TALK)
                            return
                        
                    raise Exception('No userpart found for number ' + called_number)
                
                except Exception:
                    tone_generator.start_dialtone()
                    self._set_state(State.OFFHOOK)
