#!/bin/bash

#Install Script for PILN

#update pi
sudo apt update
sudo apt upgrade -y
#make sure git and python3 dependencies are installed 

sudo apt install git
sudo apt-get install -y python3-setuptools python3-pip python-pip


#create directories

git clone --branch Off-Line-Charts https://github.com/fayena/PILN.git

#install needed softare

sudo apt install sqlite3
sudo apt install ufw
sudo apt install lighttpd
sudo pip3 install jinja2
sudo pip3 install psutil


echo "software installed"

#setup firewall
sudo ufw allow ssh
sudo ufw allow http
echo "firewall setup"

#setup web server (lighttpd)

sudo cp /home/pi/PILN/lighttpd/lighttpd.conf /etc/lighttpd/
cd /etc/lighttpd/conf-enabled
sudo ln -s ../conf-available/10-cgi.conf .
cd
#create directories

git clone https://github.com/fayena/PILN.git
sudo mkdir ./PILN/log ./PILN/style/css ./PILN/style/js
echo "directories created"


#download needed files
sudo wget -P /home/pi/PILN/style/js https://cdn.datatables.net/1.10.25/js/jquery.dataTables.min.js
sudo wget -P /home/pi/PILN/style/js https://code.jquery.com/jquery-3.5.1.js
sudo wget -P /home/pi/PILN/style/js https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.5.0/chart.min.js
sudo wget -P /home/pi/PILN/style/js https://momentjs.com/downloads/moment.js

#make sure permissions are correct
sudo chown -R -L  www-data:www-data /home/pi/PILN/style
sudo chown pi:pi /home/pi/PILN/app/pilnstat.json
sudo chown pi:pi /home/pi/PILN/log
sudo chown www-data:www-data -R /home/pi/PILN/db

restart webserver
sudo service lighttpd restart
echo "webserver setup"

#enable raspberry pi interfaces
sudo raspi-config #enable interfaces ic2 & spi
lsmod | grep spi
echo "interfaces enabled"

#install thermocouple amplifier

cd
sudo pip3 install adafruit-circuitpython-max31856

#install needed python web module
sudo pip3 install jinja2

#install database

sudo chown -R www-data:www-data /home/pi/PILN/db

echo "database installed"

#install pilnfired service
sudo cp /home/pi/PILN/daemon/pilnfired.service /lib/systemd/system/

sudo chmod 644 /lib/systemd/system/pilnfired.service
sudo chmod +x /home/pi/PILN/daemon/pilnfired.py

sudo systemctl daemon-reload
sudo systemctl enable pilnfired.service
sudo systemctl start pilnfired.service
