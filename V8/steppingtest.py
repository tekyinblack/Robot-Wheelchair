from stepmotor import Stepmotor
import time

myStepMotor = Stepmotor(2, 3, 4, 4)
#myStepMotor = Stepmotor(10,11,12,13)

try:
    while True:  
        myStepMotor.moveSteps(1, 32*64, 2000)
        myStepMotor.stop()
        time.sleep(1)
        myStepMotor.moveSteps(0, 32*64, 2000)
        myStepMotor.stop()
        time.sleep(1)
except:
    pass
    
    
    
    
    
    
    
    
    
    
    

    
    
