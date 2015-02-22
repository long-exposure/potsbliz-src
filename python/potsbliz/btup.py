# BTUP - Bluetooth User Part
# (C) 2015 - Norbert Huffschmid

import dbus
import dbus.mainloop.glib
import os
import time
import potsbliz.config as config
from threading import Thread
from potsbliz.logger import Logger
from potsbliz.userpart import UserPart



_dbus2py = {
    dbus.String : str,
    dbus.UInt32 : int,
    dbus.Int32 : int,
    dbus.Int16 : int,
    dbus.UInt16 : int,
    dbus.UInt64 : int,
    dbus.Int64 : int,
    dbus.Byte : int,
    dbus.Boolean : bool,
    dbus.ByteArray : str,
    dbus.ObjectPath : str
    }

def dbus2py(d):
    t = type(d)
    if t in _dbus2py:
        return _dbus2py[t](d)
    if t is dbus.Dictionary:
        return dict([(dbus2py(k), dbus2py(v)) for k, v in d.items()])
    if t is dbus.Array and d.signature == "y":
        return "".join([chr(b) for b in d])
    if t is dbus.Array or t is list:
        return [dbus2py(v) for v in d]
    if t is dbus.Struct or t is tuple:
        return tuple([dbus2py(v) for v in d])
    return d

def pretty(d):
    d = dbus2py(d)
    t = type(d)

    if t in (dict, tuple, list) and len(d) > 0:
        if t is dict:
            d = ", ".join(["%s = %s" % (k, pretty(v))
                    for k, v in d.items()])
            return "{ %s }" % d

        d = " ".join([pretty(e) for e in d])

        if t is tuple:
            return "( %s )" % d

    if t is str:
        return "%s" % d

    return str(d)



class Btup(UserPart):

    def __enter__(self):
        with Logger(__name__ + '.__enter__'):

            self._bus = dbus.SystemBus()
            #self._ofono_manager = dbus.Interface(self._bus.get_object('org.ofono', '/'), 'org.ofono.Manager')

            '''
            self._bus.add_signal_receiver(self._property_changed, 
                                          bus_name="org.ofono", 
                                          signal_name = "PropertyChanged", 
                                          path_keyword="path", 
                                          interface_keyword="interface")
            '''
            self._bus.add_signal_receiver(self._call_added,
                                          bus_name="org.ofono",
                                          signal_name = 'CallAdded',
                                          member_keyword="member",
                                          path_keyword="path",
                                          interface_keyword="interface")

            self._bus.add_signal_receiver(self._call_removed,
                                          bus_name="org.ofono",
                                          signal_name = 'CallRemoved',
                                          member_keyword="member",
                                          path_keyword="path",
                                          interface_keyword="interface")


    def __exit__(self, type, value, traceback):
        with Logger(__name__ + '.__exit__'):
            pass
            #self._ofono_mainloop.quit()
            #self._worker_thread.join()


    def make_call(self, called_number):
        with Logger(__name__ + '.make_call') as log:
            #bus = dbus.SystemBus()
            ofono_manager = dbus.Interface(self._bus.get_object('org.ofono', '/'),
                                         'org.ofono.Manager')
            modems = ofono_manager.GetModems()
            modem_path = modems[0][0]
            log.debug("Connecting modem %s..." % modem_path)
            modem = dbus.Interface(self._bus.get_object('org.ofono', modem_path),
                                   'org.ofono.Modem')
            
            if (modem.GetProperties()['Powered'] == False):
                modem.SetProperty("Powered", dbus.Boolean(1), timeout = 120)
                time.sleep(1) # without delay call fails
            
            vcm = dbus.Interface(self._bus.get_object('org.ofono', modem_path),
                                 'org.ofono.VoiceCallManager')
            dial_path = vcm.Dial(called_number, "default")
            log.debug(dial_path)

        
    def answer_call(self):
        with Logger(__name__ + '.answer_call') as log:
            
            ofono_manager = dbus.Interface(self._bus.get_object('org.ofono', '/'),
                                           'org.ofono.Manager')
            modems = ofono_manager.GetModems()

            for path, properties in modems:
                log.debug("modem path: %s" % (path))
                if "org.ofono.VoiceCallManager" not in properties["Interfaces"]:
                    continue

                vcm = dbus.Interface(self._bus.get_object('org.ofono', path),
                                     'org.ofono.VoiceCallManager')
                calls = vcm.GetCalls()

                for path, properties in calls:
                    state = properties["State"]
                    log.debug("path: %s, state: %s" % (path, state))
                    if state != "incoming":
                        continue

                    call = dbus.Interface(self._bus.get_object('org.ofono', path),
                                          'org.ofono.VoiceCall')
                    call.Answer()


    def send_dtmf(self, digit):
        with Logger(__name__ + '.send_dtmf') as log:
            try:
                # TODO: analyze why POTSBLIZ terminates here sporadically

                ofono_manager = dbus.Interface(self._bus.get_object('org.ofono', '/'),
                                               'org.ofono.Manager')
                modems = ofono_manager.GetModems()
                modem_path = modems[0][0]
    
                vcm = dbus.Interface(self._bus.get_object('org.ofono', modem_path),
                                         'org.ofono.VoiceCallManager')
                vcm.SendTones(str(digit))
                
            except Exception as e:
                log.error(str(e))
        
        
    def terminate_call(self):
        with Logger(__name__ + '.terminate_call'):
            
            ofono_manager = dbus.Interface(self._bus.get_object('org.ofono', '/'),
                                           'org.ofono.Manager')
            modems = ofono_manager.GetModems()
            modem_path = modems[0][0]

            vcm = dbus.Interface(self._bus.get_object('org.ofono', modem_path),
                                     'org.ofono.VoiceCallManager')
            vcm.HangupAll()


    def _call_added(self, name, value, member, path, interface):
        with Logger(__name__ + '._call_added') as log:
            iface = interface[interface.rfind(".") + 1:]
            log.debug('value: ' + str(value))
            log.debug('state: ' + value['State'])
            log.debug("{%s} [%s] %s %s" % (iface, name, member, pretty(value)))
            if (value['State'] == 'incoming'):
                self._pub.sendMessage(UserPart.TOPIC_INCOMING_CALL, sender=self)


    def _call_removed(self, name, member, path, interface):
        with Logger(__name__ + '._call_removed') as log:
            iface = interface[interface.rfind(".") + 1:]
            log.debug("{%s} [%s] %s" % (iface, name, member))
            self._pub.sendMessage(UserPart.TOPIC_TERMINATE, sender=self)


    def _property_changed(self, name, value, path, interface): 
        with Logger(__name__ + '._property_changed') as log:
            iface = interface[interface.rfind(".") + 1:] 
            log.debug("{%s} [%s] %s = %s" % (iface, path, name, pretty(value)))
