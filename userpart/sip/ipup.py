# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

# IPUP - IP User Part

import re
import sys
from subprocess import Popen, PIPE
from threading import Thread
from potsbliz.logger import Logger
from potsbliz.userpart.userpart import UserPart


class Ipup(UserPart):
    
    def __init__(self, identity, proxy, password, port=5060, call_pattern='.*'):
        
        with Logger(__name__ + '.__init__') as log:
            super(Ipup, self).__init__('net.longexposure.potsbliz.ipup.port' + str(port)) # call base class constructor
            self._identity = identity
            self._proxy = proxy
            self._password = password
            self._port = port
            self._call_pattern = call_pattern
            
        
    def __enter__(self):
        with Logger(__name__ + '.__enter__'):

            # write linphonec config file
            config_file = '/var/tmp/.linphonerc-' + self._identity
            with open(config_file, 'w') as file:
                file.write("[sip]\n")
                file.write("sip_port=%d\n" % self._port)

            self._linphonec = Popen(['/usr/bin/linphonec', '-c' , config_file],
                                    stdout=PIPE, stdin=PIPE)        

            self._worker_thread = Thread(target=self._linphone_worker)
            self._worker_thread.start()
            
            return self

    
    def __exit__(self, type, value, traceback):
        with Logger(__name__ + '.__exit__'):
            self._linphonec.stdin.write("quit\n")
            self._worker_thread.join()

    
    def CanCall(self, called_number):
        with Logger(__name__ + '.CanCall'):
            return (re.match(self._call_pattern, called_number) != None)
        
        
    def MakeCall(self, called_number):
        with Logger(__name__ + '.MakeCall'):
            sip_provider = self._identity.split('@')[1]
            destination = 'sip:' + called_number + '@' + sip_provider
            self._linphonec.stdin.write('call ' + destination + '\n')
        
        
    def AnswerCall(self):
        with Logger(__name__ + '.AnswerCall'):
            self._linphonec.stdin.write('answer\n')
        
        
    def SendDtmf(self, digit):
        with Logger(__name__ + '.SendDtmf'):
            self._linphonec.stdin.write(digit + '\n')
        
        
    def TerminateCall(self):
        with Logger(__name__ + '.TerminateCall'):
            self._linphonec.stdin.write('terminate\n')


    def _linphone_worker(self):        
        with Logger(__name__ + '._linphone_worker') as log:

            register_command = "register %s %s %s\n" % (self._identity, self._proxy, self._password)
            self._linphonec.stdin.write(register_command)
            self._linphonec.stdin.flush()
            
            while self._linphonec.poll() is None:
                
                message = self._linphonec.stdout.readline()
                log.debug('Linphonec: ' + message)

                if (message.find('Receiving new incoming call') >= 0):
                    self.IncomingCall()
                    
                if (message.find('Call terminated.') >= 0):
                    self.Release()

                if (message.endswith('busy.\n')):
                    self.Busy()

                if (message.startswith('linphonec> Registration')):
                    if (message.endswith('successful.\n')):
                        self.register()
                    else:
                        self.unregister()
                        log.error('Registration at remote sip server failed')
