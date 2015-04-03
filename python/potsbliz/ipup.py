# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

# IPUP - IP User Part

import time
from subprocess import Popen, PIPE
from threading import Thread
from potsbliz.logger import Logger
from potsbliz.userpart import UserPart


class Ipup(UserPart):
    
    def __init__(self, pub, identity, proxy, password, port=5060):
        with Logger(__name__ + '.__init__'):
            super(Ipup, self).__init__(pub) # call base class constructor
            self._identity = identity
            self._proxy = proxy
            self._password = password
            self._port = port
            
        
    def start(self):
        with Logger(__name__ + '.start'):

            # write linphonec config file
            config_file = '/var/tmp/.linphonerc-' + self._identity
            with open(config_file, 'w') as file:
                file.write("[sip]\n")
                file.write("sip_port=%d\n" % self._port)

            self._linphonec = Popen(['/usr/bin/linphonec', '-c' , config_file],
                                    stdout=PIPE, stdin=PIPE)        

            self._worker_thread = Thread(target=self._linphone_worker)
            self._worker_thread.start()

    
    def stop(self):
        with Logger(__name__ + '.stop'):
            self._linphonec.stdin.write("quit\n")
            self._worker_thread.join()

    
    def make_call(self, called_number):
        with Logger(__name__ + '.make_call'):
            sip_provider = self._identity.split('@')[1]
            destination = 'sip:' + called_number + '@' + sip_provider
            self._linphonec.stdin.write('call ' + destination + '\n')
            return True
        
        
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

            register_command = "register %s %s %s\n" % (self._identity, self._proxy, self._password)
            self._linphonec.stdin.write(register_command)
            self._linphonec.stdin.flush()
            
            while self._linphonec.poll() is None:
                
                message = self._linphonec.stdout.readline()
                log.info('Linphonec: ' + message)

                if (message.find('Receiving new incoming call') >= 0):
                    self._pub.sendMessage(UserPart.TOPIC_INCOMING_CALL, sender=self)

                if (message.find('Call terminated.') >= 0):
                    self._pub.sendMessage(UserPart.TOPIC_TERMINATE, sender=self)

                # TODO: handle user busy!
                if (message.endswith('error.\n')):
                    self._pub.sendMessage(UserPart.TOPIC_TERMINATE, sender=self)

                if (message.startswith('linphonec> Registration') and not message.endswith('successful.\n')):
                    log.error('Registration at remote sip server failed')
