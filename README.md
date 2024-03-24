***
_This is a fork of pymissile project: http://code.google.com/p/pymissile/
that add support of center missile device (0416:9391) from Winbond Electronics_

Now it has been converted to Python 3
***

Requirements
------------

* Python 3
* `pyusb` Python module
* `urwid` Python module

Install
-------

1. Ensure Python is installed and right version
2. Install Python modules either with

```bash
pip install -r requirements.txt
```

or on Raspberry Pi or any Debian-based Linux distribution

```bash
sudo apt-get install python3-usb python3-urwid
```

3. Plug in Missile Launcher
4. Run `missile.py` as `root` (maybe non-root will work if you mess with libusb, let me know the details if that's the case)

```bash
wget https://raw.github.com/wincentbalin/pymissile-ng/master/missile.py
chmod +x ./missile.py
sudo ./missile.py
```
    
Usage
-----
* `sudo ./missile.py` for command-line controls
* `sudo ./missile.py -n` for the network modus, as used for the Android Missile Launcher app ([more info](http://www.momentofgeekiness.com))
