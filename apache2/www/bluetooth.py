import dbus
import json
from mod_python import apache

def list(req):
    req.content_type = 'application/json; charset=UTF8'

    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object('org.bluez', '/'), 'org.freedesktop.DBus.ObjectManager')
    objects = manager.GetManagedObjects()

    rows = []
    for path in objects.keys():
        interfaces = objects[path]
        for interface in interfaces.keys():
            if (interface == 'org.bluez.Device1'):
                properties = interfaces[interface]
                rows.append({ 'modemname': path, 'name': properties['Name'], 'connected': properties['Connected'] })

    return json.dumps({ "Result": "OK", "Records": rows })


def delete(req):
    result = { "Result": "OK" }    
    return json.dumps(result)
