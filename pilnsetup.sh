#!/bin/bash

#Install Script for PILN

#update pi
sudo apt get update
sudo apt get upgrade

#create directories
su - pi
git clone https://github.com/fayena/PILN.git
mkdir ./db ./html ./html/images ./html/style
ln -s /home/pi/PILN/images/hdrback.png /home/pi/html/images/hdrback.png
ln -s /home/pi/PILN/images/piln.png    /home/pi/html/images/piln.png
ln -s /home/pi/PILN/style/style.css    /home/pi/html/style/style.css

#install needed softare
apt install sqlite3
apt install ufw
apt install lighttpd

#setup firewall
ufw allow ssh
ufw allow http

#setup web server (lighttpd)
cp ./PILN/lighttpd.conf /etc/lighttpd/
cd /etc/lighttpd/conf-enabled
ln -s ../conf-available/10-cgi.conf .
cd
chown www-data:www-data PILN/html/pilnstat.json

#enable raspberry pi interfaces
raspi-config #enable interfaces ic2 & spi
lsmod | grep spi

#install thermocouple amplifier

cd
git https://github.com/johnrbnsn/Adafruit_Python_MAX31856
cd Adafruit_Python_MAX31856
python setup.py install

#install database

cp ./PILN/db/PiLN.sqlite3 ./db/PiLN.sqlite3
chown -R www-data:www-data /home/pi/db
sqlite3 /home/db/PILN.sqlite3
.read /home/pi/PILN/docs/PiLN.sql;
