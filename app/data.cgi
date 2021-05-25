#!le/usr/bin/env python3
import sys
import re
import datetime
import sqlite3
import json
import time
import logging
#logging.basicConfig(filename='example.log',level=logging.DEBUG)
jsonin = ""
#logging.debug(sys.stdin)
i = 0
for line in sys.stdin:
    jsonin += line
    #logging.debug(i)
    #logging.debug(line[i])
    i = i + 1
run_id = json.loads(jsonin)
#logging.debug("query")
query= "SELECT dt, segment, set_temp, temp, pid_output FROM firing WHERE run_id=" + run_id + " ORDER BY dt ASC;"

SQLDB = '/home/pi/PILN/db/PiLN.sqlite3'
conn = sqlite3.connect(SQLDB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute(query)
firingD={'dt':[],'segment':[],'set_temp':[],'temp':[],'pid_output':[]}
for row in cur.fetchall():
    firingD['dt'].append(row[0])
    firingD['segment'].append(row[1])
    firingD['set_temp'].append(row[2])
    firingD['temp'].append(row[3])
    firingD['pid_output'].append(row[4])
out_file = open("data.json", "w") 

json.dump(firingD,out_file, indent = 6)
print(json.dumps(0))
out_file.close() 

