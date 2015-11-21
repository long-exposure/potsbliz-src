# Rotary Dial plugin for POTSBLIZ
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

import dbus
import dbus.service
import RPi.GPIO as GPIO
import time
from dbus.exceptions import DBusException
from datetime import datetime
from threading import Thread, Timer
from potsbliz.logger import Logger
from potsbliz.state_machine import State as State

GPIO_CHANNEL_HOOK = 8
GPIO_CHANNEL_DIALER = 10
GPIO_CHANNEL_GROUND_KEY = 12
GPIO_CHANNEL_LED_1 = 18
GPIO_CHANNEL_LED_2 = 22

ROTATION_TIMER = 0.3
HOOKFLASH_DOWN_TIMER = 0.5
HOOKFLASH_UP_TIMER = 0.5


class Anip(object):
    """ANIP - Analog subscriber at the IP network"""
    
    TOPIC_ONHOOK = 'topic_onhook'
    TOPIC_OFFHOOK = 'topic_offhook'
    TOPIC_DIGIT_DIALED = 'topic_digit_dialed'
    
    _is_ringing = False
    

    def __init__(self):
        with Logger(__name__ + '.__init__') as log:
            bus = dbus.SystemBus()

            # in case that POTSBLIZ is not yet ready to connect we are patient ... 
            trial_counter = 5
            while (True):
                try:
                    self._state_machine = dbus.Interface(bus.get_object('net.longexposure.potsbliz', '/StateMachine'),
                                                         'net.longexposure.potsbliz.statemachine')
                    self._state_machine.connect_to_signal('StateChanged', self.state_changed)
                    log.info('Successfully connected to POTSBLIZ')
                    break; # connection established
                except DBusException, e:
                    log.warning(str(e))
                    time.sleep(1)
                    trial_counter -= 1
                    if (trial_counter == 0):
                        raise Exception('Cannot connect to POTSBLIZ!')


    def __enter__(self):
        with Logger(__name__ + '.__enter__'):
            
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(GPIO_CHANNEL_HOOK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(GPIO_CHANNEL_DIALER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(GPIO_CHANNEL_GROUND_KEY, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(GPIO_CHANNEL_HOOK, GPIO.BOTH, bouncetime=50)
            GPIO.add_event_detect(GPIO_CHANNEL_DIALER, GPIO.RISING, bouncetime=80)
            GPIO.add_event_detect(GPIO_CHANNEL_GROUND_KEY, GPIO.BOTH, bouncetime=20)
            time.sleep(1) # inhibits sporadic immediate triggering of ground_key callback (no idea why)
            GPIO.add_event_callback(GPIO_CHANNEL_HOOK, self._hook)
            GPIO.add_event_callback(GPIO_CHANNEL_DIALER, self._dialpulse)
            GPIO.add_event_callback(GPIO_CHANNEL_GROUND_KEY, self._ground_key)
            GPIO.setup(GPIO_CHANNEL_LED_1, GPIO.OUT)
            GPIO.setup(GPIO_CHANNEL_LED_2, GPIO.OUT)
            
            self._pulse_counter = 0
            self._hookflash_counter = 0
            
            self._rotation_timer = Timer(ROTATION_TIMER, self._end_of_rotation)
            self._hookflash_down_timer = Timer(HOOKFLASH_DOWN_TIMER, self._hookflash_down_timeout)
            self._hookflash_up_timer = Timer(HOOKFLASH_UP_TIMER, self._hookflash_up_timeout)
            
            if (not GPIO.input(GPIO_CHANNEL_HOOK)):
                self._hook(GPIO_CHANNEL_HOOK)
                

    def __exit__(self, type, value, traceback):
        with Logger(__name__ + '.__exit__'):
            self._stop_bell()


    def state_changed(self, state):
        with Logger(__name__ + '.state_changed'):
            if (state == State.RINGING):
                self._ring_bell()
            else:
                self._stop_bell()
    
    
    def _ring_bell(self):
        with Logger(__name__ + '._ring_bell'):
            # no bell there, turn on leds if available 
            self._is_ringing = True
            self._worker_thread = Thread(target=self._ring_worker)
            self._worker_thread.start()


    def _stop_bell(self):
        with Logger(__name__ + '._stop_bell'):
            # no bell there, turn off leds if available 
            self._is_ringing = False


    def _hook(self, channel):
        with Logger(__name__ + '._hook'):
            if (GPIO.input(channel) == 0):
                self._offhook()
            else:    
                self._onhook()


    def _dialpulse(self, channel):
        # logging skipped due to performance reasons
        self._pulse_counter += 1
        self._rotation_timer.cancel()
        self._rotation_timer = Timer(ROTATION_TIMER, self._end_of_rotation)
        self._rotation_timer.start()


    def _ground_key(self, channel):
        with Logger(__name__ + '._ground_key') as log:

            if (GPIO.input(channel) == 0):
                log.debug('Ground key pressed.')
                self._onhook()
            else:
                log.debug('Ground key released.')
                self._offhook()


    def _onhook(self):
        with Logger(__name__ + '._onhook') as log:
            self._hookflash_counter += 1
            self._rotation_timer.cancel()
            self._hookflash_down_timer.cancel()
            log.debug('Starting hookflash_down timer ...')
            self._hookflash_down_timer = Timer(HOOKFLASH_DOWN_TIMER, self._hookflash_down_timeout)
            self._hookflash_down_timer.start()


    def _offhook(self):
        with Logger(__name__ + '._offhook') as log:
            try:
                if (self._hookflash_counter == 0):
                    self._state_machine.Offhook()
                    self._pulse_counter = 0
                else:
                    self._hookflash_down_timer.cancel()
                    self._hookflash_up_timer.cancel()
                    log.debug('Starting hookflash_up timer ...')
                    self._hookflash_up_timer = Timer(HOOKFLASH_UP_TIMER, self._hookflash_up_timeout)
                    self._hookflash_up_timer.start()
            except DBusException, e:
                log.warning(str(e))
                
    
    def _end_of_rotation(self):
        with Logger(__name__ + '._end_of_rotation') as log:
            try:
                if (self._pulse_counter == 10):
                    self._pulse_counter = 0 # 10 -> 0
    
                self._state_machine.DigitDialed(str(self._pulse_counter))
    
                self._pulse_counter = 0
            except DBusException, e:
                log.warning(str(e))


    def _hookflash_down_timeout(self):
        with Logger(__name__ + '._hookflash_down_timeout') as log:        
            try:
                self._hookflash_up_timer.cancel()
                self._hookflash_counter = 0
                
                self._state_machine.Onhook()
            except DBusException, e:
                log.warning(str(e))


    def _hookflash_up_timeout(self):
        with Logger(__name__ + '._hookflash_up_timeout') as log:        
            try:
                log.debug(str(self._hookflash_counter) + ' hookflashs detected')
                
                if (self._hookflash_counter == 1):
                    self._state_machine.DigitDialed('#')
                elif (self._hookflash_counter == 2):
                    self._state_machine.DigitDialed('*')
                else:
                    log.debug('Hookflashs ignored')
                    
                self._hookflash_counter = 0
            except DBusException, e:
                log.warning(str(e))


    def _ring_worker(self):        
        with Logger(__name__ + '._ring_worker') as log:
            while (self._is_ringing):
                # toggle leds
                GPIO.output(GPIO_CHANNEL_LED_1, True) 
                GPIO.output(GPIO_CHANNEL_LED_2, False) 
                time.sleep(0.25)
                GPIO.output(GPIO_CHANNEL_LED_1, False) 
                GPIO.output(GPIO_CHANNEL_LED_2, True) 
                time.sleep(0.25)
            GPIO.output(GPIO_CHANNEL_LED_2, False)
