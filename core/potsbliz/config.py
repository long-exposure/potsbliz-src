# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

import MySQLdb
import MySQLdb.cursors

def list_speeddial_numbers():
    try:
        with MySQLdb.connect(host="localhost", user="potsbliz",
                             passwd="potsbliz", db="potsbliz",
                             cursorclass=MySQLdb.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM speeddial")
            return cursor.fetchall()
    except Exception, e:
        raise Exception('Cannot read speeddial numbers: ' + str(e))


def create_speeddial_number(shortcut, phonenumber, comment):
    try:
        with MySQLdb.connect(host="localhost", user="potsbliz",
                             passwd="potsbliz", db="potsbliz",
                             cursorclass=MySQLdb.cursors.DictCursor) as cursor:
            cursor.execute("INSERT INTO speeddial SET shortcut = '" + shortcut +
                           "', phonenumber = '" + phonenumber +
                           "', comment = '" +
                           MySQLdb.escape_string(comment) + "'")
            cursor.execute("SELECT * FROM speeddial WHERE id = " + str(cursor.lastrowid))
            return cursor.fetchone()
    except Exception, e:
        raise Exception('Cannot create speeddial number: ' + str(e))


def update_speeddial_number(id, phonenumber, comment):
    try:
        with MySQLdb.connect(host="localhost", user="potsbliz",
                             passwd="potsbliz", db="potsbliz") as cursor:
            cursor.execute("UPDATE speeddial SET phonenumber = '" + phonenumber +
                           "', comment = '" + MySQLdb.escape_string(comment) +
                           "' WHERE id = '" + id + "'")
    except Exception, e:
        raise Exception('Cannot update speeddial number: ' + str(e))


def delete_speeddial_number(id):
    try:
        with MySQLdb.connect(host="localhost", user="potsbliz",
                             passwd="potsbliz", db="potsbliz") as cursor:
            cursor.execute("DELETE FROM speeddial WHERE id = " + id)
    except Exception, e:
        raise Exception('Cannot delete speeddial number: ' + str(e))


def update_password(oldpw, newpw):
    try:
        with MySQLdb.connect(host="localhost", user="potsbliz",
                             passwd="potsbliz", db="potsbliz") as cursor:
            cursor.execute("UPDATE mysql_auth SET passwd = MD5('" + newpw +
                           "') WHERE username = 'admin' AND passwd = MD5('" + oldpw + "')")
            if (cursor.rowcount != 1):
                 raise Exception('Old password is wrong!')
    except Exception, e:
        raise Exception('Cannot update password: ' + str(e))


def list_sip_accounts():
    try:
        with MySQLdb.connect(host="localhost", user="potsbliz",
                             passwd="potsbliz", db="potsbliz",
                             cursorclass=MySQLdb.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM sip")
            return cursor.fetchall()
    except Exception, e:
        raise Exception('Cannot read sip data: ' + str(e))
