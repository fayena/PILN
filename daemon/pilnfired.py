#!/usr/bin/env python3

from signal import *
import os
import time
import math
import logging
import sys
import sqlite3
import RPi.GPIO as GPIO
import Adafruit_GPIO
import Adafruit_GPIO.SPI as SPI
from Adafruit_MAX31856 import MAX31856 as MAX31856
#from display import display
GPIO.setmode(GPIO.BCM)

AppDir = '/home/pi/PILN'
StatFile = '/home/pi/PILN/app/pilnstat.json'

#--- sqlite3 db file ---
SQLDB = '/home/pi/db/PiLN.sqlite3'


#--- Global Variables ---
ITerm = 0.0
LastErr = 0.0
SegCompStat = 0
LastTmp = 0.0
cycle = 0 
#TempRise = 0
TotalSeg=0
LastProcVal = 0.0
RunState = ""
#--- MAX31856 only works on SPI0, SPI1 cannot do mode=1 ---
Sensor0 = MAX31856(tc_type=MAX31856.MAX31856_K_TYPE,
                   hardware_spi=SPI.SpiDev(0,0)) #SPI0,CE0 Kiln

#--- Relays ---
HEAT = (23, 24)
for element in HEAT:
    GPIO.setup(element, GPIO.OUT)
    GPIO.output(element, GPIO.LOW)

#--- Set up logging ---
# create logger
L = logging.getLogger('')

#--- Cleanup ---
def clean(*args):
    print("\nProgram ending! Cleaning up...\n")
    for element in HEAT:
        GPIO.output(element, False)
    GPIO.cleanup()
    #lcd.close(clear=True)
    print("All clean - Stopping.\n")
    os._exit(0)

for sig in (SIGABRT, SIGINT, SIGTERM):
    signal(sig, clean)

time.sleep(1)

# PID Update
def Update ( SetPoint, ProcValue, IMax, IMin, Window, Kp, Ki, Kd ):

    L.debug( "Entering PID update with parameters SetPoint:%0.2f, ProcValue:%0.2f, IMax:%0.2f, IMin:%0.2f," %
    ( SetPoint, ProcValue, IMax, IMin ))
    L.debug( "  Window:%d, Kp: %0.3f, Ki: %0.3f, Kd: %0.3f" %
    ( Window, Kp, Ki, Kd ))

    global ITerm, LastProcVal

    Err = SetPoint - ProcValue
    ITerm+= (Ki * Err);

    if ITerm > IMax:
        ITerm = IMax
    elif ITerm < IMin:
        ITerm = IMin

    DInput = ProcValue - LastProcVal

    #Compute PID Output
    Output = Kp * Err + ITerm - Kd * DInput;
    if Output > IMax:
        Output = IMax
    elif Output < IMin:
        Output = IMin
    if Err > 200:
        Output = 200
    #Remember for next time
    LastProcVal = ProcValue


    L.debug(
    "Exiting PID update with parameters Error:%0.2f, ITerm:%0.2f, DInput:%0.2f, Output:%0.2f" %
    ( Err, ITerm, DInput, Output )
    )

    return Output



#Segment loop

