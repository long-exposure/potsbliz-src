import json
import potsbliz.config as config


def list(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        return json.dumps({ 'Result': 'OK', 'Records': config.list_sip_settings() })
    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': str(e) })


def update(req):
    req.content_type = 'application/json; charset=UTF8'
    
    try:
        config.set_value(req.form.getfirst('config_key'), req.form.getfirst('config_value'))
        return json.dumps({ 'Result': 'OK' })
    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': str(e) })
