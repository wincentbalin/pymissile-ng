#!/usr/bin/env python
#
#  Written by: Scott Weston <scott@weston.id.au>
#  Edited  by: Zakaria ElQotbi <zakaria@elqotbi.com>
#  Edited  by: Raymond Vermaas <info@momentofgeekiness.com>
#
# - Version --------------------------------------------------------------
#
#  $Id: missile.py,v 2.0 2011/12/02 15:45:24 scott Exp $
#
# - License --------------------------------------------------------------
#
# Copyright (c) 2006, Scott Weston
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * The name of the contributors may not be used to endorse or promote
#   products derived from this software without specific prior written
#   permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import usb
#import exceptions
import urwid
import urwid.curses_display
import sys
import getopt
import random
import re
import os
from time import sleep, time
from socket import *

vendor_product_ids = [(0x1130,0x0202),(0x0416, 0x9391)]

class centerMissileDevice:
  dev       = None
  handle    = None
  STOP      = 0x0
  LEFT      = 0x8
  RIGHT     = 0x4
  UP        = 0x2
  DOWN      = 0x1
  LEFTUP    = LEFT + UP
  RIGHTUP   = RIGHT + UP
  LEFTDOWN  = LEFT + DOWN
  RIGHTDOWN = RIGHT + DOWN
  FIRE      = 0x10

  def __init__(self,usbdevice):
      try:
        self.handle = usbdevice.open()
        self.handle.reset()
        return
      except NoMissilesError:
        raise NoMissilesError()

  def move(self, direction):
     self.handle.controlMsg(0x21, 0x09, [0x5f, direction, 0xe0, 0xff, 0xfe], 0x0300, 0x00)

class legacyMissileDevice:
  dev       = None
  INITA     = (85, 83, 66, 67,  0,  0,  4,  0)
  INITB     = (85, 83, 66, 67,  0, 64,  2,  0)
  CMDFILL   = ( 8,  8,
                0,  0,  0,  0,  0,  0,  0,  0,
                0,  0,  0,  0,  0,  0,  0,  0,
                0,  0,  0,  0,  0,  0,  0,  0,
                0,  0,  0,  0,  0,  0,  0,  0,
                0,  0,  0,  0,  0,  0,  0,  0,
                0,  0,  0,  0,  0,  0,  0,  0,
                0,  0,  0,  0,  0,  0,  0,  0)
  STOP      = ( 0,  0,  0,  0,  0,  0)
  LEFT      = ( 0,  1,  0,  0,  0,  0)
  RIGHT     = ( 0,  0,  1,  0,  0,  0)
  UP        = ( 0,  0,  0,  1,  0,  0)
  DOWN      = ( 0,  0,  0,  0,  1,  0)
  LEFTUP    = ( 0,  1,  0,  1,  0,  0)
  RIGHTUP   = ( 0,  0,  1,  1,  0,  0)
  LEFTDOWN  = ( 0,  1,  0,  0,  1,  0)
  RIGHTDOWN = ( 0,  0,  1,  0,  1,  0)
  FIRE      = ( 0,  0,  0,  0,  0,  1)

  def __init__(self, usbdevice):
    try:
      self.handle = usbdevice.open()
      self.handle.reset()
    except NoMissilesError:
      raise NoMissilesError()

  def move(self, direction):
    self.handle.controlMsg(0x21, 0x09, self.INITA, 0x02, 0x01)
    self.handle.controlMsg(0x21, 0x09, self.INITB, 0x02, 0x01)
    self.handle.controlMsg(0x21, 0x09, direction+self.CMDFILL, 0x02, 0x01)

class NoMissilesError(Exception): pass

