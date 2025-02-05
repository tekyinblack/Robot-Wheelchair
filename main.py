# wheelchair web server
# based on Pico W documentation and RNT examples
# First working version 250131
# v4 commented version
# v5 first changed version
#    added indicator led to main loop
#    added termination code to end cleanly
# v6 move motor definitions to thread
#    added additional final code to handle cancellation, seen ioctl error for first time in this code
#    moved connection close to exit routine, only drain on response, speed improved, only 5-6 commands before crash
#    added garbage collection to recycle memory following web page response
# v7 experiments in ioctl error, inconclusive
#    remove response except for refresh
# v8 add hostname 
import network
import asyncio
import socket
import time
from machine import Pin
import _thread
from chair_webpages_comp3 import webpages
import gc
from stepmotor import Stepmotor
import utime

# Wi-Fi credentials
ssid = 'Wheel'   # <<<<<<<<<<<<<<<<<< Update before using
password = 'Chair'

# load initial webpage to use
newpages = webpages()
response = newpages.steerpage()

# initial sleep to give time to reset pico before threads start
# avoids accidental lockouts
time.sleep(5)

# hostname
newhostname = "WheelChair"

# onboard indicator led to show activity
led_indicator = machine.Pin("LED", machine.Pin.OUT)

# Initialize variables
# default mode is wifi steering
state = "STEERING"

# left and right wheel direction 0 is forward, 1 reverse
dir_left = 0
dir_right = 0

# length of stepper motor pulse 2000uS normal, >=9999 used to indicate halt
step_time = 9999

finished = False

# stepper driver thread
def runstepper():
    global finished
    global left_wheel
    finished = False
    left_wheel = Stepmotor(2,3,4,5)
    right_wheel = Stepmotor(10,11,12,13)
    while not finished:
        global dir_left
        global dir_right
        if step_time < 9999:
            left_wheel.moveOneStep(dir_left)
            right_wheel.moveOneStep(dir_right)
            time.sleep_us(step_time)
        else:
            left_wheel.stop()
            right_wheel.stop()
    
    
# Init Wi-Fi Interface
def init_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    network.hostname(newhostname)
    # Connect to your network
    wlan.connect(ssid, password)
    # Wait for Wi-Fi connection
    connection_timeout = 10
    while connection_timeout > 0:
        print(wlan.status())
        if wlan.status() >= 3:
            break
        connection_timeout -= 1
        print('Waiting for Wi-Fi connection...')
        time.sleep(1)
    # Check if connection is successful
    if wlan.status() != 3:
        print('Failed to connect to Wi-Fi')
        return False
    else:
        print('Connection successful!')
        network_info = wlan.ifconfig()
        print('IP address:', network_info[0])
        return True

# Asynchronous function to handle client's requests
async def handle_client(reader, writer):
    global state
    global finished
    global dir_left 
    global dir_right
    global step_time 
    
    print("Client connected")
    request_line = await reader.readline()
    print('Request:', request_line)
    
    # Skip HTTP request headers
    while await reader.readline() != b"\r\n":
        pass
    
    request = str(request_line, 'utf-8').split()[1]
    print('Request1:', request)
    if request != "/":
        # handle the icon request that slips through occasionally
        if request != "/favicon.ico":
            request = request.split('=')[1]
            print('Request2:', request)
    
    # Process the request and update variables
    if request == 'EXIT':
        finished = True
        print('Exit command received.')
        await writer.wait_closed()
        loop.stop()
    elif request == 'STOP':
        step_time = 9999
    elif request == 'FWD':
        step_time = 9999
        dir_left = 0
        dir_right = 0
        step_time = 2000
    elif request == 'REV':
        step_time = 9999
        dir_left = 1
        dir_right = 1
        step_time = 2000
    elif request == 'LEFT':
        step_time = 9999
        dir_left = 1
        dir_right = 0
        step_time = 2000
    elif request == 'RIGHT':
        step_time = 9999
        dir_left = 0
        dir_right = 1
        step_time = 2000
    elif request == 'STEERING':
        state = "STEERING"
    elif request == 'FOLLOW':
        state = "FOLLOW"
    elif request == '/':
    # Send the HTTP response and close the connection
        writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        writer.write(response)
        await writer.drain()
 # we olnly send a response on request, otherwise the web page script sends the next command
    gc.collect() # <---------- garbage collection to check on overloaded memory

async def main():    
    if not init_wifi(ssid, password):
        print('Exiting program.')
        return
    

    # Start the server and run the event loop
    print('Setting up server')
    server = asyncio.start_server(handle_client, "0.0.0.0", 80)
    asyncio.create_task(server)
    
    while True:
        # Flash the LED to keep things ticking over
        led_indicator.toggle()  # Toggle LED state
        await asyncio.sleep(0.5)  # Blink interval

            
# dispatch stepper driver thread            
_thread.start_new_thread(runstepper, ())        

# Create an Event Loop
loop = asyncio.get_event_loop()
# Create a task to run the main function
loop.create_task(main())

try:
    # Run the event loop indefinitely
    loop.run_forever()
except Exception as e:
    print('Error occured: ', e)
except KeyboardInterrupt:
    print('Program Interrupted by the user')
finally:
    finished = True
    print ("Program waiting to end")
    # hang around to let threads end
    time.sleep(1)
