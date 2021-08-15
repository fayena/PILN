#!/usr/bin/python3
import psutil
import sys
from subprocess import Popen
import json
for process in psutil.process_iter():
    
    if process.cmdline() == ['python3', 'pilnfired.py']:
        
        print(json.dumps(1))
        sys.exit()
print(json.dumps(0))
