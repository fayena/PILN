#!/usr/bin/env python3

from signal import *
import os
import time
import logging
import sys
import math
import sqlite3
import RPi.GPIO as GPIO
import board
import busio
import digitalio
import adafruit_max31856
import adafruit_ads7830.ads7830 as ADC
from adafruit_ads7830.analog_in import AnalogIn
from adafruit_motor import stepper

GPIO.setmode(GPIO.BCM)

AppDir = '/home/pi/PILN'
StatFile = '/home/pi/PILN/app/pilnstat.json'

#--- sqlite3 db file ---
SQLDB = '/home/pi/PILN/db/PiLN.sqlite3'


#--- Global Variables ---
ITerm = 0.0
LastErr = 0.0
SegCompStat = 0
LastTmp = 0.0
cycle = 0 
Debug = False
if Debug == True: 
    TempRise = 900
#TotalSeg=0
LastProcVal = 0.0
RunState = ""
Output = 0

i2c = board.I2C()

# Initialize ADS7830 pressure sensor and oxygen
adc = ADC.ADS7830(i2c)
chan = AnalogIn(adc, 4)
oxy = AnalogIn(adc,5)


spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
     
# allocate a CS pin and set the direction
cs = digitalio.DigitalInOut(board.D0)
cs.direction = digitalio.Direction.OUTPUT
#set thermocouple type
th = adafruit_max31856.ThermocoupleType.S     
# create a thermocouple object with the above
thermocouple = adafruit_max31856.MAX31856(spi, cs, th)

#--- step motor  --- for gas control 
HEAT = (
    digitalio.DigitalInOut(board.D17),  # A1
    digitalio.DigitalInOut(board.D18),  # A2
    digitalio.DigitalInOut(board.D27),  # B1
    digitalio.DigitalInOut(board.D22),  # B2
) 

#for pin in HEAT:
    #GPIO.setup(pin, GPIO.OUT)
    #GPIO.output(pin, GPIO.LOW)

#step motor for baffle control 
coils = (
    digitalio.DigitalInOut(board.D26),  # A1
    digitalio.DigitalInOut(board.D16),  # A2
    digitalio.DigitalInOut(board.D24),  # B1
    digitalio.DigitalInOut(board.D23),  # B2
)

for coil in HEAT:
    coil.direction = digitalio.Direction.OUTPUT
for coil in coils:
    coil.direction = digitalio.Direction.OUTPUT

regulator = stepper.StepperMotor(HEAT[0], HEAT[1], HEAT[2], HEAT[3], microsteps=None)
motor = stepper.StepperMotor(coils[0], coils[1], coils[2], coils[3], microsteps=None)

#--- Set up logging ---
# create logger
L = logging.getLogger('')

#--- Cleanup ---
def clean(*args):
    print("\nProgram ending! Cleaning up...\n")
    for pin in HEAT:
        GPIO.output(pin, False)
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
    Output = round(Kp * Err + ITerm - Kd * DInput)
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

 
def pressure_average():
    num_readings=50
    readings = [chan.value for _ in range(num_readings)]
        
    if not readings:
        return None  # Handle empty list to avoid division by zero

    total = sum(readings)
    average = total / len(readings)
    y = 0.000054609*average - 0.2
    return y

def oxygen_average():
    num_readings=500
    readings = [oxy.value for _ in range(num_readings)]
    if not readings:
        return None
    total = sum(readings)
    average = total / len(readings)
    #y = 0.0000413603*average + 0.441174016
    #y = 0.000413603*average + 0.2
    y = 0.000054609*average+0.1 

    if y> 1: 
        return 0
    else:
        return y
#Segment loop