def Fire(RunID, Seg, TargetTmp1, Rate, HoldMin, Window, Kp, Ki, Kd):
    L.info("""Entering Fire function with parameters RunID:%d, Seg:%d,
              TargetTmp:%d, Rate:%d, HoldMin:%d, Window:%d
           """ % (RunID, Seg, TargetTmp1, Rate, HoldMin, Window)
    )
    global SegCompStat
    global wheel
    global cycle 
    #global TempRise
    global RunState
    TargetTmp = TargetTmp1
    RampMin = 0.0
    RampTmp = 0.0
    #ReadTmp = TempRise
    ReadTmp = Sensor0.read_temp_c()
    #roomTmp = Sensor1.read_temp_c()
    LastTmp = 0.0
    LastErr = 0.0
    StartTmp = 0.0
    TmpDif = 0.0
    Steps = 0.0
    StepTmp = 0.0
    StartSec = 0.0
    EndSec  = 0.0
    NextSec = 0.0
    RunState = "Ramp"
    Cnt = 0
    RampTrg = 0
    ReadTrg = 0
    
    while RunState != "Stopped"  and  RunState != "Complete" and RunState != "Error":
        if time.time() >= NextSec:
            Cnt += 1                         # record keeping only
            NextSec = time.time() + Window   # time at end of window
            LastTmp = ReadTmp
            #  roomTmp = Sensor1.read_temp_c()
            #ReadTmp = TempRise
            ReadTmp = Sensor0.read_temp_c()
            ReadITmp = Sensor0.read_internal_temp_c()
            if math.isnan(ReadTmp) or ReadTmp > 1330:
                ReadTmp = LastTmp + LastErr
                print ('  "kilntemp": "' + str(int(ReadTmp)) + '",\n')
               
            if RampTrg == 0:
                # if RampTmp has not yet reached TargetTmp increase RampTmp
                RampTmp += StepTmp

            # Rising Segment
            if TmpDif > 0:
                #---- RampTrg ----
                if RampTrg == 0 and RampTmp >= TargetTmp:
                    # RampTmp (window target temp) is 1 cycle away
                    # only will trigger once per segment
                    # RampTmp will no longer be incremented
                    RampTmp = TargetTmp
                    # reduce RampTmp to TargetTemp
                    RampTrg = 1
                    # set the ramp indicator
                    if ReadTrg == 1:
                        RunState = "Ramp/Hold"
                    else:
                        RunState = "Ramp complete"
                #---- ReadTrg ----
                if ((TargetTmp-ReadTmp <= TargetTmp*0.006)
                    or (ReadTmp >= TargetTmp)) and ReadTrg == 0:
                    ReadTrg = 1
                    EndSec = int(time.time()) + HoldMin*60
                    L.info("Set temp reached - End seconds set to %d" % EndSec)
                    if RampTrg == 1:
                        RunState = "Target/Hold"
                    else:
                        RunState = "Target Reached"
            # Falling Segment
            elif TmpDif < 0:
                #---- RampTrg ----
                if RampTmp <= TargetTmp  and  RampTrg == 0:
                # Ramp temp dropped to target
                    RampTmp = TargetTmp
                    RampTrg = 1
                    if ReadTrg == 1:
                        RunState = "Target/Ramp"
                    else:
                        RunState = "Ramp complete"
                #---- ReadTrg ----
                if ((ReadTmp-TargetTmp <= TargetTmp*0.006)
                        or (ReadTmp <= TargetTmp)) and ReadTrg == 0:
                # Read temp dropped to target or close enough
                    ReadTrg = 1
                    EndSec = int(time.time()) + HoldMin*60
                    L.info("Set temp reached - End seconds set to %d" % EndSec)
                    if RampTrg == 1:
                        RunState = "Ramp/Target"
                    else:
                        RunState = "Target Reached"

            # Initial Setup
            if StartTmp == 0:
                StartTmp = ReadTmp
                StartSec = int(time.time())
                NextSec = StartSec + Window
                TmpDif = TargetTmp - StartTmp
                RampMin = abs(TmpDif) * 60 / Rate # minutes to target at rate
                Steps = RampMin * 60 / Window     # steps of window size
                StepTmp = TmpDif / Steps          # degrees / step
                EndSec = StartSec + RampMin*60 + HoldMin*60
                                                  # estimated end of segment
                RampTmp = StartTmp + StepTmp      # window target
                if ((TmpDif > 0 and RampTmp > TargetTmp)
                   or (TmpDif < 0 and RampTmp < TargetTmp)):
                    # Hey we there before we even started!
                    RampTmp = TargetTmp # set window target to final target
                LastErr = 0.0
                L.info("""First pass of firing loop - TargetTmp:%0.2f,
                          StartTmp:%0.2f,RampTmp:%0.2f, TmpDif:%0.2f,
                          RampMin:%0.2f, Steps:%d, StepTmp:%0.2f,
                          Window:%d, StartSec:%d, EndSec:%d
                       """ % (TargetTmp, StartTmp, RampTmp, TmpDif, RampMin,
                              Steps, StepTmp, Window, StartSec, EndSec)
                )
            # run state through pid
            #Output = Update(RampTmp, ReadTmp, 23.609, 25, -25, Window, Kp, Ki, Kd)
            Output = Update(RampTmp,ReadTmp,100,0,Window,Kp,Ki,Kd)
            CycleOnSec = Window * Output * 0.01
            if CycleOnSec > Window:
                CycleOnSec = Window

            RemainSec = EndSec - int(time.time())
            RemMin, RemSec = divmod(RemainSec, 60)
            RemHr, RemMin = divmod(RemMin, 60)
            RemTime = "%d:%02d:%02d" % (RemHr, RemMin, RemSec)
            L.debug("""RunID %d, Segment %d (loop %d) - RunState:%s,
                       ReadTmp:%0.2f, RampTmp:%0.2f, TargetTmp:%0.2f,
                       Output:%0.2f, CycleOnSec:%0.2f, RemainTime:%s
                    """ % (RunID, Seg, Cnt, RunState, ReadTmp, RampTmp,
                           TargetTmp, Output, CycleOnSec, RemTime)
            )
                  
		
            print("""RunID %d, Segment %d (loop %d) - RunState:%s,
                       ReadTmp:%0.2f, RampTmp:%0.2f, TargetTmp:%0.2f,
                       Output:%0.2f, CycleOnSec:%0.2f, RemainTime:%s
                    """ % (RunID, Seg, Cnt, RunState, ReadTmp, RampTmp,
                           TargetTmp, Output, CycleOnSec, RemTime)
            )
            if Output > 0:
                if Output == 200:
                    sql = "UPDATE profiles SET state=? WHERE run_id=?;"
                    p = ('Error', RunID)
                    L.error("State = Error RunID: %d" % (RunID)) 
                    try:
                        SQLCur.execute(sql, p)
                        SQLConn.commit()
                        L.error("state updated to Error")
                        RunState = "Error"
                    except:
                        SQLConn.rollback()
                        L.error("DB Update failed2!")
                else:    
                    L.debug("==>Relay On")
                    for element in HEAT:
                        GPIO.output(element, True)
                    #TempRise += (CycleOnSec*0.138888889)
                    #L.info("cycleoNsee: %d and temprise: %d" % (CycleOnSec, TempRise)) 
                    cycle = cycle + 1
                    time.sleep(CycleOnSec)
            if Output < 100:
                L.debug("==>Relay Off")
                for element in HEAT:
                    GPIO.output(element, False)
                #TempRise = TempRise - 5
            #L.info("Write status information to status file %s:" % StatFile)

            # Write status to file for reporting on web page
            sfile = open(StatFile, "w+")
            sfile.write('{\n' +
                '  "proc_update_utime": "' + str(int(time.time())) + '",\n'
                + '  "readtemp": "' + str(int(ReadTmp)) + '",\n'
                + '  "run_profile": "' + str(RunID) + '",\n'
                + '  "run_segment": "' + str(Seg) + '",\n'
                + '  "ramptemp": "' + str(int(RampTmp)) + '",\n'
                + '  "targettemp": "' + str(int(TargetTmp)) + '",\n'
                + '  "status": "' + str(RunState) + '",\n'
                + '  "segtime": "' + str(RemTime) + '"\n'
                + '}\n'
            )
            sfile.close()

            L.debug("Writing stats to Firing DB table...")
            SQL = "INSERT INTO Firing (run_id, segment, dt, set_temp, temp, int_temp, pid_output) VALUES ( '%d', '%d', '%s', '%.2f', '%.2f', '%.2f', '%.2f' )" % ( RunID, Seg, time.strftime('%Y-%m-%d %H:%M:%S'), RampTmp, ReadTmp, ReadITmp, Output )
            try:
                SQLCur.execute(SQL)
                SQLConn.commit()
                L.info ("database writing complete1")
            except:
                SQLConn.rollback()
                L.error("DB Update failed1!")
            
            # Check if profile is still in running state and check that the 
            #currently running profile 
            sql = "SELECT * FROM profiles WHERE state='Running';"
            SQLCur.execute(sql)
            result = SQLCur.fetchall()
            if len(result) > 0:
                RunningID = result[0]['run_id']
                if time.time() > EndSec and ReadTrg == 1:
                    # hold time is over and reached target
                    RunState = "Complete"    
            if (len(result) == 0 or RunningID != RunID) and RunState != "Error"  :
                L.warning("Profile no longer in running state - exiting firing")
                SegCompStat = 1 
                RunState = "Stopped"

            L.info("RunState end: %s" % (RunState))
    return () 
