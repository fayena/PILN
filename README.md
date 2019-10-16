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

It will work for smaller kilns.  My largest one is 27amps.  Theoretically it would work with a larger kiln.  However, I have not tried it and will not be trying it anytime soon.  Again electricity can cause injuries and death and can also start fires if done wrong.  Use your own judgement!


Changes I made to code include:
- Changing the logging function to be a per run log with the file named by RunID.  The logging does not run while the daemon is idle.     
- Adding an error trigger if the ramp temperature is 200C or more than the read temperature.   This errors the run and keeps your kiln from running and running trying to reach temp when it's not going to happen.
- Adding some code to resume in case of a power flicker.   It checks for completed segments and resumes the segment not completed.   While this will work fine for ramps, it could result in over firing if it lands on a hold.   ALWAYS Monitor you kiln!
- Added sorting to the main chart.   
- Removed, all the lcd code and the second thermocouple sensor and the kiln sitter code that BlackCLewis had added. 
- Kiln sitter is used as the safetly.   Put a small cone in the sitter that is at least one cone highter than your desired   firing.      

I do not have a screen or wifi at my kiln location.   I tether my cell phone and then access the raspberry pi through ssh and a webbrowser both on my phone.   It will connect from a surprising distance this way.


Possible future improvements    
- install script 
- Offline charts  This would be really helpful to someone who uses a raspberry pi touch screen to run the daemon with no wifi.  
- performance watchdog:
    + klexting;  Sounds like fun to add but at the time it's not really helpful to me as I don't have wifi at my kiln           location    
    
## Hardware and Cost:
- Raspberry pi   I got my raspberry pi 3 B+ from amazon for $38 but looking at prices this morning, it looks like they are now listed for around $50 so you might want to shop around.   I used Raspberry Pi 3 B+ with the latest Raspbian but other Pi's will work
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

- raspberry pi 3 b+                    37.36
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
- total                               187.41


## Thermocouple, Kiln, and Max31856 info
Thermocouple tip: One side of the type-K thermocouple and type-k wire is magnetic(red side), Test with magnet to wire correctly.


The max31856 reads the room temperature as the cold junction temperature.   If the kiln is heating up the cold junction on the thermocouple more than room temperature, you will need to adjust the location of the max31856 or adjust the cold junction temperature.   

-Kilns are old Paragons one is an A88B and one is a A66B.   Both are over 40 years old.   
 Kiln controller can be used with both

## Install 

Stuff to get it to work:

- Pin-Out:

        MAX31856 Vcc:    3.3V    PIN17
        MAX31856 GND:    GND     PIN14
        MAX31856 SDO:    GPIO 9  MISO
        MAX31856 SDI:    GPIO 10 MOSI
        MAX31856 CS:    GPIO 8  CE0
        MAX31856 SCK:    GPIO 11 CLK
        unl2003a 1:        GPIO 22
        unl2003a 3:        GPIO 23
        unl2003a 8:        GND
        unl2003a 9:        12V
        unl2003a 16:    relay #1 coil (input is across the chip on pin1)
        unl2003a 14:    relay #2 coil (input is pin3)
        12V:        relay 1 and 2 coils



- Install PiLN files in /home and create log directory:

        su - pi
        git clone git@github.com:BlakeCLewis/PiLN.git
        mkdir ./log ./db ./html ./html/images ./html/style


- Install sqlite3:

        sudo apt install sqlite3

- Set up directories/link for web page:


        ln -s /home/pi/PiLN/images/hdrback.png /home/pi/html/images/hdrback.png
        ln -s /home/pi/PiLN/images/piln.png    /home/pi/html/images/piln.png
        ln -s /home/pi/PiLN/style/style.css    /home/pi/html/style/style.css
- lighttpd:

        sudo apt-get install lighttpd
        sudo cp lighttpd.conf /etc/lighttpd/
        cd /etc/lighttpd/conf-enabled
        sudo ln -s ../conf-available/10-cgi.conf .
        sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
        sudo iptables save
        cd
        sudo chown www-data:www-data PiLN/html/pilnstat.json
        
- Install required Python packages:

        sudo raspi-config #enable interfaces ic2 & spi
        lsmod | grep spi

- Install Adafruit Pyhton MAX31856 library:

        cd
        git https://github.com/johnrbnsn/Adafruit_Python_MAX31856
        cd Adafruit_Python_MAX31856
        sudo python setup.py install

- create the sqlite3 database:

                sudo chown -R www-data:www-data /home/pi/PiLN/db
        sqlite3 /home/pi/db/PILN.sqlite3
        sqlite> .read /home/pi/PILN/docs/PiLN.sql;

- Tuning:

    + Skutt KS1027 with old elements:
    
            Kc:   6.0
            Kp:   3.0
            Ki:   0.4
            Kd:  13.0
            Time internal:  30 seconds

- Using the Web App:

        On the same network that the RPi is connected, http://<RPi_IPAddress>/pilnapp/home.cgi
        Or, on the controller RPi, http://localhost/pilnapp/home.cgi

- Start the firing daemon:

        python3 /home/pi/PILN/daemon/pilnfired.py

![screen shot of frizing wiring](https://raw.githubusercontent.com/fayena/PILN/master/docs/Fritzing%20Diagram.png)

