import json
import potsbliz.config as config

def index(req):
    req.content_type = 'application/json; charset=UTF8'
    
    try:
        config.update_password(req.form.getfirst('oldpw'), req.form.getfirst('newpw'))
        return json.dumps({ 'Result': 'OK', 'Message': 'Password successfully changed' })
    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': str(e) })
