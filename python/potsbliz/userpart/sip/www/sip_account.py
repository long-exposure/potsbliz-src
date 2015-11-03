# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

import json
import MySQLdb
import MySQLdb.cursors
import potsbliz.config as config

def list(req):
    req.content_type = 'application/json; charset=UTF8'

    try:
        
        with MySQLdb.connect(host="localhost", user="potsbliz",
                             passwd="potsbliz", db="potsbliz",
                             cursorclass=MySQLdb.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM sip")
            accounts = cursor.fetchall()

        return json.dumps({ 'Result': 'OK', 'Records': accounts })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'Cannot read sip data: ' + str(e) })


def update(req):
    req.content_type = 'application/json; charset=UTF8'
    
    try:
        
        with MySQLdb.connect(host="localhost", user="potsbliz",
                             passwd="potsbliz", db="potsbliz") as cursor:
            cursor.execute("UPDATE sip SET identity = '" + req.form.getfirst('identity') +
                           "', proxy = '" + req.form.getfirst('proxy') +
                           "', password = '" + req.form.getfirst('password') +
                           "' WHERE id = '" + req.form.getfirst('id') + "'")

        return json.dumps({ 'Result': 'OK' })

    except Exception, e:
        return json.dumps({ 'Result': 'ERROR', 'Message': 'Cannot update sip account: ' + str(e) })
