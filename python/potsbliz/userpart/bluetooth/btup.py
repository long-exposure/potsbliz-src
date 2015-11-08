# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

# BTUP - Bluetooth User Part

import dbus
import subprocess
import re
import sys
import time
from threading import Thread
from potsbliz.logger import Logger
from potsbliz.userpart.userpart import UserPart


class Btup(UserPart):

    def __init__(self):
        
        with Logger(__name__ + '.__init__') as log:
            super(Btup, self).__init__('net.longexposure.potsbliz.btup') # call base class constructor


    def __enter__(self):
        with Logger(__name__ + '.__enter__'):

            self._bus = dbus.SystemBus()

            subprocess.Popen(["pulseaudio", "-D"])

            self._bus.add_signal_receiver(self._property_changed, 
                                          bus_name="org.ofono", 
                                          signal_name = "PropertyChanged", 
                                          path_keyword="path", 
                                          interface_keyword="interface")

            self._bus.add_signal_receiver(self._call_added, 
                                          bus_name="org.ofono", 
                                          signal_name = "CallAdded")

            self._bus.add_signal_receiver(self._call_removed, 
                                          bus_name="org.ofono", 
                                          signal_name = "CallRemoved")

            self._update_registration()
            
            return self


    def __exit__(self, type, value, traceback):
        with Logger(__name__ + '.__exit__'):
            subprocess.Popen(["pulseaudio", "--kill"])
            self.unregister()


    def CanCall(self, called_number):
        with Logger(__name__ + '.CanCall'):
            return (re.match('^[0-9][0-9#\*]+$', called_number) != None)

    
    def MakeCall(self, called_number):
        with Logger(__name__ + '.MakeCall') as log:

            ofono_manager = dbus.Interface(self._bus.get_object('org.ofono', '/'),
                                         'org.ofono.Manager')
            modems = ofono_manager.GetModems()
            for path, properties in modems:
                log.debug('modem path: %s' % (path))
                if ('org.ofono.VoiceCallManager' not in properties['Interfaces']):
                    continue                
                if (properties['Online'] == False):
                    continue
                
                vcm = dbus.Interface(self._bus.get_object('org.ofono', path),
                                     'org.ofono.VoiceCallManager')
                dial_path = vcm.Dial(called_number, 'default')
                log.debug(dial_path)
                return
            
            raise Exception('No active modem found')


    def AnswerCall(self):
        with Logger(__name__ + '.AnswerCall') as log:
            
            ofono_manager = dbus.Interface(self._bus.get_object('org.ofono', '/'),
                                           'org.ofono.Manager')
            modems = ofono_manager.GetModems()

            for path, properties in modems:
                log.debug('modem path: %s' % (path))
                if ('org.ofono.VoiceCallManager' not in properties['Interfaces']):
                    continue

                vcm = dbus.Interface(self._bus.get_object('org.ofono', path),
                                     'org.ofono.VoiceCallManager')
                calls = vcm.GetCalls()

                for path, properties in calls:
                    state = properties['State']
                    log.debug('path: %s, state: %s' % (path, state))
                    if state != 'incoming':
                        continue

                    call = dbus.Interface(self._bus.get_object('org.ofono', path),
                                          'org.ofono.VoiceCall')
                    call.Answer()


    def SendDtmf(self, digit):
        with Logger(__name__ + '.SendDtmf') as log:

            log.debug('Dbus: Get ofono manager')
            ofono_manager = dbus.Interface(self._bus.get_object('org.ofono', '/'),
                                           'org.ofono.Manager')
            log.debug('Dbus: Get modem path')
            modems = ofono_manager.GetModems()

            # find modem with active call
            # why is SendTones a method of VoiceCallManager and not VoiceCall???
            for path, properties in modems:
                log.debug('modem path: %s' % (path))
                if ('org.ofono.VoiceCallManager' not in properties['Interfaces']):
                    continue

                vcm = dbus.Interface(self._bus.get_object('org.ofono', path),
                                     'org.ofono.VoiceCallManager')
                calls = vcm.GetCalls()

                for path, properties in calls:
                    state = properties['State']
                    log.debug('path: %s, state: %s' % (path, state))
                    if state != 'active':
                        continue

                    log.debug('Dbus: Send tone ...')
                    vcm.SendTones(str(digit))
                    log.debug('Dbus: Tone sent.')
            

    def TerminateCall(self):
        with Logger(__name__ + '.TerminateCall') as log:
            
            ofono_manager = dbus.Interface(self._bus.get_object('org.ofono', '/'),
                                           'org.ofono.Manager')
            modems = ofono_manager.GetModems()

            for path, properties in modems:
                log.debug('modem path: %s' % (path))
                if ('org.ofono.VoiceCallManager' not in properties['Interfaces']):
                    continue

                vcm = dbus.Interface(self._bus.get_object('org.ofono', path),
                                     'org.ofono.VoiceCallManager')
                calls = vcm.GetCalls()

                for path, properties in calls:
                    call = dbus.Interface(self._bus.get_object('org.ofono', path),
                                          'org.ofono.VoiceCall')
                    call.Hangup()


    def _update_registration(self):        
        with Logger(__name__ + '._update_registration') as log:
            
            ofono_manager = dbus.Interface(self._bus.get_object('org.ofono', '/'),
                                           'org.ofono.Manager')
            modems = ofono_manager.GetModems()
            for path, properties in modems:
                if ('org.ofono.VoiceCallManager' not in properties['Interfaces']):
                    continue                
                if (properties['Online'] == False):
                    continue
                # at least one modem is online, ==> register
                self.register()
                return
            
            # no online modem found, ==> unregister
            self.unregister()


    def _property_changed(self, name, value, path, interface): 
        with Logger(__name__ + '._property_changed') as log:
            log.debug("{%s} [%s] %s" % (interface, name, str(value),))
            if ((interface == 'org.ofono.Modem') and (name == 'Online')):
                if (value == 1):
                    # if we invoke update_registration here, often no online modem is found!?!
                    self.register()
                else:
                    self._update_registration()


    def _call_added(self, name, value): 
        with Logger(__name__ + '._call_added'):
            if (value['State'] == 'incoming'):
                self.IncomingCall()

                
    def _call_removed(self, name): 
        with Logger(__name__ + '._call_removed'):
            self.Release()
