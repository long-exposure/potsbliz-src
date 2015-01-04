#!/usr/bin/env python

import time
import potsbliz.speeddial as speeddial
from potsbliz.logger import Logger
from potsbliz.userpart import UserPart
from potsbliz.ipup import Ipup
from potsbliz.anip import Anip
from pubsub import pub
from threading import Timer


EOD_TIMER = 5


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

            self._ipup = Ipup(pub)
            self._ipup.__enter__()

            # wait for linphone init
            # playing dailtone during linphone startup breaks soundcard setting for strange reasons!
            # make test with simultanuous dialtone and ringing!!!
            time.sleep(3)

            self._anip = Anip(pub)
            self._anip.__enter__()
            
            self._anip.play_ok_tone()


    def __exit__(self, type, value, traceback):
        with Logger(__name__ + '.__exit__'):
            self._ipup.__exit__(type, value, traceback)
            self._anip.__exit__(type, value, traceback)


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


    def event_incoming_call(self):
        with Logger(__name__ + '.event_incoming_call'):
            if (self._state == State.IDLE):
                self._anip.ring_bell()
                self._set_state(State.RINGING)
            elif (self._state == State.OFFHOOK):
                self._ipup.terminate_call()
            elif (self._state == State.COLLECTING):
                self._ipup.terminate_call()
    
    
    def event_terminate(self):
        with Logger(__name__ + '.event_terminate'):
            if (self._state == State.RINGING):
                self._anip.stop_bell()
                self._set_state(State.IDLE)
            elif (self._state == State.TALK):
                self._anip.start_dialtone()
                self._set_state(State.OFFHOOK)
    
    
    def event_onhook(self):
        with Logger(__name__ + '.event_onhook'):
            if (self._state == State.OFFHOOK):
                self._anip.stop_dialtone()
                self._set_state(State.IDLE)
            elif (self._state == State.COLLECTING):
                self._set_state(State.IDLE)
            elif (self._state == State.TALK):
                self._ipup.terminate_call()
                self._set_state(State.IDLE)
    
    
    def event_offhook(self):
        with Logger(__name__ + '.event_offhook'):
            if (self._state == State.IDLE):
                self._anip.start_dialtone()
                self._set_state(State.OFFHOOK)
            elif (self._state == State.RINGING):
                self._anip.stop_bell()
                self._ipup.answer_call()
                self._set_state(State.TALK)


    def event_digit_dialed(self, digit):
        with Logger(__name__ + '.event_digit_dialed') as log:
            
            log.info('Dialed digit: ' + digit)
            
            if (self._state == State.OFFHOOK):
                self._anip.stop_dialtone()
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
                self._ipup.send_dtmf(digit)


    def _end_of_dialing(self):
        with Logger(__name__ + '._end_of_dialing') as log:
            if (self._state == State.COLLECTING):
                called_number = speeddial.convert(self._collected_digits)
                log.info('Make call to: ' + called_number)
                
                self._ipup.make_call(called_number)

                self._set_state(State.TALK)
