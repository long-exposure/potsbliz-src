# IPUP - IP User Part
# (C) 2014 - Norbert Huffschmid

import os
import time
import potsbliz.config as config
from subprocess import Popen, PIPE
from threading import Event, Thread
from potsbliz.logger import Logger

TOPIC_INCOMING_CALL = 'topic_incoming_call'
TOPIC_TERMINATE = 'topic_terminate'

SETTINGS_EXTENSION = '#'
LOCAL_SIP_PBX = 'localhost:5065'


class Ipup(object):
    
    def __init__(self, pub):
        with Logger(__name__ + '.__init__'):
            self._pub = pub


    def __enter__(self):
        with Logger(__name__ + '.__enter__'):
            
            if (os.path.exists('/.linphonerc')):
                os.remove('/.linphonerc')
            if (os.path.exists('/root/.linphonerc')):
                os.remove('/root/.linphonerc')
            self._linphonec = Popen('/usr/bin/linphonec', stdout=PIPE, stdin=PIPE)        

            self._worker_thread = Thread(target=self._linphone_worker)
            self._worker_thread.start()

    
    def __exit__(self, type, value, traceback):
        with Logger(__name__ + '.__exit__'):
            self._linphonec.stdin.write("quit\n")
            self._worker_thread.join()

    
    def make_call(self, called_number):
        with Logger(__name__ + '.make_call'):
            
            if (called_number == SETTINGS_EXTENSION):
                # call settings script on asterisk
                destination = "sip:500@%s" % (LOCAL_SIP_PBX)                
            else:
                # make call towards remote sip server
                sip_provider = config.get_value('sip_identity').split('@')[1]
                destination = 'sip:' + called_number + '@' + sip_provider

            self._linphonec.stdin.write('call ' + destination + '\n')
        
        
    def answer_call(self):
        with Logger(__name__ + '.answer_call'):
            self._linphonec.stdin.write('answer\n')
        
        
    def send_dtmf(self, digit):
        with Logger(__name__ + '.send_dtmf'):
            self._linphonec.stdin.write(digit + '\n')
        
        
    def terminate_call(self):
        with Logger(__name__ + '.terminate_call'):
            self._linphonec.stdin.write('terminate\n')


    def _linphone_worker(self):        
        with Logger(__name__ + '._linphone_worker') as log:

            # register with local asterisk PBX
            register_command = "register sip:potsbliz@%s sip:%s potsbliz\n" % (LOCAL_SIP_PBX, LOCAL_SIP_PBX)
            self._linphonec.stdin.write(register_command)
            self._linphonec.stdin.flush()
            time.sleep(1)
            
            # register at remote sip server
            # for some strange reasons linphonec does allow a second registration as above
            # (trying to do so forces an unregistration)
            # therefore we add a new proxy and register at it
            # (doing this twice doesn't work either, because linphone does not ask for the password the second time)
            # oh what a crap!
            sip_identity = config.get_value('sip_identity')
            sip_proxy = config.get_value('sip_proxy')
            sip_password = config.get_value('sip_password')
            
            self._linphonec.stdin.write("proxy add\n")
            self._linphonec.stdin.write("%s\n" % sip_proxy)
            self._linphonec.stdin.write("%s\n" % sip_identity)
            self._linphonec.stdin.write("yes\n") # yes, we want to register
            self._linphonec.stdin.write("\n")    # default expiration time
            self._linphonec.stdin.write("\n")    # no route to be specified
            self._linphonec.stdin.write("yes\n") # yes, we accept this configuration 
            self._linphonec.stdin.flush()
            time.sleep(2)                        # wait for password request
            self._linphonec.stdin.write("%s\n" % sip_password)
            self._linphonec.stdin.flush()

            while self._linphonec.poll() is None:
                
                message = self._linphonec.stdout.readline()
                log.info('Linphonec: ' + message)

                if (message.find('Receiving new incoming call') >= 0):
                    self._pub.sendMessage(TOPIC_INCOMING_CALL)

                if (message.find('Call terminated.') >= 0):
                    self._pub.sendMessage(TOPIC_TERMINATE)

                if (message.startswith('linphonec> Registration') and not message.endswith('successful.\n')):
                    log.error('Registration at remote sip server failed')
