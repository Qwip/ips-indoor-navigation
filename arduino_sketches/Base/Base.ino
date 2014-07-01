//Base station v0.9.1  20130704 1300
#define VERSION "alpha"
#define DEVICEID 0

#define VERSIONMAJOR 0
#define VERSIONMINOR 9

#include <SPI.h>
#include <Mirf.h>
#include <nRF24L01.h>
#include <MirfHardwareSpiDriver.h>
#include <stdio.h>
#include <stdlib.h>

// NRF24 settings
#define RFADDR "base"
#define RFBASE "Bloon"
#define RFCHANNEL 30
#define PAYLOAD 12

//constants
const byte MYID = DEVICEID;
const byte Version[2] = {VERSIONMAJOR,VERSIONMINOR};
const byte MAXSTATIONS = 15;

// Global Variables
int PID = 5;
int state = 0;

byte sending[PAYLOAD] = {1};
byte receiving[PAYLOAD] = {0};
unsigned long timer = 0;
unsigned long interval = 2000;
char menu;
byte count;
int wpx, wpy;
byte sollh, Pack;


void consend(byte data[PAYLOAD])
{
  Mirf.send(data);
  while(Mirf.isSending()){
  }

  if(Mirf.dataReady())
  {
    Mirf.getData(receiving);
  }
}


void setup() {
  Serial.begin(115200);
  Serial.print("Balloon Control ");
  Serial.println(VERSION);
  //init NRF24
  Mirf.spi = &MirfHardwareSpi;
  Mirf.cePin = 9;
  Mirf.csnPin = 10;
  Mirf.init();
  Mirf.setRADDR((byte *)RFADDR);
  Mirf.setTADDR((byte *)RFBASE);
  Mirf.payload = 12;
  Mirf.channel = RFCHANNEL;
  Mirf.config();
  state = 0;
  
}


void loop()
{
  switch (state)
  {
    case 0: //initialize coordinates
      
      sending[0] = 30;
      sending[1] = 0;
      sending[2] = 0;
      sending[3] = 0;
      sending[4] = 0;
      sending[5] = 0;
      count = 0;
      state = 3;
      break;
      
    case 2: //send data
      
      consend(sending);
      
      Serial.print("X");
      for(int i=0; i<10; i++)
      {
        Serial.print(receiving[i]);
        Serial.print("Q");
      }
      
      state = 3;      
      break;
      
    case 3: //listen and relay
      while(Mirf.isSending()) {
      }
      
    
      if (Serial.available() > 0) 
      {
          state = 4;
      }
      state = 2;
      delay(50);
      break;
    
    case 4: //read serial
      
      if(Serial.available() > 5) 
      {
        for(int n=0; n<4; n++)
          sending[n+2]= Serial.read();
        sending[8] = Serial.read();
        sending[9] = Serial.read();
      }
      
      state = 2;
      break;
  }
}
