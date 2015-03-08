import dbus
import json
from mod_python import apache

def list(req):
    req.content_type = 'application/json; charset=UTF8'

    rows = []
    bus = dbus.SystemBus()
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
                              'paired': properties['Paired'] })

    return json.dumps({ 'Result': 'OK', 'Records': rows })


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
