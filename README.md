Electricity and heat are dangerous! Evaluate the risk and make go no go decision!

Web-based Raspberry Pi Kiln Control:
- achieved my goal to run on Rasberry Pi Zero W, but I am currently firing on a Raspberry Pi 3b: 
	+ sqlite3 database for firing profiles and logging (small memory footprint)
	+ lighttpd web server (small memory footprint)

- kiln sitter(KS) as a sensor
	+ KS functions as 'ARMED', can not start firing without kilnsitter being armed
	+ set profile top temp higher than KS cone, KS is intended trigger, thermocouple is safety

Future improvements:
- performance watchdog:
	+ warning notifications, klexting;
	+ shutdown when a minimum rate cannot be maintained,
- inductive current sensors: element fault indication;
- crash/loss of power recovery:
	+ PI comes up, KS is armed & profile is 'Running' then how to consider unfinished segment
	+ compare temp at the timestamp to current temp
	+ compare last timestamp of 'Running' firing to current time
	+ notify on power resume, klexting (kiln text message)

Hardware:
- 20x4 LCD w/ i2c backpack
	+ $13, (https://www.amazon.com/gp/product/B01GPUMP9C/ref=oh_aui_detailpage_o01_s00?ie=UTF8&psc=1) uses RPLCD library;
- 2 MAX31856 thermocouple module
	+ $17.50 each, Adafruit (https://www.adafruit.com/product/3263);
- High temperature (2372 F) type K thermocouple
	+ $7/each, 3 pack, (https://www.aliexpress.com/item/High-Temperature-K-Type-Thermocouple-Sensor-for-Ceramic-Kiln-Furnace-1300-Temperature/32832729663.html?spm=a2g0s.9042311.0.0.3dd14c4dIQr1ud);
- Thermocouple wire
    + I bought the 24awg yellow k-type wire at the pottery store,
    + I use about 6 feet, the controller is attached to the wall;
- uln2803a to switch 12V fan and 12V coils of the relays
	+ $1/each on amazon, using 3 of 8 channels;
- Deltrol 20852-81 relays
	+ 1 for each segment of kiln, 3 for my kiln
	+ This is equivalent to relay Skutt uses to switch sections/zones (Skutt model is SPDT, this is same series but DPDT),
	+ $17.50 each and about that much for shipping (https://www.galco.com/buy/Deltrol-Controls/20852-81);
- 12V power supply
	+ converts 120vac to 12vdc,
	+ supplies 12v to relay coils, HDMI monitor, and 5v buck converter,
	+ $20 (https://www.amazon.com/gp/product/B00DECZ7WC/ref=oh_aui_detailpage_o01_s01?ie=UTF8&psc=1),
	+ rail mounted;
- 5V buck converter
	+ converts 12v to 5v USB connector for Pi power,
	+ $7 (https://www.amazon.com/gp/product/B071FJVRCT/ref=oh_aui_detailpage_o03_s00?ie=UTF8&psc=1);
- monitor w/HDMI input
	+ optionally can be controlled/viewed from phone or computer on home network;
- terminal blocks to distribute L1, L2, N and GND
	+ Ground, $6 (https://www.amazon.com/gp/product/B000K2MA9M/ref=oh_aui_detailpage_o05_s00?ie=UTF8&psc=1),
	+ L1,L2,Neutral, 3 @ $7/each, (https://www.amazon.com/gp/product/B000OTJ89Q/ref=oh_aui_detailpage_o05_s00?ie=UTF8&psc=1);
- #12 awg hi-temp appliance wire to each element;
- 3 ceramic 2 pole terminal blocks
	+ 1 for each kiln segment;
- crimp terminals, #10 awg, hi-temp appliance
	+ $.16/each, (https://www.amazon.com/gp/product/B01L2TL63C/ref=oh_aui_detailpage_o02_s00?ie=UTF8&psc=1),
	+ uses the same crimper used on the elements $16, (https://www.amazon.com/gp/product/B01L2TL63C/ref=oh_aui_detailpage_o02_s00?ie=UTF8&psc=1);
	+ the crimpers require muscle
- lugs #6 AWG copper
	+ $9 for 10 (https://www.amazon.com/gp/product/B073Y8Q9JQ/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1);
- big crimper
	+ $25, (https://www.amazon.com/gp/product/B07D7Q54N2/ref=oh_aui_detailpage_o01_s03?ie=UTF8&psc=1),
	+ I crimp 2 times, first time with correct size, second time reduced one notch(correct size is loose);
- 14 THHN stranded, hardware store, to power 12V supply, white,red,green 2' each;
- hook up wire
	+ power to pi, fan, relay coils,
	+ (https://www.amazon.com/gp/product/B07G7W7G4T/ref=ppx_yo_dt_b_asin_title_o01_s00?ie=UTF8&psc=1);
- prototype board to mount everything
	+ https://www.adafruit.com/product/2310);
- heat shrink, Harbor Freight

Thermocouple tip: One side of the type-K thermocouple and type-k wire is magnetic(red side), Test with magnet to wire correctly.

- Current kiln controller is attached to is a Old Skutt 281, which is a previous model number of KS1027:
  + old elements, I am surprised that it easily reaches temp at a reasonable rate, this kiln sat unused, outside under roof for 15 years;
  + lid(split and flaking)repaired/coated;
  + base(cracks) repaired;
  + rust removal on controller boxes, painted;
  + built rolling stand out of 2"x3" mild steel rectangular tube;


Stuff to get it to work:

- Pin-Out:

		RPLCD:  	GPIO 2 SDA
		RPLCD:  	GPIO 3 SCL
		RPLCD:  	5V
		RPLCD:  	GND
		MAX31856 Vcc:	3.3V    PIN17
		MAX31856 GND:	GND     PIN14
		MAX31856 SDO:	GPIO 9
		MAX31856 SDI:	GPIO 10
		MAX31856 CS:	GPIO 8 & GPIO 7
		MAX31856 SCK:	GPIO 11
		unl2003a 1:	GPIO 22 
		unl2003a 3:	GPIO 23
		unl2003a 5:	GPIO 24
		unl2003a 7:	GPIO 13
		unl2003a 8:	GND
		unl2003a 9:	12V
		unl2003a 10:	FAN black/gnd
		unl2003a 16:	relay #1 coil (input is across the chip on pin1)
		unl2003a 14:	relay #2 coil (input is pin3)
		unl2003a 12:	relay #3 coil (input is pin5)
		12V:    	relay 1,2,3 coils and FAN red/+

- Install PiLN files in /home and create log directory:

		su - pi
		git clone git@github.com:BlakeCLewis/PiLN.git
		mkdir ./log ./db ./html ./html/images ./html/style


- Install sqlite3:

		sudo apt-get install sqlite3
		mkdir -p db
		sqlite3 ~/db/PiLN.sqlite3
		sqlite> .read /home/pi/PILN/docs/PiLN.sql
		sqlite> .q
		sudo chown -R www-data:www-data ~/db



- Set up directories/link for web page:


		sudo ln -s /home/pi/PILN/images/hdrback.png /home/pi/html/images/hdrback.png
		sudo ln -s /home/pi/PILN/images/piln.png    /home/pi/html/images/piln.png
		sudo ln -s /home/pi/PILN/style/style.css    /home/pi/html/style/style.css
		sudo ln -s /home/pi/PILN/app /home/pi/html/
		touch /home/pi/PILN/app/pilnstat.json
		sudo chown -R www-data:www-data /home/pi/html
		
- lighttpd:

		sudo apt-get install lighttpd
		sudo cp /home/pi/PILN/lighttpd/lighttpd.conf /etc/lighttpd/
		cd /etc/lighttpd/conf-enabled
		sudo ln -s ../conf-available/10-cgi.conf .
		sudo apt install ufw
  		sudo ufw enable
  		sudo ufw allow http
	
		
- Install required Python packages:

		sudo raspi-config #enable interfaces ic2 & spi
		lsmod | grep spi

- Install Adafruit Pyhton MAX31856 library:

		cd
		git clone https://github.com/adafruit/Adafruit_Python_MAX31856.git
		cd Adafruit_Python_MAX31856
		sudo python setup.py install

- create the sqlite3 database:
		sudo mkdir -p /home/pi/PiLN/db/
                sudo chown -R www-data:www-data /home/pi/PiLN/db
		sqlite3 /home/pi/db/PiLN.sqlite3
		sqlite> .read /home/pi/PiLN/docs/PiLN.sql;

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

		python3 /home/pi/PiLN/daemon/pilnfired.py

- PID with C algorithm:

      This is a work in progress and I have not finish testing these instructions;
      My implementation of a PID algorithm that is optimized for a system that can only add heat;

      Kc is not determined by a time sensitive value;
      Ki is not time sensitive;
      Kp & Kd are determined by an amount of error over a time segment 
          these terms should be normalized by the time segment like (term*60/window)
      
      Cterm = Kc/100 * (Current_temp - room_temp);
      Window = determined by bump test, mine is 30 seconds
      error = Setpoint - Currrent_temp;
      Pterm = Kp * 60/Window * error;
      Iterm = Summation (Ki * error), constrained by (Imin <= Iterm <= Imax);
      Dterm = Kd * 60/Window * (error - previous_error);
      output = (Cterm + Pterm + Iterm + Dterm) constrained by (0 <= output <= 100);

      Window:
          Size of the base time unit, the controller will decide what to do every window;
          based on the response time of the kiln (how long it takes to finish reacting to input);
          my kiln window = 30;
          bump test

              turning on kiln for 30 seconds
              record time/temp every 10 seconds until temp starts falling
              tau_temp = .75 * (hi_temp - start_temp)
              window = .25 * (time of tau_temp)

      Cterm:

          Kc = 6;
          steady state term, required amount of energy to maintain temp;
          linear, inverse proportional to r-value of kiln;
          my kiln requires about 6% of output per 100C of temp differential;
          (100C ~= 6% to hold temp, 1000C ~= 60% to hold temp);
          tune:
              after determining "window", do a test run to 500C, with a 10 minute hold every 100C;
              query the database to find the average output during the holds;
              mine was about 6% per 100C.

      Pterm:

          Kp = 3;
          proportional to desired change in temp;
          TODO - test runs with rate 60 and 166 C/hr, query the database and average(pid_output-Pterm) for each 100C segment.

      Iterm:
          
          Ki = 0.4;
          Imin = -25;
          Imax = 25;
          Imax and Imin are hard coded, may need to make tunable or auto-adjusted based on temp and/or temp climb rate;
          accumlitive error correction of Cterm + Pterm;
          to reduce "Iterm Windup", limit with (Imin <= Iterm <+ Imax).

      Dterm:

          Kd = 13;
          change in error;
          Dterm is the acceleration term.
          it allows time for Iterm to wind up or down, to keep from falling behind or over shooting.

      output:

          output = (Cterm + Pterm + Iterm + Dterm);
          output is a percentage and therefore needs to be constrained by (0 <= output <= 100)
