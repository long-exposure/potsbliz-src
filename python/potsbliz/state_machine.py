# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

import dbus
import dbus.service
import time
import potsbliz.config as config
import potsbliz.speeddial as speeddial
import potsbliz.tone_generator as tone_generator
from enum import IntEnum
from potsbliz.logger import Logger
from potsbliz.userpart import UserPart
from potsbliz.ipup import Ipup
from potsbliz.btup import Btup
from pubsub import pub
from threading import Timer


EOD_TIMER = 5
SETTINGS_EXTENSION = '#'
State = IntEnum('State', 'IDLE RINGING TALK OFFHOOK COLLECTING')


class StateMachine(dbus.service.Object):
    
    def __init__(self):
        busName = dbus.service.BusName('net.longexposure.potsbliz', bus = dbus.SystemBus())
        dbus.service.Object.__init__(self, busName, '/StateMachine')


    def __enter__(self):
        with Logger(__name__ + '.__enter__'):
        
            self._state_event_log = Logger(__name__)
            self._set_state(State.IDLE)

            pub.subscribe(self.event_incoming_call, UserPart.TOPIC_INCOMING_CALL)
            pub.subscribe(self.event_terminate, UserPart.TOPIC_TERMINATE)

            self._asterisk = Ipup(pub,
                                  'sip:potsbliz@localhost:5065',
                                  'sip:localhost:5065',
                                  'potsbliz',
                                  5061)
            self._asterisk.__enter__()

            sip_account = config.list_sip_accounts()[0]
            self._sip = Ipup(pub,
                             sip_account['identity'],
                             sip_account['proxy'],
                             sip_account['password'])
            self._sip.__enter__()

            # wait for linphone init
            # playing dailtone or starting pulseaudio during linphone startup breaks
            #   soundcard setting for strange reasons!
            # make test with simultanuous dialtone and ringing!!!
            time.sleep(3)

            self._btup = Btup(pub)
            self._btup.__enter__()

            tone_generator.play_ok_tone()


    def __exit__(self, type, value, traceback):
        with Logger(__name__ + '.__exit__'):
            self._sip.__exit__(type, value, traceback)
            self._asterisk.__exit__(type, value, traceback)
            self._btup.__exit__(type, value, traceback)


    def _set_state(self, state):
        with Logger(__name__ + '._set_state'):
            self._state_event_log.info(state.name)
            self.StateChanged(state)
            self._state = state


    def event_incoming_call(self, sender):
        with Logger(__name__ + '.event_incoming_call'):
            if (self._state == State.IDLE):
                self._up = sender
                self._set_state(State.RINGING)
            else:
                sender.terminate_call()
    
    
    def event_terminate(self, sender):
        with Logger(__name__ + '.event_terminate'):
            self._up = None
            if (self._state == State.RINGING):
                self._set_state(State.IDLE)
            elif (self._state == State.TALK):
                tone_generator.start_dialtone()
                self._set_state(State.OFFHOOK)
    
    @dbus.service.method(dbus_interface='net.longexposure.potsbliz.statemachine', in_signature='', out_signature='')
    def Onhook(self):
        with Logger(__name__ + '.event_onhook'):
            if (self._state == State.OFFHOOK):
                tone_generator.stop_dialtone()
                self._set_state(State.IDLE)
            elif (self._state == State.COLLECTING):
                self._set_state(State.IDLE)
            elif (self._state == State.TALK):
                self._up.terminate_call()
                self._up = None
                self._set_state(State.IDLE)
    
    
    @dbus.service.method(dbus_interface='net.longexposure.potsbliz.statemachine', in_signature='', out_signature='')
    def Offhook(self):
        with Logger(__name__ + '.event_offhook'):
            if (self._state == State.IDLE):
                tone_generator.start_dialtone()
                self._set_state(State.OFFHOOK)
            elif (self._state == State.RINGING):
                self._up.answer_call()
                self._set_state(State.TALK)


    @dbus.service.method(dbus_interface='net.longexposure.potsbliz.statemachine', in_signature='s', out_signature='')
    def DigitDialed(self, digit):
        with Logger(__name__ + '.event_digit_dialed') as log:
            
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
                self._up.send_dtmf(digit)


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
                called_number = speeddial.convert(self._collected_digits)
                log.info('Make call to: ' + called_number)
                
                if (called_number == SETTINGS_EXTENSION):
                    self._up = self._asterisk
                    success = self._up.make_call('500')
                else:
                    # first we try it via bluetooth
                    self._up = self._btup
                    success = self._up.make_call(called_number)
                    if (success == False):
                        # then we try sip
                        self._up = self._sip
                        success = self._up.make_call(called_number)

                if (success == True):
                    self._set_state(State.TALK)
                else:
                    tone_generator.start_dialtone()
                    self._set_state(State.OFFHOOK)
