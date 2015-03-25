# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

from subprocess import Popen, PIPE

def index(req):
    req.content_type = 'text/plain'
    
    process = Popen(['/usr/bin/apt-cache', 'show' ,'potsbliz-rpi'], stdout=PIPE, stderr=PIPE)
    output, errors = process.communicate()
    req.write(output)
    
    process = Popen(['/bin/uname', '-a'], stdout=PIPE, stderr=PIPE)
    output, errors = process.communicate()
    req.write(output)
