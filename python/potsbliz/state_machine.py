#!/usr/bin/env python

import time
import potsbliz.config as config
import potsbliz.speeddial as speeddial
import potsbliz.tone_generator as tone_generator
from potsbliz.logger import Logger
from potsbliz.userpart import UserPart
from potsbliz.ipup import Ipup
from potsbliz.btup import Btup
from potsbliz.anip import Anip
from pubsub import pub
from threading import Timer


EOD_TIMER = 5
SETTINGS_EXTENSION = '#'


class State:
    IDLE = 1
    RINGING = 2
    TALK = 3
    OFFHOOK = 4
    COLLECTING = 5


class StateMachine(object):
    
    def __enter__(self):
        with Logger(__name__ + '.__enter__'):
        
            self._state_event_log = Logger(__name__)
            self._set_state(State.IDLE)

            pub.subscribe(self.event_incoming_call, UserPart.TOPIC_INCOMING_CALL)
            pub.subscribe(self.event_terminate, UserPart.TOPIC_TERMINATE)
            pub.subscribe(self.event_offhook, Anip.TOPIC_OFFHOOK)
            pub.subscribe(self.event_onhook, Anip.TOPIC_ONHOOK)
            pub.subscribe(self.event_digit_dialed, Anip.TOPIC_DIGIT_DIALED)

            self._asterisk = Ipup(pub,
                                  'sip:potsbliz@localhost:5065',
                                  'sip:localhost:5065',
                                  'potsbliz',
                                  5061)
            self._asterisk.__enter__()

            self._sip = Ipup(pub,
                             config.get_value('sip_identity'),
                             config.get_value('sip_proxy'),
                             config.get_value('sip_password'))
            self._sip.__enter__()

            # wait for linphone init
            # playing dailtone or starting pulseaudio during linphone startup breaks
            #   soundcard setting for strange reasons!
            # make test with simultanuous dialtone and ringing!!!
            time.sleep(3)

            self._btup = Btup(pub)
            self._btup.__enter__()

            self._anip = Anip(pub)
            self._anip.__enter__()
            
            self._anip.ring_bell()
            tone_generator.play_ok_tone()
            self._anip.stop_bell()


    def __exit__(self, type, value, traceback):
        with Logger(__name__ + '.__exit__'):
            self._sip.__exit__(type, value, traceback)
            self._asterisk.__exit__(type, value, traceback)
            self._btup.__exit__(type, value, traceback)
            self._anip.__exit__(type, value, traceback)
            tone_generator.stop_dialtone()


    def _set_state(self, state):
        if (state == State.IDLE):
            self._state_event_log.info('New state: IDLE')
        elif (state == State.RINGING):
            self._state_event_log.info('New state: RINGING')
        elif (state == State.TALK):
            self._state_event_log.info('New state: TALK')
        elif (state == State.OFFHOOK):
            self._state_event_log.info('New state: OFFHOOK')
        elif (state == State.COLLECTING):
            self._state_event_log.info('New state: COLLECTING')
        else:
            raise ValueError('Invalid state for state machine')

        self._state = state


    def event_incoming_call(self, sender):
        with Logger(__name__ + '.event_incoming_call'):
            if (self._state == State.IDLE):
                self._anip.ring_bell()
                self._up = sender
                self._set_state(State.RINGING)
            else:
                sender.terminate_call()
    
    
    def event_terminate(self, sender):
        with Logger(__name__ + '.event_terminate'):
            self._up = None
            if (self._state == State.RINGING):
                self._anip.stop_bell()
                self._set_state(State.IDLE)
            elif (self._state == State.TALK):
                tone_generator.start_dialtone()
                self._set_state(State.OFFHOOK)
    
    
    def event_onhook(self):
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
    
    
    def event_offhook(self):
        with Logger(__name__ + '.event_offhook'):
            if (self._state == State.IDLE):
                tone_generator.start_dialtone()
                self._set_state(State.OFFHOOK)
            elif (self._state == State.RINGING):
                self._anip.stop_bell()
                self._up.answer_call()
                self._set_state(State.TALK)


    def event_digit_dialed(self, digit):
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


    def _end_of_dialing(self):
        with Logger(__name__ + '._end_of_dialing') as log:
            if (self._state == State.COLLECTING):
                called_number = speeddial.convert(self._collected_digits)
                log.info('Make call to: ' + called_number)
                
                if (called_number == SETTINGS_EXTENSION):
                    self._up = self._asterisk
                    self._up.make_call('500')
                else:
                    self._up = self._sip
                    self._up.make_call(called_number)
                    
                # TODO: consider making call through btup
                
                self._set_state(State.TALK)
