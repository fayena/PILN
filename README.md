### UPDATE:  6/4/25 Works on Bookworm but there is a permissions error.   I 777 the entire folder and it works (I know I know but I needed it to run).   I'll try to trouble shoot the rest.  I also fixed an error that was causing a boot loop if the thermocouple was reading 0.0.   Tested as working with a clean install on Raspberry Pi OS (32-bit) Lite on a Raspberry Pi Zero W and a Raspberry PI 4 1G. Appears to run flawlessly on the Zero. Only 37M of memory was being used during test firing. Updated to python3 and offical adafruit libaries.

### Update: 3/14/2025   Solid state relays did not fix the interfearence problem.   It only seems to happen when the elements are worn.   However, it finally dawned on me that I could just turn off the relays before reading the temperature.   Hopefully this solves the problem for good.   Two good firings so far to cone 7 with no interference.   It was occuring with every firing previously.   

#### Update: 12/16/2020 After working great for a year, I started getting two different forms of interference. The first was a voltage fault on the max31856 that caused the temperature reading to hang. Not good when you’re doing a controlled firing. I'm almost positive this was caused by voltage spike from the relay coils. The second was that the temperature readings would start dropping after 1150C even though the real temperature was still rising. After a huge amount of trouble shooting, I ended up changing 3 things at once which eliminated both forms of interference. The three things were 1) add an opto isolator board between the raspberry pi/max31856 control circuit and the relays, 2) remove the max31856 control circuit from the relay box and 3) replace the mechanical relays. I still haven't isolated the cause of the interference that was causing the temperature readings to drop, but everything is working again. I will be updating the wiring schematics after Christmas. In the meantime, if you have questions feel free to contact me. You may be able to avoid both forms of interference by using solid state relays instead of mechanical ones. However, you will need to use heat sinks, probably a fan, and watch them closely for heat issues. Especially if you buy cheap ones.  Good solid state relays are not cheap.   

 

#### Tested as working with a clean install on Raspberry Pi OS (32-bit) Lite on a Raspberry Pi Zero W and a Raspberry PI 4 1G.   Appears to run flawlessly on the Zero.  Only 37M of memory was being used during test firing.   Updated to python3 and offical adafruit libaries.   

## Electricity and heat are dangerous! Evaluate the risk and make go no go decision!  I am not responsible for any injuries sustained or fires started!!!

## Useful skills
- linux command line
- basic soldering (to make all your connections permanent)
- electricity
## Helpful stuff
- Fritzing https://fritzing.org/home/ for viewing the fritizng wiring diagram
- SQLite Browser https://sqlitebrowser.org/ for viewing the sqlite3 database
- unl2003a pin diagram http://www.bristolwatch.com/ele/uln2003a/uln2003a_2.jpg
- Rasperry pi 40 pin connector pin diagram http://www.bristolwatch.com/ele/uln2003a/uln2003a_2.jpg  
## Code Info
This is a mesh of code from both git@github.com:pvarney/PiLN.git and git@github.com:BlakeCLewis/PILN.git  

It will work for smaller kilns.  My largest one is 27amps.  Theoretically it would work with a kiln up to about 84 amps (two 60 amp relays with 30% allowance).  However, I have not tried it and will not be trying it anytime soon.   If you decide to try a larger kiln, make sure all your wires are rated for the amperage you will be pulling.  Again electricity can cause injuries and death and can also start fires if done wrong.  Use your own judgement!


Changes I made to code include:
- Changing the logging function to be a per run log with the file named by RunID.  The logging does not run while the daemon is idle.     
- Adding an error trigger if the ramp temperature is 200C or more than the read temperature.   This errors the run and keeps your kiln from running and running trying to reach temp when it's not going to happen.
- Adding some code to resume in case of a power flicker.   It checks for completed segments and resumes the segment not completed.   While this will work fine for ramps, it could result in over firing if it lands on a hold.   ALWAYS Monitor you kiln!
- Added sorting to the main chart.   
- Removed, all the lcd code and the second thermocouple sensor and the kiln sitter code that BlackCLewis had added. 
- Kiln sitter is used as the safetly.   Put a small cone in the sitter that is at least one cone highter than your desired   firing.      
- Added Testing Code (see bottom of readme for instructions).    

I do not have a screen or wifi at my kiln location.   I tether my cell phone and then access the raspberry pi through ssh and a webbrowser both on my phone.   It will connect from a surprising distance this way.

Possible future improvements    
- install script (DONE)
- Offline charts  This would be really helpful to someone who uses a raspberry pi touch screen to run the daemon with no wifi.  (Done)
- performance watchdog:
    + klexting;  Sounds like fun to add but at the time it's not really helpful to me as I don't have wifi at my kiln           location    
    
