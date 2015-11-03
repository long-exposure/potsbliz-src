# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

# Asterisk IP User Part

from time import sleep
from potsbliz.logger import Logger
from potsbliz.userpart.sip.ipup import Ipup


if __name__ == '__main__':
    with Logger('Asterisk::__main__') as log:
        
        log.info('Asterisk IP userpart for POTSBLIZ started ...')

        with Ipup('sip:potsbliz@localhost:5065', 'sip:localhost:5065',
                  'potsbliz', 5061,
                  '^#$' # Asterisk only deals with '#' (hookflash) number
                 ) as userpart:
            
            # wait for registration to be completed
            while (not userpart.CanCall('#')):
                sleep(1)
            
            # tell about IP address    
            userpart.MakeCall('#')
            
            userpart.run()

        log.info('Asterisk IP userpart for POTSBLIZ terminated')
