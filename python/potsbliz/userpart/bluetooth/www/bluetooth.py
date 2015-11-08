# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

import dbus
import json
from mod_python import apache

def list(req):
    
    req.content_type = 'application/json; charset=UTF8'

    try:
        
        rows = []
        bus = dbus.SystemBus()

        ofono_manager = dbus.Interface(bus.get_object('org.ofono', '/'), 'org.ofono.Manager')
        modems = ofono_manager.GetModems()
        strength = 0
        for path, properties in modems:
            if ('org.ofono.NetworkRegistration' not in properties['Interfaces']):
                continue                
            if (properties['Online'] == False):
                continue
            nr = dbus.Interface(bus.get_object('org.ofono', path), 'org.ofono.NetworkRegistration')
            #nr_properties = nr.GetProperties()
            strength = nr.GetProperties()['Strength']

        manager = dbus.Interface(bus.get_object('org.bluez', '/'), 'org.freedesktop.DBus.ObjectManager')
        objects = manager.GetManagedObjects()
        for path in objects.keys():
            interfaces = objects[path]
            for interface in interfaces.keys():
                if (interface == 'org.bluez.Device1'):
                    properties = interfaces[interface]
                    rows.append({ 'device': path,
                                  'name': properties['Name'],
                                  'connected': properties['Connected'],
                                  'paired': properties['Paired'],
                                  'strength': int(strength) })
    
        return json.dumps({ 'Result': 'OK', 'Records': rows })
    
    except Exception, e:
        return json.dumps({ 'Result': 'Error', 'Message': str(e) })


def delete(req):
    req.content_type = 'application/json; charset=UTF8'
    
    # read POST parameter
    device = req.form.getfirst('device')

    bus = dbus.SystemBus()
    adapter = dbus.Interface(bus.get_object('org.bluez', '/org/bluez/hci0'), 'org.bluez.Adapter1')
    adapter.RemoveDevice(device)

    return json.dumps({ "Result": "OK" })


def start_discovery(req):
    bus = dbus.SystemBus()
    adapter = dbus.Interface(bus.get_object('org.bluez', '/org/bluez/hci0'), 'org.bluez.Adapter1')
    adapter.StartDiscovery()


def stop_discovery(req):
    bus = dbus.SystemBus()
    adapter = dbus.Interface(bus.get_object('org.bluez', '/org/bluez/hci0'), 'org.bluez.Adapter1')
    adapter.StopDiscovery()
    
    
def get_discoverable_timeout (req):
    req.content_type = 'application/json; charset=UTF8'

    bus = dbus.SystemBus()
    adapter = dbus.Interface(bus.get_object('org.bluez', '/org/bluez/hci0'), 'org.freedesktop.DBus.Properties')
    timeout = adapter.Get('org.bluez.Adapter1', 'DiscoverableTimeout')
    return json.dumps({ "DiscoverableTimeout": timeout })


def pair(req):
    req.content_type = 'application/json; charset=UTF8'
    
    # read POST parameter
    device_id = req.form.getfirst('device')

    bus = dbus.SystemBus()
    device = dbus.Interface(bus.get_object('org.bluez', device_id), 'org.bluez.Device1')
    device.Pair()
    properties_manager = dbus.Interface(device, 'org.freedesktop.DBus.Properties')
    properties_manager.Set('org.bluez.Device1', 'Trusted', True)
    device.Connect()
    
    return json.dumps({ "Result": "OK" })
    
    
def connect(req):
    req.content_type = 'application/json; charset=UTF8'
    
    # read POST parameter
    device_id = req.form.getfirst('device')

    bus = dbus.SystemBus()
    device = dbus.Interface(bus.get_object('org.bluez', device_id), 'org.bluez.Device1')
    
    try:
        device.Connect()
        return json.dumps({ 'Result': 'OK' })
    
    except dbus.DBusException, e:
        return json.dumps({ 'Result': 'Error', 'Message': str(e) })
    
    
def disconnect(req):
    req.content_type = 'application/json; charset=UTF8'
    
    # read POST parameter
    device_id = req.form.getfirst('device')

    bus = dbus.SystemBus()
    device = dbus.Interface(bus.get_object('org.bluez', device_id), 'org.bluez.Device1')
    device.Disconnect()
    
    return json.dumps({ "Result": "OK" })
