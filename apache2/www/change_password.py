# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

import json
import potsbliz.config as config

def index(req):
    req.content_type = 'application/json; charset=UTF8'
    
    try:
        config.update_password(req.form.getfirst('oldpw'), req.form.getfirst('newpw'))
        return json.dumps({ 'Result': 'OK', 'Message': 'Password successfully changed' })
    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': str(e) })
