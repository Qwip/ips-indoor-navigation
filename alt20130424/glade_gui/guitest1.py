#!/usr/bin/env python3
# -*- coding: iso-8859-1 -*-
from gi.repository import Gtk,Gdk, GLib
import math
import random
import os
import glob
import sys, traceback
import time
from ctypes import *

dir = os.path.dirname(__file__)
multilat=CDLL(os.path.join(dir, 'multilat.so'))

stations = [[0 for col in range(5)] for row in range(10)]

stations[0][0] = 0
stations[0][1] = 0
stations[0][2] = 0
stations[1][0] = 0
stations[1][1] = 0
stations[1][2] = 0
stations[2][0] = 1665
stations[2][1] = 0
stations[2][2] = 0
stations[3][0] = 0
stations[3][1] = 0
stations[3][2] = 0
stations[4][0] = 0
stations[4][1] = 3020
stations[4][2] = 470
stations[5][0] = 1665
stations[5][1] = 3020
stations[5][2] = 0

posx = 0.0
posy = 0.0
posz = 1000.0


# The number of circles and the window size.
num = 6
size = 512
red = 1
green = 0
blue = 0
# Initialize circle coordinates and velocities.
x = []
y = []
xv = []
yv = []
for i in range(num):
    x.append(random.randint(0, size))
    y.append(random.randint(0, size))
    if i < 5:
        xv.append(0)
        yv.append(0)
    if i > 4:
        xv.append(random.randint(-4, 4))
        yv.append(random.randint(-4, 4))
    
def clib_multilat():
    global posx
    global posy
    global posz
    numstations = 0
    millis = int(round(time.time() * 1000))
    for station in stations:
        if (millis - station[4]) < 1500:
            numstations += 1
    if (numstations > 2):
        i = -1
        #cstationtype = c_double * 3 * numstations
        #cradiustype = c_double * numstations
        cstationtype = c_double * 3 * 10
        cradiustype = c_double * 10
        cstarttype = c_double * 3
        cstations = cstationtype((0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0))
        cradii = cradiustype(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        cstartpos = cstarttype(posx, posy, posz)
        cnn = c_int (numstations)
        for station in stations:
            if (millis - station[4]) < 1500:
                i += 1
                cstations[i][0] = c_double(station[0])
                cstations[i][1] = c_double(station[1])
                cstations[i][2] = c_double(station[2])
                cradii[i] = c_double(station[3])

        x = c_double
        y = c_double
        z = c_double
        deltar = c_double
        multilat.wrapper.restype=c_double
        

        deltar = multilat.wrapper(cstations, cstartpos, cradii, cnn, byref(x), byref(y), byref(z))

        posx = x.value
        posy = y
        posz = z
        print posx, posy, posz  


class arduino:
  def __init__(self,main):
    self.main = main
    self.s = serial.Serial(self.main.ttyport, 115200, 8, 'N', 1, 0.05)
    self.s.flush()
    self.pattern = re.compile(r"deltat from (\d+) - (\d+) - (\d+\.\d+)")
  def run(self):
    if (self.s.inWaiting() > 0):
      self.recv_packet() 
      clib_multilat()
    time.sleep(0.005)
  def setled(self, led, state):
    self.s.write("\x02" + led + chr(state) + "\x03")
    self.s.flush()
    self.recv_packet()
  def recv_packet(self):
    if (self.s.inWaiting() > 0):
      res = self.s.readline()
      print res
      tmp = self.pattern.search(res)
      if tmp is not None:
        deltat = float(tmp.group(2))
        deltat = deltat * 0.34
        if deltat > 1:
            stationnr = int(tmp.group(1))
            millis = int(round(time.time() * 1000))
            stations[stationnr][3] = deltat
            stations[stationnr][4] = millis

  def reset(self):
    self.s.setDTR(False)
    time.sleep(0.00001)
    self.s.setDTR(True)


class init():
    def __init__(self, main):
        self.main = main
        print(self.main.ttyport,self.main.team)
        builder = Gtk.Builder()
        #builder.add_from_file("/home/alex/ips/glade_gui/daedalus.glade")
        builder.add_from_file(os.path.join(dir, 'daedalus.glade'))
        builder.connect_signals(EventHandler())
        window = builder.get_object("window2")
        self.ttybox = builder.get_object("buttonbox4")
        self.teambox = builder.get_object("buttonbox5")
        reloadbtn = builder.get_object("button12")
        reloadbtn.connect("pressed", self.reloadtty)
        self.reloadtty("")
        # TODO add your team here
        button1 = Gtk.RadioButton(group=None, label="Alex")
        button1.connect("toggled", self.setteam, "TeamX")
        self.teambox.pack_start(button1, True, True, 0)
        self.main.team = "TeamX"
        button = Gtk.RadioButton(group=button1, label="Team1")
        button.connect("toggled", self.setteam, "Team1")
        self.teambox.pack_start(button, True, True, 0)
        button = Gtk.RadioButton(group=button1, label="Team2")
        button.connect("toggled", self.setteam, "Team2")
        self.teambox.pack_start(button, True, True, 0)
        button = Gtk.RadioButton(group=button1, label="Team3")
        button.connect("toggled", self.setteam, "Team3")
        self.teambox.pack_start(button, True, True, 0)
        
        # end: add team
        window.show_all()
        Gtk.main()
    def setttydev(self, button, dev):
        if button.get_active():
            self.main.ttyport = dev
            print("tty=",self.main.ttyport)
    def setteam(self, button, team_):
        if button.get_active():
            self.main.team = team_
            print("team=",self.main.team)
    def reloadtty(self, button):
        #ladde tty ports
        ttydevs = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyS*')
        for i in self.ttybox.get_children():
            self.ttybox.remove(i)
        if len(ttydevs) == 0:
          print ("error: no tty Port")
        else:
          button = None
          for item in ttydevs:
            if button == None:
                self.main.ttyport = item
            button = Gtk.RadioButton(group=button, label=item)
            button.connect("toggled", self.setttydev, item)
            self.ttybox.pack_start(button, True, True, 0)
            self.ttybox.show_all()



class TeamX():
    def __init__(self, main):
        self.main = main
        print("TeamX")
        self.run = 1
        self.start = 0
    def run(self):
        i=0
        while(run):
            i=i+1
            print("team run:",i)
            if (start):
                #wegpunktnavigation
                pass
                
    def onStart(self):
        self.start = 1
        pass
    def onStop(self):
        self.start = 0
        pass
    def onNewPos(self):
        pass
    def onButtonPressed(self, i):
        print(i)
        pass
    def onWaypointUpdate(self):
        pass
    def onObstacleUpdate(self):
        pass
    def onExit(self):
        self.run=0
        pass


def do_expose_event(widget, cr):
    global red
    global green
    global blue
    #cr = self.window.cairo_create()

    # Restrict Cairo to the exposed area; avoid extra work


    cr.set_line_width(4)
    for i in range(num):
        cr.set_source_rgb(red, green, blue)
        cr.arc(x[i], y[i], 8, 0, 2 * math.pi)
        cr.stroke_preserve()
        cr.set_source_rgb(1, 1, 1)
        cr.fill()
        x[i] += xv[i]
        y[i] += yv[i]
        if x[i] > size or x[i] < 0:
            xv[i] = -xv[i]
        if y[i] > size or y[i] < 0:
            yv[i] = -yv[i]
    widget.queue_draw()


class GraphicalUserInterface():
    global team
    global waypointlist
    global obstaclelist
    global stationlist
    global builder
    def __init__(self, main):
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(dir, 'daedalus.glade'))
        builder.connect_signals(EventHandler())
        window = builder.get_object("window1")
        drawingarea = builder.get_object("drawingarea1")
        waypointlist = builder.get_object("liststore1")
        obstaclelist = builder.get_object("liststore2")
        stationlist = builder.get_object("liststore3")
        drawingarea.queue_draw()
        window.show_all()
        pass
    def run(self):
        Gtk.main()
        pass
    def draw(self):
        pass
    def drawWaypoints(self):
        pass
    def drawStations(self):
        pass
    def drawObstacles(self):
        pass
    def drawPositions(self):
        pass
    def drawStations(self):
        pass
    def drawLegend(self):
        pass


