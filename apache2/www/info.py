# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

from subprocess import Popen, PIPE

def index(req):
    req.content_type = 'text/plain'
    
    req.write('POTSBLIZ - (C)2015 - Norbert Huffschmid\n\n')

    req.write('Plain Old Telephone Service Beyond Local IP Stack\n\n')
    
    with open ('/usr/local/lib/python2.7/dist-packages/potsbliz/potsbliz.version', 'r') as version_file:
        version = version_file.read()
    req.write('Version: ' + version + '\n')

    req.write('License: GNU GPL V3\n\n')
    
    process = Popen(['/bin/uname', '-a'], stdout=PIPE, stderr=PIPE)
    output, errors = process.communicate()
    req.write(output)
