#!le/usr/bin/env python3
import sys
import re
import datetime
import sqlite3
import json
import time
debug = 0 
SQLDB = '/home/pi/db/PiLN.sqlite3'
# Get json data from standard in
jsonin = ""
for line in sys.stdin:
    jsonin += line
#DEBUG
if 1 == debug:
    chkutime = jsonin.rstrip()
    f = open("/tmp/pygetdata.txt","w+")
    f.write(jsonin)
#-----
if jsonin == "":
    print ("\n{\n \"unix_timestamp\": ", str(int(time.time()))," \n}")
else:
    query = json.loads(jsonin)
    conn = sqlite3.connect(SQLDB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query['select'])
#DEBUG
    if 1 == debug:
        jsoncol = json.dumps(query['columns'])
#-----
    retdata = '\n{"cols":' + json.dumps(query['columns']) + ',"rows":['
    for row in cur:
        retdata += '{"c":['
        colindx = 0
        for coldata in query['columns']:
            cval = ""
            colname = coldata['id']
            if coldata['type'] == "datetime":
                dtvals = re.split('[- :]', str(row[colindx]) )
                dtvals[1] = str( int( dtvals[1] ) - 1 )
                cval = '"Date(' + ",".join(dtvals) + ')"'
            elif coldata['type'] == "number":
                cval = float(row[colindx])
            else:
                cval = '"' + str(row[colindx]) + '"'
            colindx += 1
            if cval:
                retdata += '{"v":' + str(cval) + '},'
            else:
                retdata += '{"v":null},'
        retdata = retdata.rstrip(',')
        retdata += "]},"
    cur.close()
    conn.close()
    retdata = retdata.rstrip(',')
    retdata += "]}\n"
    print (retdata)
