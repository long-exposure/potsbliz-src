# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

import json
import potsbliz.config as config

def list(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        return json.dumps({ 'Result': 'OK', 'Records': config.list_sip_accounts() })
    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': str(e) })


def update(req):
    req.content_type = 'application/json; charset=UTF8'
    
    try:
        config.update_sip_account(req.form.getfirst('id'),
                                  req.form.getfirst('identity'),
                                  req.form.getfirst('proxy'),
                                  req.form.getfirst('password'))
        return json.dumps({ 'Result': 'OK' })
    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': str(e) })
