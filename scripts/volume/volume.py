#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import ConfigParser

class Volume ():

  def __init__ (self):

    self.config_path = os.path.expanduser ("~/.volume")
    self.sink = None
    self.mute = False
    self.volume = 50
    self.volume_adjustment = 5
    self.min_volume = 0
    self.max_volume = 100
    self.pactl = "/usr/bin/pactl"


  def main (self):
    """Constructor"""

    command = None

    if self.load_config () == False:
      print "Failed to load in configuration"
      sys.exit ()

    try:
      command = sys.argv[1]
    except IndexError:
      pass

    if command == "mute":
      self.mute = not self.mute

    elif command == "up":
      self.adjust_volume (self.volume_adjustment)

    elif command == "down":
      self.adjust_volume (self.volume_adjustment * -1)

    else:

      try:
        self.set_volume (int (command))
      except (TypeError, ValueError):
        pass


    self.save_config ()
    self.apply ()
    self.awesome ()
    self.print_status ()


  def load_config (self):
    """Loads in the configuration"""

    config = ConfigParser.ConfigParser ()
    config.read (self.config_path)

    if config.has_section ("main") == False:
      return False

    try:
      self.sink = config.getint ("main", "sink")
      self.volume = config.getint ("main", "volume")
      self.mute = config.getboolean ("main", "mute")
    except:
      return False

    return True


  def save_config (self):
    """Saves the configuration to disk"""

    config = ConfigParser.ConfigParser ()
    config.add_section ("main")
    config.set ("main", "sink", self.sink)
    config.set ("main", "volume", self.volume)
    config.set ("main", "mute", self.mute)

    with open (self.config_path, "wb") as configfile:
      config.write (configfile)


  def set_volume (self, volume):
    """Sets the volume level"""

    self.volume = volume
    self.limit_volume ()


  def adjust_volume (self, adjustment):
    """Adjusts the volume level"""

    self.volume += adjustment
    self.limit_volume ()


  def limit_volume (self):
    """Ensures the volume is within the allowed range"""

    self.volume = min (self.volume, self.max_volume)
    self.volume = max (self.volume, self.min_volume)


  def apply (self):
    """Applies the changes"""

    self.run ("set-sink-mute %d %d" % (self.sink, self.mute))
    self.run ("set-sink-volume %d %d%%" % (self.sink, self.volume))


  def run (self, command):
    """Runs a pactl command"""

    os.system ("%s -- %s" % (self.pactl, command))


  def awesome (self):
    """Informs the awesome widget of the status"""

    mute = "true" if self.mute else "false"
    command = 'volumewidget.callback (%d, %s, "%s")' % (self.volume, mute, self.get_icon ())

    p1 = subprocess.Popen (['echo', command], stdout=subprocess.PIPE)
    p2 = subprocess.Popen (['awesome-client'], stdin=p1.stdout)

    p1.stdout.close ()
    p2.communicate ()


  def get_icon (self):
    """Returns the icon to pass to awesome"""

    if self.volume == 100:
      icon = "volume-high"
    elif self.volume >= 50:
      icon = "volume-medium"
    elif self.volume > 0:
      icon = "volume-low"
    else:
      icon = "volume-zero"

    if self.mute:
      icon += "-muted"

    return icon


  def print_status (self):
    """Prints the current status"""

    status = "Volume: %d%%" % self.volume

    if self.mute == True:
      status += " (mute)"

    print status


if __name__ == "__main__":
  Volume ().main ()
