# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack
# (C)2015  - Norbert Huffschmid - GNU GPL V3 

import os
import subprocess
from threading import Lock
from time import sleep


_dialtone_lock = Lock()
_dialtone_proc = None


def start_dialtone():
    global _dialtone_lock, _dialtone_proc
    with _dialtone_lock:
        if (_dialtone_proc == None):
            os.environ["AUDIODEV"] = "hw:1,0"
            # don't know why the second sin argument is required (gets ignored in potsbliz setup)
            _dialtone_proc = subprocess.Popen(["play", "-n", "synth", "120", "sin", "425", "sin", "425", "sin", "350"])


def stop_dialtone():
    global _dialtone_lock, _dialtone_proc
    with _dialtone_lock:
        if (_dialtone_proc != None):
            _dialtone_proc.terminate()
            _dialtone_proc.wait()
            _dialtone_proc = None


def play_ok_tone():
    start_dialtone()
    sleep(1)
    stop_dialtone()
            

def play_error_tone():
    for x in range(0, 5):
        start_dialtone()
        sleep(0.2)
        stop_dialtone()
        sleep(0.2)
