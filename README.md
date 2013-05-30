
***
_This is a fork of pymissile project: http://code.google.com/p/pymissile/
that add support of center missile device (0416:9391) from Winbond Electronics_
***

Requirements
------------

* python (>=2.3)
* libusb (>=0.1.8)
* pyusb (==0.3.1) python module with patch included below
* urwid python module 

Install
-------

1. ensure python is installed and right version
2. install libusb-0.1.18 or better (available [here](http://libusb.sourceforge.net/) or use package appropriate for your distro, e.g. on ubuntu:

    ```$ sudo apt-get install libusb-dev```

3. install pyusb-0.3.1 (available [here](http://libusb.sourceforge.net/) or archived [here](http://pymissile.googlecode.com/svn/trunk/pyusb-0.3.1.tar.gz)) but patched (see below):

    `$ wget http://pymissile.googlecode.com/svn/trunk/pyusb-0.3.1.tar.gz`
    `$ tar zxvf pyusb-0.3.1.tar.gz`
    `$ cd pyusb-0.3.1`
    `$ wget http://pymissile.googlecode.com/svn/trunk/pyusb-0.3.1-kernel-detach.patch`
    `$ patch -p1 < pyusb-0.3.1-kernel-detach.patch`
    `$ sudo python setup.py install`

4. install urwid-0.8.10 (available [here](http://excess.org/urwid/))
5. plug in Missile Launcher
6. run missile.py as root (maybe non-root will work if you mess with libusb, let me know the details if that's the case)

    `$ wget http://pymissile.googlecode.com/svn/trunk/missile.py` 
    `$ chmod +x ./missile.py`
    `$ sudo ./missile.py`
    
Usage
-----
* `sudo ./missile.py` for command-line controls
* `sudo ./missile.py -n` for the network modus, as used for the Android Missile Launcher app ([more info](http://www.momentofgeekiness.com))
