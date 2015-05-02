# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

# SIP IP User Part

import potsbliz.config as config
from potsbliz.logger import Logger
from potsbliz.up.sip.ipup import Ipup


if __name__ == '__main__':
    with Logger('SIP::__main__') as log:
        
        log.info('SIP IP userpart for POTSBLIZ started ...')

        sip_account = config.list_sip_accounts()[0]

        with Ipup(sip_account['identity'], sip_account['proxy'],
                  sip_account['password'], 5060,
                  '^[0-9][0-9#\*]+$'
                 ) as userpart:
            userpart.run()

        log.info('SIP userpart for POTSBLIZ terminated')
