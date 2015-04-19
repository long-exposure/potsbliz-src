# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

# BTUP - Bluetooth User Part

from potsbliz.logger import Logger
from potsbliz.up.bluetooth.btup import Btup


if __name__ == '__main__':
    with Logger('Bluetooth::__main__') as log:
        
        log.info('Bluetooth userpart for POTSBLIZ started ...')

        with Btup() as userpart:
            userpart.run()
        
        log.info('Bluetooth userpart for POTSBLIZ terminated')
