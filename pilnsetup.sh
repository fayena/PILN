#!/bin/bash

#Install Script for PILN

#update pi
#sudo apt update
#sudo apt upgrade

#create directories

git clone https://github.com/fayena/PILN.git
sudo mkdir ./db ./html ./html/images ./html/style
sudo ln -s /home/pi/PILN/images/hdrback.png /home/pi/html/images/hdrback.png
sudo ln -s /home/pi/PILN/images/piln.png    /home/pi/html/images/piln.png
sudo ln -s /home/pi/PILN/style/style.css    /home/pi/html/style/style.css
sudo ln -s /home/pi/PILN/app /home/pi/html/
sudo chown -R www-data:www-data /home/pi/html

echo "directories created"

#install needed softare

sudo apt install sqlite3
sudo apt install ufw
sudo apt install lighttpd

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
sudo chown www-data:www-data PILN/html/pilnstat.json
echo "webserver setup"

#enable raspberry pi interfaces
sudo raspi-config #enable interfaces ic2 & spi
lsmod | grep spi
echo "interfaces enabled"

#install thermocouple amplifier

cd
git clone https://github.com/johnrbnsn/Adafruit_Python_MAX31856
cd Adafruit_Python_MAX31856
python setup.py install
echo "thermocouple amplifier installed"

#install database

sudo cp ./PILN/db/PiLN.sqlite3 ./db/PiLN.sqlite3
sudo chown -R www-data:www-data /home/pi/db

echo "database installed"
