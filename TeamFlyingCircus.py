import math
import random
import os
import glob
import sys, traceback
import time
import threading 
import serial
import re
import struct
##
import cairo
##
import TeamFlyingCircus



class TeamFlyingCircus(threading.Thread):
    """ Das ist Eure Funktionsklasse, hier kommt alles rein, was speziell Euer Team betrifft. In den Eventhandler-Funktionen bitte keine komplizierten Berechnungen durchführen, sondern nur flags setzen, da diese von einem anderen Thread berechnet werden müssten und diesen evtl. blockieren würden(=>GUI hängt, etc.). Die run-Funktion wird in Eurem Thread ausgeführt, da kommen die Berechnungen rein. Zugriff auf die gui oder arduino habt Ihr über self.main.gui bzw. self.main.arduino """
    def __init__(self, main):
        threading.Thread.__init__(self) 
        self.main = main
        print("TeamFlyingCircus")
        self.run_ = True
        self.start_ = 0
        self.currentWP = 0
        self.buffer0 = 0
        self.buffer1 = 0
        self.buffer2 = 0
        self.distance = 0
        self.angle_north = 0
        self.raw_local_x = 0
        self.raw_local_y = 0
        self.bufferlist_1_x = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.bufferlist_1_y = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.bufferlist_2_x = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.bufferlist_2_y = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.buffercount = 0
        self.buff = 10
        #threading.Thread.__init__(self) #p-initialisierung der vererbten Fähigkeit threading der Klasse Thread.
        #self.ttylock = threading.Lock()
        self.bob = serial.Serial("/dev/ttyUSB1", 115200, 8, 'N', 1, 0.0001)
        self.bob.flushInput() #flush input buffer, discarding all its contents
        self.bob.flushOutput()#flush output buffer, aborting current output 
    def run(self):
        #i=0
        while(self.run_):
            #i=i+1
            #print("TeamFlyingCircus run:",i)
            self.loop()
    def loop(self):
        if (self.start_):
            #wegpunktnavigation etc.
            #self.main.arduino.send("TeamFlyingCircus fliegt!\n")
            pass
        time.sleep(0.005) #schlafen ist gut, um die CPU nicht voll auszulasten
    def onStart(self):
        #Start-Button wurde gedrückt
        self.start_ = 1
        pass
    def onStop(self):
        #Stop-Button wurde gedrückt
        self.start_ = 0
        # reset etc.
        pass
    def onNewPos(self):
        print("yahoooooooooooo")
        self.main.doppel = self.main.doppel + 1
        send1 = " "
        self.raw_local_x = 0
        self.raw_local_y = 0
        
        if (self.main.doppel%2==0 and (buffer2 + self.main.rawPos[2])/2 > 200):
          #filter over 20
          self.bufferlist_1_x[self.buffercount] = self.buffer0
          self.bufferlist_1_y[self.buffercount] = self.buffer1
          self.bufferlist_2_x[self.buffercount] = self.main.rawPos[0]
          self.bufferlist_2_y[self.buffercount] = self.main.rawPos[1]
          self.buffercount = self.buffercount + 1
          if(self.buffercount > self.buff):
            self.buffercount = 0

          filterd_1_x = sum(self.bufferlist_1_x)/self.buff
          filterd_1_y = sum(self.bufferlist_1_y)/self.buff
          filterd_2_x = sum(self.bufferlist_2_x)/self.buff
          filterd_2_y = sum(self.bufferlist_2_y)/self.buff

          #create global x,y
          self.main.filterdPos[0] = (filterd_1_x + filterd_2_x)/2
          self.main.filterdPos[1] = (filterd_1_y + filterd_2_y)/2
          self.main.filterdPos[2] = 700
          
          #create distance and northern angle to next waypoint
          buf0 = self.main.waypoints[self.currentWP][0] - self.main.filterdPos[0]
          buf1 = self.main.waypoints[self.currentWP][1] - self.main.filterdPos[1]
          
          self.distance = (buf0**2+buf1**2)**(0.5)
          self.angle_north = 180 / math.pi * (math.asin((-1)*buf0/self.distance))

          print(self.distance)
          print(self.angle_north)
          
          #formatting
          buf0 = self.distance
          buf1 = self.angle_north
          
          if(buf0 < 0):
            buf0 += 65536
          if(buf1 < 0):
            buf1 += 65536
          
          bybuf0 = chr(int(buf0%256))
          bybuf2 = chr(int(buf1%256))
          bybuf1 = chr(int(buf0/256))
          bybuf3 = chr(int(buf1/256))
           
          if ((self.local_x**2+self.local_y**2) < 600):
            self.currentWP = self.currentWP + 1
        
          #self.ttylock.acquire()
          self.bob.write(bytes(('{a}{b}{c}{d}'.format(a=bybuf0, b=bybuf2, c=bybuf1, d=bybuf3)).encode('UTF-8')))
          self.bob.flush()
          #self.ttylock.release()

        self.buffer0 = self.main.rawPos[0]
        self.buffer1 = self.main.rawPos[1]
        self.buffer2 = self.main.rawPos[2]
        pass

    def onButtonPressed(self, i):
        #welcher Button welche Nummer hat seht Ihr in der glade Datei oder im Eventhandler oder durch Testen
        #print("Button ", i)
        pass
    def onWaypointUpdate(self):
        #wegpunkt wurde in der gui geändert
        pass
    def onObstacleUpdate(self):
        pass
    def onExit(self):
        # Programm beenden
        self.run_=False
        pass
    def setkurswinkelflag(self):
        self.kurswinkelflag = True
