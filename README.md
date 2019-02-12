# Auto watering system using Raspberry Pi

This is a software package for a Raspberry Pi based automatic watering system built with an analog moisture sensor. The software design supports up to four independently managed plants (each handled by one sensor and one pump). Besides monitoring moisture and watering as needed it also captures measurements and pump activity in a database and charts stats in a web diagram. Hardware is only covered to clarify compatibility, this is not a step-by-step guide on wiring your system (see for example [here](https://www.hackster.io/ben-eagan/raspberry-pi-automated-plant-watering-with-website-8af2dc) for a guide on wiring everything together).

Also provided are 3d print models for the enclosure of the control unit as well as an adapter to spread water evenly over the surface of the pot.

## Software

Starting from [Raspbian Lite OS](https://www.raspberrypi.org/downloads/raspbian/) install perform the following steps:

* raspi-setup - configure wifi, locale and in Interfacing Options enable I2C
* apt-get install sqlite3
* apt-get install libsqlite3-dev
* apt-get install i2c-tools
* apt-get install python-smbus
* pip install pysqlite
* pip install flask 
* pip install adafruit-ads1x15

Unpack this software to `/home/pi`

To detect moisture and possibly water the plant periodically, run:

`crontab -e`

Add this line to the bottom to run every 2 hours

`* */2    * * *   (cd /home/pi/pi_auto_waterer/ || exit 1; sudo python ./auto_water.py)`

To start the web server automatically, add the following line to /etc/rc.local

`python /home/pi/pi_auto_waterer/web_plants.py &`


Edit `config.json` to match your hardware configuration (e.g., GPIO assignments) as well as the watering parameters appropriate for your plants. The stats web site is available at the root of your device, ie. `http://<IP address of your Pi here>` 


## Hardware

This software is built for the following hardware. Since a single AD converter can handle up to four separate analog signals, it is easy to modify the hardware configuration by adding sensors and using a relay with more channels to support up to four plants. 
* [Raspberry Pi (any model)](https://amzn.to/2X7l62m)
* [Relay (5V)](https://amzn.to/2WVOE2F)
* [Pump (5V)](https://amzn.to/2I9JrBd) + [matching water line](https://amzn.to/2tleJL7)
* [Moisture Sensor](https://amzn.to/2GCUHDM)
* [Analog-Digital Converter ADS1x15](https://amzn.to/2WVOlVC)

## Box

You can 3d-print the box to put everything in using the included STL files. In addition to the hardware above, it uses the following parts:
* MicroUSB breakout board to connect a power adapter for the pump(s)
* Two 3.5mm audio jacks (per plant) to plug in the sensor and the pump
* Self tapping screws (M2.3 + 6mm)
* 4x #8-32 x 2in machine screw and nut to screw the box together
