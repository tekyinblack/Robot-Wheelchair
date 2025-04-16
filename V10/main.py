# wheelchair web server by tekyinblack
# based on Pico W documentation 
# v9 converted to PIO from idea by Colin Walls
# v10 move to encapsulated stepper definitions
import network
import asyncio
import socket
import time
from machine import Pin
import _thread
from chair_webpages_comp4 import webpages
import gc
import rp2
import PIO_Stepper2
import utime

# load initial webpage to use
newpages = webpages()
response = newpages.steerpage()

# initial sleep to give time to reset pico before threads start
# avoids accidental lockouts
time.sleep(5)

# Wi-Fi credentials
ssid = 'tekyinblack.com'
password = 'warehouse'

newhostname = "WheelChair"

# onboard indicator led to show activity
led_indicator = machine.Pin("LED", machine.Pin.OUT)

# Initialize variables
# default mode is wifi steering
state = "STEERING"

# length of stepper motor pulse 2000uS normal, >=9999 used to indicate halt
step_time = 9999

finished = False

left_wheel = PIO_Stepper2.S28byj_48(base_pin_no=2, state_machine_no=0)
right_wheel = PIO_Stepper2.S28byj_48(base_pin_no=10, state_machine_no=2)

def forward():
    left_wheel(70,'A')
    right_wheel(70,'A')
    
def stop():
    left_wheel(0)
    right_wheel(0)
    
def reverse():
    left_wheel(70,'C')
    right_wheel(70,'C')
    
def left():
    left_wheel(35,'C')
    right_wheel(35,'A')
    
def right():
    left_wheel(35,'A')
    right_wheel(35,'C')
    
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
        stop()
    elif request == 'FWD':
        forward()
    elif request == 'REV':
        reverse()
    elif request == 'LEFT':
        left()
    elif request == 'RIGHT':
        right()
    elif request == 'STEERING':
        state = "STEERING"
    elif request == 'FOLLOW':
        state = "FOLLOW"
    #elif request == '/':
    # Send the HTTP response and close the connection
    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(response)
    await writer.drain()
 # we onnly send a response on request, otherwise the web page script sends the next command
    gc.collect() # <---------- garbage collection to check on overloaded memory

async def main():    
    if not init_wifi(ssid, password):
        print('Exiting program.')
        return
    
    #init_machine()    

    # Start the server and run the event loop
    print('Setting up server')
    server = asyncio.start_server(handle_client, "0.0.0.0", 80)
    asyncio.create_task(server)
    
    while True:
        # Flash the LED to keep things ticking over
        led_indicator.toggle()  # Toggle LED state
        await asyncio.sleep(0.5)  # Blink interval

            
# dispatch stepper driver thread            
#_thread.start_new_thread(runstepper, ())        

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

    time.sleep(0.01)
    # float the pins
    left_wheel.close()
    right_wheel.close()

    print ("Program waiting to end")
    # hang around to let threads end
    time.sleep(1)