class EventHandler:
    global team
    global waypointlist
    global obstaclelist
    global stationlist
    global builder
    #menu
    def on_imagemenuitem5_activate(self, *args):
        #beenden
        Gtk.main_quit(*args)
    def on_imagemenuitem1_activate(self, *args):
        #neu TODO
        pass
    def on_imagemenuitem2_activate(self, *args):
        #öffnen TODO
        pass
    def on_imagemenuitem3_activate(self, *args):
        #speichern TODO
        pass
    def on_imagemenuitem4_activate(self, *args):
        #speichern unter TODO
        pass
    def on_imagemenuitem10_activate(self, *args):
        #hilfe info about TODO
        pass
    #window
    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)
    def on_window1_destroy(self, *args):
        Gtk.main_quit(*args)
    def on_window2_destroy(self, *args):
        Gtk.main_quit(*args)
    def on_window2_delete_event(self, *args):
        Gtk.main_quit(*args)
    #drawingarea
    def on_drawingarea1_draw(self, *args):
        do_expose_event(*args)
    #TODO
    #buttons
    def on_button1_pressed(self, *args):
        #wp add TODO: Nummern anpassen
        team.onButtonPressed(1)
        waypointlist.append((11, 111, 222, 333, "neu"))
        team.onWaypointUpdate()
    def on_button2_pressed(self, *args):
        #wp remove TODO: Nummern anpassen
        team.onButtonPressed(2)
        model, treeiter = builder.get_object("treeview-selection").get_selected()
        model.iter_next(treeiter)
        model.remove(treeiter)
        team.onWaypointUpdate()
    def on_button3_pressed(self, *args):
        #wp rauf  TODO: Nummern anpassen
        team.onButtonPressed(3)
        model, treeiter = builder.get_object("treeview-selection").get_selected()
        prev = model.iter_previous(treeiter)
        if prev:
            model.swap(treeiter, prev)
        team.onWaypointUpdate()
    def on_button4_pressed(self, *args):
        #wp runter TODO: Nummern anpassen
        team.onButtonPressed(4)
        model, treeiter = builder.get_object("treeview-selection").get_selected()
        next = model.iter_next(treeiter)
        if next:
            model.swap(treeiter, next)
        
        team.onWaypointUpdate()
    def on_button5_pressed(self, *args):
        #wp springe zu TODO
        team.onButtonPressed(5)
    def on_button11_pressed(self, *args):
        #hindernis add TODO
        team.onButtonPressed(11)
    def on_button14_pressed(self, *args):
        #hindernis remove TODO
        team.onButtonPressed(14)
    def on_button6_pressed(self, *args):
        #start
        team.onStart()
        team.onButtonPressed(6)
    def on_button7_pressed(self, *args):
        #stop
        team.onStop()
        team.onButtonPressed(7)
    def on_button8_pressed(self, *args):
        #abstürzen
        team.onButtonPressed(8)
    def on_button9_pressed(self, *args):
        #bombe
        team.onButtonPressed(9)
    def on_button10_pressed(self, *args):
        #kreis
        team.onButtonPressed(10)
    def on_button12_pressed(self, *args):
        #init reload 
        pass
    def on_button13_pressed(self, *args):
        #init go
        pass
    def on_button15_pressed(self, *args):
        #edit wp TODO
        team.onButtonPressed(15)
    def on_button16_pressed(self, *args):
        #edit obstacle TODO
        team.onButtonPressed(16)
    def on_button17_pressed(self, *args):
        #edit station TODO
        team.onButtonPressed(17)

    #edited
    def on_cellrenderertext2_edited(self, widget, path, text):
        #wp x
        waypointlist[path][1] = int(text)
        team.onWaypointUpdate()
        pass
    def on_cellrenderertext3_edited(self, widget, path, text):
        #wp y
        waypointlist[path][2] = int(text)
        team.onWaypointUpdate()
        pass
    def on_cellrenderertext4_edited(self, widget, path, text):
        #wp z
        waypointlist[path][3] = int(text)
        team.onWaypointUpdate()
        pass
    def on_cellrenderertext16_edited(self, widget, path, text):
        #wp typ
        waypointlist[path][4] = text
        team.onWaypointUpdate()
        pass
    def on_cellrenderertext5_edited(self, widget, path, text):
        #hindernis x
        obstaclelist[path][0] = int(text)
        team.onObstacleUpdate()
        pass
    def on_cellrenderertext6_edited(self, widget, path, text):
        #hindernis y
        obstaclelist[path][1] = int(text)
        team.onObstacleUpdate()
        pass
    def on_cellrenderertext7_edited(self, widget, path, text):
        #hindernis z
        obstaclelist[path][2] = int(text)
        team.onObstacleUpdate()
        pass
    def on_cellrenderertext8_edited(self, widget, path, text):
        #hindernis r
        obstaclelist[path][3] = int(text)
        team.onObstacleUpdate()
        pass
    def on_cellrenderertext10_edited(self, widget, path, text):
        #station x
        stationlist[path][1] = int(text)
        pass
    def on_cellrenderertext11_edited(self, widget, path, text):
        #station y
        stationlist[path][2] = int(text)
        pass
    def on_cellrenderertext12_edited(self, widget, path, text):
        #station z
        stationlist[path][3] = int(text)
        pass

    def onx(self, *args):
        #
        pass


class main():
    def __init__(self):
        self.team = ""
        self.ttyport = ""
        self.waypointlist = ""
        self.obstaclelist = ""
        self.stationlist = ""
        self.builder = ""
        init(self)
        if self.team and self.ttyport:
          if self.team == "TeamX":
            self.team = TeamX(self)
          if self.team == "Team1":
            self.team = Team1(self)
          if self.team == "Team2":
            self.team = Team2(self)
          if self.team == "Team3":
            self.team = Team3(self)
        else:
            print("init failed, please specify a tty port and a team")
            print(self.ttyport,self.team)
            sys.exit() 
        builder = Gtk.Builder()
        #builder.add_from_file("/home/alex/ips/glade_gui/daedalus.glade")
        builder.add_from_file(os.path.join(dir, 'daedalus.glade'))
        builder.connect_signals(EventHandler())
        window = builder.get_object("window1")
        drawingarea = builder.get_object("drawingarea1")
        waypointlist = builder.get_object("liststore1")
        obstaclelist = builder.get_object("liststore2")
        stationlist = builder.get_object("liststore3")
        drawingarea.queue_draw()
        window.show_all()
        Gtk.main()


if __name__ == "__main__":
    main()