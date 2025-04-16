module_name = 'PIO_Stepper.py'
# developed by Colin Walls
# enhanced by tekyinblack
import time
import rp2
from machine import Pin

@rp2.asm_pio()
def count_it():
    mov(y,invert(null))
    label('loop')
    wait(1,irq,rel(0))
    jmp(y_dec,'loop')

class Counter():
    def __init__(self, state_machine_no=5, frequency=320000):
        self.sm = rp2.StateMachine(state_machine_no, count_it, freq=frequency)
        self.sm.active(1)
    def __call__(self):
        self.sm.active(0)
        self.sm.exec('mov(isr,invert(y))')
        self.sm.exec('push()')
        self.sm.active(1)
        return(self.sm.get())
    def rx_fifo(self):
        return self.sm.rx_fifo()
    def close(self):
        self.sm.active(0)

@rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW))
def step_it():
    pull()        #  Blocking pull of bit pattern
    mov(x,osr)    #  Save in x
    pull()        #  Blocking pull of delay loop
    mov(isr,osr)  #  Save in ISR
    label('main_loop')
    mov(osr,x)    #  Reload bit pattern
    label('inner_loop')
    out(pins,4)   #  Set stepper GPIOs to bit pattern
    mov(y,isr)    #  Reload delay loops
    label('delay_loop')
    nop()
    jmp(y_dec,'delay_loop')
    jmp(not_osre,'inner_loop')
    irq(rel(1))        #  Set every 8 iterations
    jmp('main_loop')

class Stepper():
    def __init__(self, base_pin_no=18, state_machine_no=4, frequency=64000,
                 speed_factor=33, delay_adjust=2,hsc=0x8a264519,fsc=0x82418241,
                 hsac=0x915462a8,fsac=0x14281428):
        self.frequency = frequency
        self.base_pin_no = base_pin_no
        self.sm = rp2.StateMachine(state_machine_no, step_it, freq=frequency, out_base=Pin(base_pin_no))
        self.speed_factor = speed_factor   #  'Magic' number. Depends on the actual servo
        self.delay_adjust = delay_adjust   #   Ditto
        self.half_step = True
        self.half_step_cw = hsc
        self.half_step_acw = hsac
        self.full_step_cw = fsc
        self.full_step_acw = fsac
    def __call__(self, speed=50, direction='C', half_step=False):
        #  speed is in range 0 to 99. 0 means stop
        #  direction is 'C' for clockwise, or anything else for anticlockwise
        self.half_step = half_step

        if direction == 'C':
            if self.half_step:
                bit_pattern = self.half_step_cw
            else:
                bit_pattern = self.full_step_cw
        else:
            if self.half_step:
                bit_pattern = self.half_step_acw
            else:
                bit_pattern = self.full_step_acw
        if speed > 99:
            speed = 99
        elif speed < 1:
            bit_pattern = 0x00000000
            speed = 1
 
        delay = int(float(self.frequency) / (float(speed) * self.speed_factor)) + self.delay_adjust
        if not half_step:
            delay = delay * 2
        if self.sm.active():
            self.sm.restart()
        else:
            self.sm.active(1)
        self.sm.put(bit_pattern)
        self.sm.put(delay)
    def float_steppers(self):
        self.sm.active(0)
        Pin(self.base_pin_no, Pin.IN)
        Pin(self.base_pin_no + 1, Pin.IN)
        Pin(self.base_pin_no + 2, Pin.IN)
        Pin(self.base_pin_no + 3, Pin.IN)
    def close(self):
        self.float_steppers()

class ST35ST26(Stepper):
    def __init__(self, base_pin_no=18, state_machine_no=0, frequency=64000, half_step=True):
        super().__init__(base_pin_no=base_pin_no,
                         state_machine_no=state_machine_no,
                         frequency=frequency,
                         speed_factor = 33,
                         delay_adjust = 2)
        
class S28byj_48(Stepper):
    def __init__(self, base_pin_no=2, state_machine_no=0, frequency=64000, half_step=False):
        super().__init__(base_pin_no=base_pin_no,
                         state_machine_no=state_machine_no,
                         frequency=frequency,
                         speed_factor = 33,
                         delay_adjust = 2,
                         hsc=0x8a264519,
                         fsc=0x84218421,
                         hsac=0x915462a8,
                         fsac=0x12481248)
        

if __name__ == '__main__':
    print (module_name)