class UsbDevice:
  def __init__(self):
    self.handle = None
    self.launcher = None
    self.dev = None
    self.busses = usb.busses()

  def probe(self):
    count = 0
    for bus in self.busses:
      devices = bus.devices
      for dev in devices:
       for i, (vendor_id, product_id) in enumerate(vendor_product_ids):
        if dev.idVendor==vendor_id and dev.idProduct==product_id:
          if count==0:
            self.dev = dev
            self.conf = self.dev.configurations[0]
            self.intf = self.conf.interfaces[0][0]
            self.endpoints = []
            for endpoint in self.intf.endpoints:
              self.endpoints.append(endpoint)
            if i == 0:
              self.launcher = legacyMissileDevice
              return self.launcher
            elif i == 1:
              self.launcher = centerMissileDevice
              return self.launcher
          else:
            count=count+1
    raise NoMissilesError()

  def open(self):
    if self.handle:
      self.handle = None
    self.handle = self.dev.open()
    try:
      self.handle.detachKernelDriver(0)
      self.handle.detachKernelDriver(1)
    except usb.USBError as err:
      print(err, file=sys.stderr)

    self.handle.setConfiguration(self.conf)
    self.handle.claimInterface(self.intf)
    self.handle.setAltInterface(self.intf)
    return self.handle

class MissileNoDisplay:
  def run(self):
    try:
        usbdevice = UsbDevice()
        MissileDevice = usbdevice.probe()
        m = MissileDevice(usbdevice)
    except NoMissilesError:
        raise NoMissilesError()
    while 1:
      keys = None
      while not keys:
        keys = raw_input("Enter something: ")
      for k in keys:
        if k == 'window resize':
          size = self.ui.get_cols_rows()
        elif k in ('w', 'up'):
            m.move(MissileDevice.UP)
        elif k in ('x', 'down'):
            m.move(MissileDevice.DOWN)
        elif k in ('a', 'left'):
            m.move(MissileDevice.LEFT)
        elif k in ('d', 'right'):
            m.move(MissileDevice.RIGHT)
        elif k in ('f', 'space'):
            m.move(MissileDevice.FIRE)
        elif k in ('s'):
            m.move(MissileDevice.STOP)
        elif k in ('q'):
            m.move(MissileDevice.LEFTUP)
        elif k in ('e'):
            m.move(MissileDevice.RIGHTUP)
        elif k in ('z'):
            m.move(MissileDevice.LEFTDOWN)
        elif k in ('c'):
            m.move(MissileDevice.RIGHTDOWN)
        elif k in ('r'):
          for n in range(3):
              sleep(0.5)
        elif k in ('v'):
            if  random.random() > 0.8:
              m.move(MissileDevice.FIRE)
        elif k in ('esc'):
          return

class MissileDisplay:
  palette = [ ('body', 'black', 'dark cyan', 'standout'),
              ('footer','light gray', 'dark blue'),
              ('header', 'white', 'dark blue', 'underline'),
              ('important','white', 'dark red', 'bold'),
              ('key', 'light cyan', 'black', 'underline'),
              ('title', 'white', 'black',), ]

  BLANK   = urwid.Text("")
  WARNING = urwid.Text([('important',"CAUTION: AIM AWAY FROM FACE")],
                       align='center')
  HEADER  = urwid.AttrWrap(urwid.Text("MISSILE COMMAND!", align='center'),
                           'header')
  FOOTER  = urwid.AttrWrap(urwid.Text("scott@weston.id.au", align='center'),
                           'footer')
  CONTENT = [ BLANK,
              urwid.Text(["Use the following\n"
                          "keys  to move\n\n"
                          "Q   W   E \n"
                          "  \ | /   \n"
                          "A -(S)- D \n"
                          "  / | \   \n"
                          "Z   X   C \n\n"
                          "F to fire all guns once\n"
                          "R for rapid sequentual fire of all missiles\n"
                          "S to Stop\n"
                          "ESC to Exit\n\n",], align='center'),
              WARNING,
              BLANK, ]

  def __init__(self):
    self.listbox = urwid.ListBox(self.CONTENT)
    view = urwid.AttrWrap(self.listbox, 'body')
    self.view = urwid.Frame(view, header=self.HEADER, footer=self.FOOTER)

  def main(self):
    self.ui = urwid.curses_display.Screen()
    self.ui.register_palette(self.palette)
    self.ui.run_wrapper(self.run)

  def run(self):

    try:
        usbdevice = UsbDevice()
        MissileDevice = usbdevice.probe()
        m = MissileDevice(usbdevice)
    except NoMissilesError:
        raise NoMissilesError()

    size = self.ui.get_cols_rows()
    while 1:
      canvas = self.view.render(size, focus=1)
      self.ui.draw_screen(size, canvas)
      keys = None
      while not keys:
        keys = self.ui.get_input()
      for k in keys:
        if k == 'window resize':
          size = self.ui.get_cols_rows()
        elif k in ('w', 'up'):
            m.move(MissileDevice.UP)
        elif k in ('x', 'down'):
            m.move(MissileDevice.DOWN)
        elif k in ('a', 'left'):
            m.move(MissileDevice.LEFT)
        elif k in ('d', 'right'):
            m.move(MissileDevice.RIGHT)
        elif k in ('f', 'space'):
            m.move(MissileDevice.FIRE)
        elif k in ('s'):
            m.move(MissileDevice.STOP)
        elif k in ('q'):
            m.move(MissileDevice.LEFTUP)
        elif k in ('e'):
            m.move(MissileDevice.RIGHTUP)
        elif k in ('z'):
            m.move(MissileDevice.LEFTDOWN)
        elif k in ('c'):
            m.move(MissileDevice.RIGHTDOWN)
        elif k in ('r'):
          for n in range(3):
              m.move(MissileDevice.FIRE)
              sleep(0.5)
        elif k in ('v'):
            if  random.random() > 0.8:
              m.move(MissileDevice.FIRE)
        elif k in ('esc'):
          return
        self.view.keypress(size, k)

