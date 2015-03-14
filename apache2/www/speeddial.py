import json
import potsbliz.config as config
import re


def list(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        return json.dumps({ 'Result': 'OK', 'Records': config.list_speeddial_numbers() })
    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': str(e) })


def create(req):
    req.content_type = 'application/json; charset=UTF8'
    
    try:
        _check_shortcut(req.form.getfirst('shortcut'))
        _check_phonenumber(req.form.getfirst('phonenumber'))
        entry = config.create_speeddial_number(req.form.getfirst('shortcut'),
                                               req.form.getfirst('phonenumber'),
                                               req.form.getfirst('comment'))
        return json.dumps({ 'Result': 'OK', 'Record': entry })
    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': str(e) })


def update(req):
    req.content_type = 'application/json; charset=UTF8'
    
    try:
        _check_phonenumber(req.form.getfirst('phonenumber'))
        config.update_speeddial_number(req.form.getfirst('id'),
                                       req.form.getfirst('phonenumber'),
                                       req.form.getfirst('comment'))
        return json.dumps({ 'Result': 'OK' })
    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': str(e) })


def delete(req):
    req.content_type = 'application/json; charset=UTF8'
    
    try:
        config.delete_speeddial_number(req.form.getfirst('id'))
        return json.dumps({ 'Result': 'OK' })
    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': str(e) })


def _check_shortcut(shortcut):
    if (re.match("^[0-9#\*]{1,3}$", shortcut) == None):
        raise Exception('Invalid speed dial number')

    for number in config.list_speeddial_numbers():
        if (number['shortcut'] == shortcut):
            raise Exception('Speed dial number already exists!')


def _check_phonenumber(phonenumber):
    if (re.match("^[0-9#\*\-\/]{1,20}$", phonenumber) == None):
        raise Exception('Invalid phone number')