def Fire(RunID, Seg, TargetTmp1, Rate, HoldMin, Window, Kp, Ki, Kd,oxymax, oxymin):
    L.info("""Entering Fire function with parameters RunID:%d, Seg:%d,
              TargetTmp:%d, Rate:%d, HoldMin:%d, Window:%d
           """ % (RunID, Seg, TargetTmp1, Rate, HoldMin, Window)
    )
    global SegCompStat
    global cycle 
    if Debug == False:
        global TempRise
    global RunState
    global Output
    TargetTmp = TargetTmp1
    RampMin = 0.0
    RampTmp = 0.0
    if Debug == True: 
        ReadTmp = TempRise
    else:
        ReadTmp = thermocouple.temperature
        pressure = pressure_average()
        oxygen = oxygen_average()
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
            
            if Debug:
                ReadTmp = TempRise
            else:
                pressure = pressure_average()
                ReadTmp = thermocouple.temperature
                oxygen = oxygen_average()

            if math.isnan(ReadTmp): #or ReadTmp > 1330:
                ReadTmp = LastTmp + LastErr
                print ('  "kilntemp1": "' + str(int(ReadTmp)) + '",\n')
               
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
                if ((TargetTmp-ReadTmp <= 0.5)
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
                if ((ReadTmp-TargetTmp <= 0.5)
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
                print(ReadTmp)
                print(StartTmp)
                StartSec = int(time.time())
                NextSec = StartSec + Window
                TmpDif = TargetTmp - StartTmp
                print(TmpDif)
                print(Window)
                RampMin = abs(TmpDif) * 60 / Rate # minutes to target at rate
                Steps = RampMin * 60 / Window 
                print(Steps)    # steps of window size
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
            Old_Pid = Output
            Output = Update(RampTmp,ReadTmp,100,0,Window,Kp,Ki,Kd)
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
                L.debug("==>Motor On")
                #for element in HEAT:
                #    GPIO.output(element, True)
                if Debug == True:
                    TempRise += (Output*0.25)
                #L.info("cycleoNsee: %d and temprise: %d" % (CycleOnSec, TempRise)) 
                cycle = cycle + 1
                step_sleep = 0.002
                reg_sleep=0.02
                STEPS=2500
                motor_step_counter = 0 ;
                # 400 steps is one full turn of valve  For the gas nema17
                print("output: ", Output)
                print("Old_Pid: ", Old_Pid)
                print("Pressure: ", pressure)
                print("oxygen:", oxygen)
                print("oxymin:",oxymin)
                print("oxymax:",oxymax)
                try : 
                    float(oxygen) 
                    res = True
                except : 
                    print("Not a float") 
                    res = False
                if Output < Old_Pid and pressure > .5:   #decrease temperature
                    if oxygen >= oxymin:
                        #direction = True # True to decrease pressure, False to increase pressure
                        step_count = round((Old_Pid - Output)*2)
                        for step in range(step_count):
                            regulator.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
                            time.sleep(reg_sleep)

                    else:
                        for step in range(STEPS):
                            motor.onestep(style=stepper.DOUBLE)
                            time.sleep(step_sleep)

                        step_count= 0
                elif  Output > Old_Pid and pressure < 3:  #increase temperature
                    if oxygen >= oxymin:
                        #open baffle
                        for step in range(STEPS):
                            motor.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
                            time.sleep(step_sleep)
                        step_count = 0
                    else:
                        #direction = False # True to decrease pressure, False to increase pressure
                        step_count = round((Output - Old_Pid)*2)
                        for step in range(step_count):
                            regulator.onestep(style=stepper.DOUBLE)
                            time.sleep(reg_sleep)
                    
                elif Output == 100 and Old_Pid == 100: #increase temperature
                    if oxygen >= oxymin:
                        #open baffle
                        for step in range(STEPS):
                            motor.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
                            time.sleep(step_sleep)
                        step_count = 0
                    else:
                        #direction = False # True to decrease pressure, False to increase pressure
                        if pressure <=3:
                            step_count = round((Output - Old_Pid)*2)
                            for step in range(step_count):
                                regulator.onestep(style=stepper.DOUBLE)
                                time.sleep(reg_sleep)
                    
                    
                elif Output == 0 and Old_Pid == 0:  #decrease temperature
                    if pressure >= .5:
                        if oxygen >= oxymin:
                            #direction = True # True to decrease pressure, False to increase pressure
                            step_count = 100
                            for step in range(step_count):
                                regulator.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
                                time.sleep(reg_sleep)
                        else:
                            for step in range(STEPS):
                                motor.onestep(style=stepper.DOUBLE)
                                time.sleep(step_sleep)
                            step_count= 0
                    else:
                        step_count = 0
                else:
                    step_count = 0
                                # the meat
                
                regulator.release()
                motor.release()
                time.sleep(Window)
                
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
            SQL = "INSERT INTO Firing (run_id, segment, dt, set_temp, temp, pid_output,pressure,oxy) VALUES ( '%d', '%d', '%s', '%.2f', '%.2f', '%.2f' , '%.2f','%.2f')" % ( RunID, Seg, time.strftime('%Y-%m-%d %H:%M:%S'), RampTmp, ReadTmp,Output,pressure,oxygen )
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
   
    if Debug:
        ReadTmp = TempRise
    else:
        ReadTmp = thermocouple.temperature
        pressure = pressure_average()
        oxygen = oxygen_average()
    while math.isnan(ReadTmp):
        if Debug:
            ReadTmp = TempRise
        else:
            ReadTmp = thermocouple.temperature
            pressure = pressure_average()
            oxygen = oxygen_average()
    print (' "kilntemp2": "' + str(int(ReadTmp)) + '",\n')

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
        TotalSeg=0
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
            oxymax=Row['oxymax']
            oxymin = Row['oxymin']
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
                                 Kp, Ki, Kd,oxymax,oxymin)
                    
                    #turn down to start point
                   
                    
                    try:
                        pressure=pressure_average()
                        print ("pressure: ", pressure)
                        while pressure >= .5:
                            for step in range(100):
                                regulator.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
                                time.sleep(reg_sleep)
                            pressure=pressure_average()
                    # try:
                    #     i = 0
                    #     for i in range(MotorSteps):
                    #         for pin in range(0, len(HEAT)):
                    #             GPIO.output( HEAT[pin], step_sequence[motor_step_counter][pin] )
                    #         motor_step_counter = (motor_step_counter - 1) % 8
                    #         time.sleep( step_sleep )
                    except:
                        print ("error with motor")
                    regulator.release()

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
                    if Seg == TotalSeg and RunState != "Error" and RunState != "Stopped":
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
