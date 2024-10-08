# -*- coding: utf-8 -*-
"""
Created on Jul 25, 2015

Thanks to Lex Wernars

@author: jrm
@author: lwernars
"""
from atom.api import Enum, Instance, Float
from inkcut.device.plugin import DeviceProtocol, Model


class DMPLConfig(Model):
    #: Version number
    mode = Enum(1, 2, 3, 4, 6, 7).tag(config=True)


class DMPLProtocol(DeviceProtocol):

    #: Different modes
    config = Instance(DMPLConfig, ()).tag(config=True)

    #: Output scaling
    scale = Float(1021/90.0)

    def connection_made(self):
        v = self.config.mode
        if v == 1:
            self.write(";:HAEC1")
        elif v == 2:
            self.write(" ;:ECN A L0 ")
        elif v in [3, 4]:
            self.write(" ;:H A L0 ")
        elif v == 6:
            self.write("IN;PA;")
        elif v==7:
            # Send the initialization commands without leading whitespace to ensure proper com initialization
            self.write(";:H A L0 ECN U ")

    def move(self, x, y, z, absolute=True):
        x, y = int(x*self.scale), int(y*self.scale)
        # Only protocol 6 requires PD and PU commmans.
        if self.config.mode==6:
            self.write("{z}{x},{y};".format(x=x, y=y, z=z and "PD" or "PU"))
        else:
            self.write(" {z}{x},{y} ".format(x=x, y=y, z=z and "D" or "U"))

    def set_pen(self, p):
        self.write("EC{p} ".format(p=p))

    def set_velocity(self, v):
        self.write("V{v} ".format(v=v))

    def set_force(self, f):
        self.write("BP{f} ".format(f=f))

    def connection_lost(self):
        pass

    def finish(self):
        if self.config.mode==7:
            # Properly end the transmission to avoid locking up the cutter interface with "Waiting..." message
            self.write(" U F @ ")
