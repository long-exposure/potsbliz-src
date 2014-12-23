import MySQLdb
from potsbliz.logger import Logger


def get_value(key):
    with Logger(__name__ + '.get_value') as log:
        conn = MySQLdb.connect(host="localhost", user="potsbliz", passwd="potsbliz", db="potsbliz")
        cursor = conn.cursor() 
        cursor.execute("SELECT config_value FROM config WHERE config_key='" + key + "';")
        result = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        log.debug('key: ' + key + ', value: ' + result)
        
        return result

    
def get_speeddial_numbers():
    with Logger(__name__ + '.get_speeddial_numbers') as log:
        conn = MySQLdb.connect(host="localhost", user="potsbliz", passwd="potsbliz", db="potsbliz")
        cursor = conn.cursor() 
        cursor.execute("SELECT shortcut, phonenumber FROM speeddial")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        
        log.debug('Speeddial numbers: ' + str(result))
        
        return result