# --- end Fire() ---

L.info("===START PiLN Firing Daemon===")
L.info("Polling for 'Running' firing profiles...")

SQLConn = sqlite3.connect(SQLDB)
SQLConn.row_factory = sqlite3.Row
SQLCur = SQLConn.cursor()

while 1:
   
    #ReadTmp = TempRise
    ReadTmp = Sensor0.read_temp_c()
    ReadITmp = Sensor0.read_internal_temp_c()
  #  roomTmp = Sensor1.read_temp_c()
  #  roomITmp = Sensor1.read_internal_temp_c()
    while math.isnan(ReadTmp):
        #ReadTmp = TempRise
        ReadTmp = Sensor0.read_temp_c()
        print (' "kilntemp": "' + str(int(ReadTmp)) + '",\n')

    #L.debug("Write status information to status file %s:" % StatFile)
    sfile = open(StatFile, "w+")
    sfile.write('{\n' +
        '  "proc_update_utime": "' + str(int(time.time())) + '",\n'
        + '  "readtemp": "' + str(int(ReadTmp)) + '",\n'
        + '  "run_profile": "none",\n'
        + '  "run_segment": "n/a",\n'
        + '  "ramptemp": "n/a",\n'
        + '  "status": "n/a",\n'
        + '  "targettemp": "n/a"\n'
        + '}\n'
    )
    sfile.close()
    # --- Check for 'Running' firing profile ---
    sql = "SELECT * FROM profiles WHERE state=?;"
    p = ('Running',)
    SQLCur.execute(sql, p)
    Data = SQLCur.fetchall()

    #--- if Running profile found, then set up to fire, woowo! --
    
        
    if len(Data) > 0:
        RunID = Data[0]['run_id']
        Kp = float(Data[0]['p_param'])
        Ki = float(Data[0]['i_param'])
        Kd = float(Data[0]['d_param'])
        logfile = (AppDir + '/log/RunID_%s_Fired.log' % (RunID))
        StTime = time.strftime('%Y-%m-%d %H:%M:%S')
        #add logging for RunID.          
        for hdlr in L.handlers[:]:  # remove all old handlers
            L.removeHandler(hdlr)
        # create file handler which logs even debug messages
        fh = logging.FileHandler(logfile, 'a')
        L.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)                
        L.addHandler(fh)    
        
        sql = "UPDATE profiles SET start_time=? WHERE run_id=?;"
        p = (StTime, RunID)
        try:
            SQLCur.execute(sql, p)
            SQLConn.commit()
        except:
            SQLConn.rollback()

        # Get segments
        sql = "SELECT * FROM segments WHERE run_id=?;"
        p = (RunID,)
        SQLCur.execute(sql, p)
        ProfSegs = SQLCur.fetchall()
        # --- for each segment in firing profile loop ---
        for Row in ProfSegs:
            TotalSeg += 1
        #write_log("TotalSeg:%d" % (TotalSeg), logfile)    
        L.info("TotalSeg: %d" % (TotalSeg))
        for Row in ProfSegs:
            RunID = Row['run_id']
            Seg = Row['segment']
            TargetTmp = Row['set_temp']
            Rate = Row['rate']
            HoldMin = Row['hold_min']
            Window = Row['int_sec']
             #--check to see if uncompleted segments
            if SegCompStat != 1:
                L.info("segment is %d start time is %s endtime is %s" % (Seg, Row['start_time'],Row['end_time']))
                if (Row['start_time'] is not None and Row['end_time'] is not None):
                    L.info("segment %d is finished and ReadTmp is %d" % (Row['segment'],ReadTmp))
                else:       
                            
                    StTime = time.strftime('%Y-%m-%d %H:%M:%S')
                    #--- mark started segment with datatime ---
                    sql = """UPDATE segments SET start_time=?
                             WHERE run_id=? AND segment=?;
                          """
                    p = (StTime, RunID, Seg)
                    try:
                        SQLCur.execute(sql, p)
                        SQLConn.commit()
                    except:
                        print("error")
                        SQLConn.rollback()

                    time.sleep(0.5)

                    Fire(RunID, Seg, TargetTmp, Rate, HoldMin, Window,
                                 Kp, Ki, Kd)
                    for element in HEAT:
                        GPIO.output(element, False) ## make sure elements are off

                        EndTime=time.strftime('%Y-%m-%d %H:%M:%S')
                        
                        L.debug("""Update run id %d,
                                   segment %d end time to %s
                                """ % (RunID, Seg, EndTime)
                        )

                    #--- mark segment finished with datetime ---
                    sql = """UPDATE segments SET end_time=?
                            WHERE run_id=? AND segment=?;
                          """
                    p = (EndTime, RunID, Seg)
                    L.info("Segment %s Complete" % (Seg))
                                     
                    try:
                        SQLCur.execute(sql, p)
                        SQLConn.commit()
                    except:
                        SQLConn.rollback()
                    #check to see if the segment just completed 
                    #is the final segment if so mark completed 
                    if Seg == TotalSeg and RunState != "Error" :
                        sql = "UPDATE profiles SET end_time=?, state=? WHERE run_id=?;"
                        p = (EndTime, 'Completed', RunID)
                        try:
                            SQLCur.execute(sql, p)
                            SQLConn.commit()
                            L.info("state updated to Completed")
                        except:
                            SQLConn.rollback()
                            L.error("DB Update failed2!")

        # --- end firing loop ---
            L.info("SegCompStat %d" % (SegCompStat))

            SegCompStat = 0

            L.info("Polling for 'Running' firing profiles...")
            #remove log handlers so we're not logging a bunch of stuff from the max31856
            for hdlr in L.handlers[:]:  # remove all old handlers
                L.removeHandler(hdlr)
    time.sleep(2)

SQLConn.close()
