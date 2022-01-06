#!/usr/bin/python3
import psutil
import sys
from subprocess import Popen
import json
import fnmatch
for process in psutil.process_iter():
    for f in fnmatch.filter(process.cmdline(),'*pilnfired.py'):    
    # if process.cmdline() == ['python3', 'pilnfired.py']:
        
        print(json.dumps(1))
        sys.exit()
print(json.dumps(0))
