import dbus
import json
from mod_python import apache

def list(req):
    req.content_type = 'application/json; charset=UTF8'

    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object('org.ofono', '/'), 'org.ofono.Manager')
    modems = manager.GetModems()

    rows = []
    for path, properties in modems:
        rows.append({ 'modemname': path, 'name': properties['Name'], 'online': properties['Online'] })

    result = { "Result": "OK", "Records": rows }
    
    return json.dumps(result)


def delete(req):
    result = { "Result": "OK" }    
    return json.dumps(result)
