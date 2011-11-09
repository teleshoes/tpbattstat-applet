[![Flattr this git repo](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=wolke&url=https://github.com/teleshoes/tpbattstat-applet&title=tpbattstat-applet&language=en_GB&tags=github&category=software) 
```
Copyright 2011 Elliot Wolk
This project is licensed under the GPLv3. See COPYING for details.


TPBattStat-Applet runs in a standalone gtk window, in the gnome-panel,
or outputs text suitable for piping to dzen2.
It extends the functionality of tp_smapi, which provides access to certain
battery controls on nearly all Lenovo/IBM ThinkPads.
TPBattStat-Applet provides:
 -battery balancing
   {protecting your main, ultrabay, and/or slice battery from unhealthy
    charging/discharging}
 -percent(s) remaining, image meters, charge/discharge rate in Watts
 -a nominally pretty, reasonably configurable graphical display
   {e.g.: can be big, with one image per battery,
    small, with one image and some text,
    or tiny, with a little bit of colored text}


Requires:
tp_smapi
  see: http://www.thinkwiki.org/wiki/Tp_smapi#Installation_from_source
       the ubuntu installation script should take care of this for most users.

For led controls, you need to have the thinkpad_acpi module.
To install led controls, run ./led-controls/install.sh
This copies the two perl execs and adds setuid to led.

In case anyone feels overwhelmed with an urge to thank me:
https://flattr.com/thing/289178/ThinkPad-Battery-Status-Applet


pygtk v2.0 or higher
e.g.: sudo apt-get install python-gnome2
newer pygtk packages have 'gnomeapplet' in python-gnomeapplet


Here is an example script to install on Ubuntu 10.10
##########################################
echo
echo building tpsmapi...
sudo aptitude install tp-smapi-source 
sudo module-assistant prepare tp-smapi 
sudo module-assistant auto-install tp-smapi 
sudo modprobe tp-smapi
echo
echo installing git and prereq libs...
sudo apt-get install git
sudo apt-get install python-gnome2
sudo apt-get install python-gnomeapplet
echo
echo git clone and build...
cd /tmp
git clone git://github.com/teleshoes/tpbattstat-applet.git
cd tpbattstat-applet
./install.sh
sudo rm -rf /tmp/tpbattstat-applet
echo
echo restart gnome-panel and apparmor
killall gnome-panel
gnome-panel --replace & #restarts gnome-panel so you can add it to the panel
sudo /etc/init.d/apparmor reload #loads the smapi-battaccess scripts profile.
##########################################
```
