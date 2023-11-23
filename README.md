### Update: 11/18/2023   I'm currently back to working on this branch since I've switched to firing with gas.  I still use my electric kiln for bisque firings with solid state relays so if you have any questions about either repo feel free to ask.   
 

#### Currently only works on the "Bullseye" branch of Raspberry pi OS.  Haven't had a chance to trouble shoot that yet.   Tested as working with a clean install on Raspberry Pi OS (32-bit) Lite on a Raspberry Pi Zero W and a Raspberry PI 4 1G.   Appears to run flawlessly on the Zero.  Only 37M of memory was being used during test firing.   Updated to python3 and offical adafruit libaries.   

## Electricity and heat are dangerous! Evaluate the risk and make go no go decision!  I am not responsible for any injuries sustained or fires started!!!

## Useful skills
- linux command line
- basic soldering (to make all your connections permanent)
- electricity
## Helpful stuff
- Fritzing https://fritzing.org/home/ for viewing the fritizng wiring diagram
- SQLite Browser https://sqlitebrowser.org/ for viewing the sqlite3 database
- Rasperry pi 40 pin connector pin diagram http://www.bristolwatch.com/ele/uln2003a/uln2003a_2.jpg  
## Code Info
This is a mesh of code from both git@github.com:pvarney/PiLN.git and git@github.com:BlakeCLewis/PILN.git  

Changes I made to code include:
- Changing the logging function to be a per run log with the file named by RunID.  The logging does not run while the daemon is idle.     
- Adding an error trigger if the ramp temperature is 200C or more than the read temperature.   This errors the run and keeps your kiln from running and running trying to reach temp when it's not going to happen.
- Adding some code to resume in case of a power flicker.   It checks for completed segments and resumes the segment not completed.   While this will work fine for ramps, it could result in over firing if it lands on a hold.   ALWAYS Monitor you kiln!
- Added sorting to the main chart.   
- Removed, all the lcd code and the second thermocouple sensor and the kiln sitter code that BlackCLewis had added.      
- Added Testing Code (see bottom of readme for instructions).
-Changed the charting from google charts to chart.js so that I could load it offline    

I do not have a screen or wifi at my kiln location.   I tether my cell phone and then access the raspberry pi through ssh and a webbrowser both on my phone.   It will connect from a surprising distance this way.

Possible future improvements    
- install script (DONE)
- Offline charts  This would be really helpful to someone who uses a raspberry pi touch screen to run the daemon with no wifi.  (done)
- klexting;  Sounds like fun to add     
    
## Hardware and Cost:
-Need to update 
## Thermocouple, Kiln, and Max31856 info
-Thermocouple tip: One side of the type-K thermocouple and type-k wire is magnetic(red side), Test with magnet to wire correctly.
-TDI Conversion Kiln 
## Install 

Instructions for install an operating system to the Raspberry Pi  https://www.raspberrypi.org/documentation/installation/installing-images/    I use the Raspbian OS https://www.raspberrypi.org/downloads/raspbian/  

Stuff to get it to work:

- Pin-Out:

        MAX31856 Vcc:    3.3V    PIN17
        MAX31856 GND:    GND     PIN14
        MAX31856 SDO:    GPIO 9  MISO
        MAX31856 SDI:    GPIO 10 MOSI
        MAX31856 CS:    GPIO 5  (aka D5)
        MAX31856 SCK:    GPIO 11 CLK
     


- Run Install script
From the terminal     
             
```wget https://raw.githubusercontent.com/fayena/PILN/gas-fired-modulating-valve/pilnsetup.sh```

```sudo chmod +x pilnsetup.sh```

```./pilnsetup.sh```

You may have to enter your password and approve installs.   When the raspi-config interface opens select "interfacing options" and enable spi and ic2 and then select "finish".   The script should install everything you need.   This was tested in a raspberry pi 4.   
       

- Tuning:

   +need to update

- Using the Web App:

        On the same network that the RPi is connected, http://<RPi_IPAddress>/app/home.cgi
        Or, on the controller RPi, http://localhost/app/home.cgi

- Start the firing daemon:

        If you used the install script the daemon should start automatically.   If it doesn't you can use 

```sudo systemctl  start pilnfired.service```


## Testing
 You can run the code and do testing without having any electronics connected.   To run testing change "Debug = False" to "Debug = True" 
 -- need to update:   You can change temperature rise and decrease by changing "TempRise += (CycleOnSec*5)" and "TempRise = TempRise - 2"