## Hardware and Cost:
- Raspberry pi   I bought a Raspberry Pi 4 with 1gb ram for $41 on amazon.  I Installed the latested Raspbian but other Pi's will work.
- micro SD card (I used 32GB one)
- Raspberry pi Power supply and case if you want to build it as removable from the kiln controller.   If not you can add a 12v to 5v power board and have everything built permanently.   I bring my pi to my house for testing and use it for other things so building it this way is convenient for me.    
- 1 MAX31856 thermocouple module
    + $17.50 each, Adafruit (https://www.adafruit.com/product/3263);
- High temperature (2372 F) type K thermocouple
    + $7 https://www.aliexpress.com/item/32832729663.html?spm=a2g0s.9042311.0.0.b8fd4c4dqA7r1E
- Thermocouple wire
    + Braided wire 10m   $5.63  https://www.aliexpress.com/item/32961438359.html?spm=a2g0s.9042311.0.0.b8fd4c4dqA7r1E
- ULN2803A $1.22/10 to switch 12V fan and 12V coils of the relays Ali Express
 
- JQX-60F 1Z 60A High-power relay DC12V coils  They are loud when switching but generate very little heat.   Very pleased so far we'll see how long they last.  
    + 2 $3.73 each +$6.29 shipping https://www.aliexpress.com/item/32858874579.html?spm=a2g0s.9042311.0.0.b8fd4c4dqA7r1E or for about $12 each on amazon
- 12V power supply
    + converts 120vac to 12vdc,
    + supplies 12v to relay coils
    + $7.19 https://www.aliexpress.com/item/32911389359.html?spm=a2g0s.9042311.0.0.b8fd4c4dqA7r1E,
- crimp terminals, #10 awg, hi-temp appliance
    + $.16/each, (https://www.amazon.com/gp/product/B01L2TL63C/ref=oh_aui_detailpage_o02_s00?ie=UTF8&psc=1),
    + uses the same crimper used on the elements $16, (https://www.amazon.com/gp/product/B01L2TL63C/ref=oh_aui_detailpage_o02_s00?ie=UTF8&psc=1);
    + the crimpers require muscle
- big crimper
    + $25, (https://www.amazon.com/gp/product/B07D7Q54N2/ref=oh_aui_detailpage_o01_s03?ie=UTF8&psc=1),
    + I crimp 2 times, first time with correct size, second time reduced one notch(correct size is loose);
- 14 THHN stranded, hardware store, to power 12V supply, white,red,green 2' each;
- prototype board to mount everything
    + https://www.amazon.com/gp/product/B071R3BFNL/ref=ppx_yo_dt_b_asin_title_o09_s00?ie=UTF8&psc=1
- heat shrink, Harbor Freight
- metal ammo can from harbor freight

Rough breakdown of cost, it's possible I forgot something...If you want to wire you're kiln controller directly to the kiln you could save the cost of the power cord and plug.   
 
We had the wire I used to build this so it's not included in the cost.

- raspberry pi 4                       41
- 32gb micro sd card                    8
- raspberry pi case and power supply   13.59
- power cord 240v 50amp                20
- plug 240v 50amp                      11
- 12V 5 amp power supply                7.35
- din rails                             3.61
- din rail brackets                     3.44
- 2 60 amp relays                      13.75
- thermocouple wire                     5.94
- k style thermocouplex2               13.69
- Thermocouple Amplifier MAX31856      22
- metal ammo can                       15
- solderable breadboards               12.68
- total                               190ish


## Thermocouple, Kiln, and Max31856 info
Thermocouple tip: One side of the type-K thermocouple and type-k wire is magnetic(red side), Test with magnet to wire correctly.

-Kilns are old Paragons one is an A88B and one is a A66B.   Both are over 40 years old.   
 Kiln controller can be used with both

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
        unl2003a 1:        GPIO 23
        unl2003a 3:        GPIO 24
        unl2003a 8:        GND
        unl2003a 9:        12V
        unl2003a 16:    relay #1 coil (input is across the chip on pin1)
        unl2003a 14:    relay #2 coil (input is pin3)
        12V:        relay 1 and 2 coils



- Run Install script
From the terminal     
             
```wget https://raw.githubusercontent.com/fayena/PILN/Off-Line-Charts/pilnsetup.sh```

```sudo chmod +x pilnsetup.sh```

```./pilnsetup.sh```

You may have to enter your password and approve installs.   When the raspi-config interface opens select "interfacing options" and enable spi and ic2 and then select "finish".   The script should install everything you need.   This was tested in a raspberry pi 4.   
       

- Tuning:

    + Skutt KS1027 with old elements:
    
            Kc:   6.0
            Kp:   3.0
            Ki:   0.4
            Kd:  13.0
            Time internal:  30 seconds

- Using the Web App:

        On the same network that the RPi is connected, http://<RPi_IPAddress>/app/home.cgi
        Or, on the controller RPi, http://localhost/app/home.cgi

- Start the firing daemon:

        If you used the install script the daemon should start automatically.   If it doesn't you can use 

```sudo systemctl  start pilnfired.service```


## Testing
 You can run the code and do testing without having any electronics connected.   To run testing change "Debug = False" to "Debug = True" 
 You can change temperature rise and decrease by changing "TempRise += (CycleOnSec*5)" and "TempRise = TempRise - 2"


![screen shot of frizing wiring](https://raw.githubusercontent.com/fayena/PILN/master/Fritzing%20wiring%20diagram.png)

![cone 6 drop and hold](https://raw.githubusercontent.com/fayena/PILN/master/Drop%20and%20Hold%20Cone%206.png)

![Bique cone 06](https://raw.githubusercontent.com/fayena/PILN/master/Bique.png)