class MissileNetwork:

  def main(self):
    host = "0.0.0.0"
    port = 20000
    buf  = 1024
    addr = (host,port)

    try:
        usbdevice = UsbDevice()
        MissileDevice = usbdevice.probe()
        m = MissileDevice(usbdevice)
    except NoMissilesError:
        raise NoMissilesError()

    UDPSock = socket(AF_INET,SOCK_DGRAM)
    UDPSock.bind(addr)

    while 1:
      cmd,addr = UDPSock.recvfrom(buf)
      cmd = cmd.strip()
      k = cmd

      if not k:
        continue

      print("Received via network at {:2.2f} command {} ".format(time(), k))

      if k in ('w', 'up'):
         m.move(MissileDevice.UP)
      elif k in ('x', 'down'):
         m.move(MissileDevice.DOWN)
      elif k in ('a', 'left'):
        m.move(MissileDevice.LEFT)
      elif k in ('d', 'right'):
        m.move(MissileDevice.RIGHT)
      elif k in ('f', 'space'):
        m.move(MissileDevice.FIRE)
      elif k in ('s', 'S'):
        m.move(MissileDevice.STOP)
      elif k in ('q'):
        m.move(MissileDevice.LEFTUP)
      elif k in ('e'):
        m.move(MissileDevice.RIGHTUP)
      elif k in ('z'):
        m.move(MissileDevice.LEFTDOWN)
      elif k in ('c'):
        m.move(MissileDevice.RIGHTDOWN)
      elif k in ('r'):
        for n in range(3):
          m.move(MissileDevice.FIRE)
          sleep(0.5)
      elif k in ('v'):
        if random.random() > 0.9:
            m.move(MissileDevice.FIRE)
      elif k in ('esc'):
        UDPSock.close()
        return

def usage():
  print("Usage:")
  print("  -h | --help : this help")
  print("  -n | --network: simple network listener mode (Read the source Luke!)")
  print("  -c | --console: read command directly from console (dont use urwid interface)")
  print("  -v | --version: version")
  sys.exit(2)

def version():
  print("$Id: missile.py,v 1.13 2006/07/25 17:01:24 scott Exp $")
  sys.exit(0)

def main(argv):
  try:
    opts, args = getopt.getopt(argv, "hvnc", ["help", "version", "network", "console"])
  except getopt.GetoptError:
    print("Sorry, bad option.")
    usage()

  if opts:
    for o, a in opts:
      if o in ("-h", "--help"):
        usage()
      elif o in ("-v", "--version"):
        version()
      elif o in ("-n", "--network"):
        try:
          MissileNetwork().main()
        except NoMissilesError:
          print("No WMDs found.")
          return
      elif o in ("-c", "--console"):
        try:
          MissileNoDisplay().run()
        except NoMissilesError:
          print("No WMDs found.")
          return
      else:
        try:
          MissileDisplay().main()
        except NoMissilesError:
          print("No WMDs found.")
          return
  else:
    try:
      MissileDisplay().main()
    except NoMissilesError:
      print("No WMDs found.")
      return

if __name__=="__main__":
  main(sys.argv[1:])
