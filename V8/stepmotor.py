from machine import Pin
import time

phasecw  = [0x08,0x04,0x02,0x01]
phaseccw = [0x01,0x02,0x04,0x08]
#out=0x01

class Stepmotor(object):
    def __init__(self, A: int=21, B: int=20, C: int=19, D: int=18):
        self._A = Pin(A,Pin.OUT,0)
        self._B = Pin(B,Pin.OUT,0)
        self._C = Pin(C,Pin.OUT,0)
        self._D = Pin(D,Pin.OUT,0)
        self.out = 0x01
        
    def _motorcontrol(self,data):
        if data == 0x08:
            self._A.on()
            self._B.off()
            self._C.off()
            self._D.off() 
        if data == 0x04:
            self._A.off()
            self._B.on()
            self._C.off()
            self._D.off()       
        if data == 0x02:
            self._A.off()
            self._B.off()
            self._C.on()
            self._D.off()     
        if data == 0x01:
            self._A.off()
            self._B.off()
            self._C.off()
            self._D.on()   
        if data == 0x00:
            self._A.off()
            self._B.off()
            self._C.off()
            self._D.off()
            
    def moveOneStep(self,direction):
        #global out
        if direction == 1:
            if self.out != 0x08:
                self.out = self.out<<1
            else:
                self.out = 0x01
        else:
            if direction == 0:
                if self.out != 0x01:
                    self.out = self.out >> 1
                else:
                    self.out = 0x08
        self._motorcontrol(self.out)
        
    def moveSteps(self, direction, steps, us):
        for i in range(steps):
            self.moveOneStep(direction)
            time.sleep_us(us)

    def moveAround(self,direction, turns, us):
        for i in range(turns):
            self.moveSteps(direction, 32*64,us)
    
    def moveAngle(self, angles, us):
        self.moveSteps(direction, 32*64//angles, us)
        
    def stop(self):
        self._motorcontrol(0x00)

    

            
