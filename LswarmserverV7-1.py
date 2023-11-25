'''
    LightSwarm Raspberry Pi Logger 
    SwitchDoc Labs 
    December 2020
'''

from __future__ import print_function
#from multiprocess import Process
from builtins import chr
from builtins import str
from builtins import range
import sys  
import time
import threading
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from netifaces import interfaces, ifaddresses, AF_INET
from math import floor
from socket import *
import signal
import RPi.GPIO as GPIO
from gpiozero import LED
from datetime import date
from datetime import datetime


thread_exit = False
data_map = False
swarms = ['0','0','0']
time_1 = []
time_2 = []
time_3 = []
four_sec_val = 0
#bar_time = [0] * 30
loop_count = 0
mastertimes = [0,0,0]
tick = 0
max_val = 50
IDmaster = 0
BUTTON_GPIO = 16

YELLOW_LED = LED(24)

WHITE_LED = LED(27)
columnDataPin = 20
rowDataPin = 21
latchPIN = 14
clockPIN = 15


VERSIONNUMBER = 7
# packet type definitions
LIGHT_UPDATE_PACKET = 0
RESET_SWARM_PACKET = 1
CHANGE_TEST_PACKET = 2   # Not Implemented
RESET_ME_PACKET = 3
DEFINE_SERVER_LOGGER_PACKET = 4
LOG_TO_SERVER_PACKET = 5
MASTER_CHANGE_PACKET = 6
BLINK_BRIGHT_LED = 7

MYPORT = 50001

SWARMSIZE = 3


light_packet_1 = []
light_packet_2 = []
light_packet_3 = []

logString = ""
global file_name
global data_plot
data_plot =    [['11111111'],\
                    ['11111111'],\
                    ['11111111'],\
                    ['11111111'],\
                    ['11111111'],\
                    ['11111111'],\
                    ['11111111'],\
                    ['11111111']]
global thread_start
thread_start = False

# Fetch the service account key JSON file contents
cred = credentials.Certificate('ecps216final-7c76c-firebase-adminsdk-u2acj-74e7063012.json')
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://ecps216final-7c76c-default-rtdb.firebaseio.com/"
})

def signal_handler(sig, frame):
	GPIO.cleanup()
	sys.exit(0)


def data_logger(device_data,mastertimes,swarms,file_name):
    
    string = f"{swarms[0]},{swarms[1]},{swarms[2]},{device_data[0]},{device_data[1]},{device_data[2]},{mastertimes[0]},{mastertimes[1]},{mastertimes[2]}\n"
    
    with open('/home/pi/Documents/%s'%file_name, 'a') as f:
        f.write(string)
def LED_Matrix_graph(tick,max_val):
    global thread_start
    global data_plot
    
    def shift_update_matrix(input_Col,Column_PIN,input_Row,Row_PIN,clock,latch):
      GPIO.output(clock,0)
      GPIO.output(latch,0)
      GPIO.output(clock,1)

      for i in range(7, -1, -1):
        GPIO.output(clock,0)
        GPIO.output(Column_PIN, int(input_Col[i]))
        GPIO.output(Row_PIN, int(input_Row[i]))
        GPIO.output(clock,1)

      GPIO.output(clock,0)
      GPIO.output(latch,1)
      GPIO.output(clock,1)
    def make_matrix():
        data_plot[7] = data_plot[6]
        data_plot[6] = data_plot[5]
        data_plot[5] = data_plot[4]
        data_plot[4] = data_plot[3]
        data_plot[3] = data_plot[2]
        data_plot[2] = data_plot[1]
        data_plot[1] = data_plot[0]
        
    def inf_loop():
        
        while True:
          try:
            while True:
                RowSelect=[1,0,0,0,0,0,0,0]
                for i in range(0,8): # last value in rage is not included by default
                  shift_update_matrix(''.join(map(str, data_plot[i])),columnDataPin,\
                                      ''.join(map(str, RowSelect)),rowDataPin,clockPIN,latchPIN)
                  RowSelect = RowSelect[-1:] + RowSelect[:-1]
                
                    
          except KeyboardInterrupt:
            GPIO.cleanup()
            #sys.exit()
    i = 7
    
    if  tick < 32:
       
        if tick/4 <= 1.0:
            i = 7
        elif  tick/4 <= 2.0:
            i = 6
        elif tick/4 <= 3.0:
            i = 5
        elif tick/4 <= 4.0:
            i = 4
        elif tick/4 <= 5.0:
            i = 3
        elif tick/4 <= 6.0:
            i = 2
        elif tick/4 <= 7.0:
            i = 1
        elif tick/4 <= 8.0:
            i = 0
    else:
        
        i = 0
    
    if max_val < 128:
        if i == 0:
            make_matrix()
        data_plot[i] = ['11111110']
        
    elif max_val < 256:
        if i == 0:
            make_matrix()
        data_plot[i] = ['11111101']
        
    elif max_val < 384:
        if i == 0:
            make_matrix()
        data_plot[i] = ['11111011']
        
    elif max_val < 512:
        if i == 0:
            make_matrix()
        data_plot[i] = ['11110111']
        
    elif max_val < 640:
        if i == 0:
            make_matrix()
        data_plot[i] = ['11101111']
        
    elif max_val < 768:
        if i == 0:
            make_matrix()
        data_plot[i] = ['11011111']
        
    elif max_val < 896:
        if i == 0:
            make_matrix()
        data_plot[i] = ['10111111']
        
    elif max_val <= 1024:
        if i == 0:
            make_matrix()
        data_plot[i] = ['01111111']
        
        
    t1 = threading.Thread(target = inf_loop)
    if thread_start == False:
        t1.start()
        thread_start = True
        
    
        
    

def SendDEFINE_SERVER_LOGGER_PACKET(s):
    print("DEFINE_SERVER_LOGGER_PACKET Sent") 
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

	# get IP address
    for ifaceName in interfaces():
            addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
            print('%s: %s' % (ifaceName, ', '.join(addresses)))
  
    # last interface (wlan0) grabbed 
    print(addresses) 
    myIP = addresses[0].split('.')
    print(myIP) 
    data= ["" for i in range(14)]

    
    data[0] = int("F0", 16).to_bytes(1,'little') 
    data[1] = int(DEFINE_SERVER_LOGGER_PACKET).to_bytes(1,'little')
    data[2] = int("FF", 16).to_bytes(1,'little') # swarm id (FF means not part of swarm)
    data[3] = int(VERSIONNUMBER).to_bytes(1,'little')
    data[4] = int(myIP[0]).to_bytes(1,'little') # 1 octet of ip
    data[5] = int(myIP[1]).to_bytes(1,'little') # 2 octet of ip
    data[6] = int(myIP[2]).to_bytes(1,'little') # 3 octet of ip
    data[7] = int(myIP[3]).to_bytes(1,'little') # 4 octet of ip
    data[8] = int(0x00).to_bytes(1,'little')
    data[9] = int(0x00).to_bytes(1,'little')
    data[10] = int(0x00).to_bytes(1,'little')
    data[11] = int(0x00).to_bytes(1,'little')
    data[12] = int(0x00).to_bytes(1,'little')
    data[13] = int(0x0F).to_bytes(1,'little')
    mymessage = ''.encode()  	
    s.sendto(mymessage.join(data), ('<broadcast>'.encode(), MYPORT))
	
def SendRESET_SWARM_PACKET( channel):
        #global s
        
        print("RESET_SWARM_PACKET Sent")
        print(s) 
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        WHITE_LED.on()
        data= ["" for i in range(14)]

        data[0] = int("F0", 16).to_bytes(1,'little')
        
        data[1] = int(RESET_SWARM_PACKET).to_bytes(1,'little')
        data[2] = int("FF", 16).to_bytes(1,'little') # swarm id (FF means not part of swarm)
        data[3] = int(VERSIONNUMBER).to_bytes(1,'little')
        data[4] = int(0x00).to_bytes(1,'little')
        data[5] = int(0x00).to_bytes(1,'little')
        data[6] = int(0x00).to_bytes(1,'little')
        data[7] = int(0x00).to_bytes(1,'little')
        data[8] = int(0x00).to_bytes(1,'little')
        data[9] = int(0x00).to_bytes(1,'little')
        data[10] = int(0x00).to_bytes(1,'little')
        data[11] = int(0x00).to_bytes(1,'little')
        data[12] = int(0x00).to_bytes(1,'little')
        data[13] = int(0x0F).to_bytes(1,'little')
            
        mymessage = ''.encode()  	
        s.sendto(mymessage.join(data), ('<broadcast>'.encode(), MYPORT))
        time.sleep(3)
        
        WHITE_LED.off()
        global data_map
        data_map = True
        
        time_now = datetime.now()
        global file_name
        file_name = 'Log File %s.txt'%time_now
        swarms = ['0','0','0']
        time.sleep(2)
        SendDEFINE_SERVER_LOGGER_PACKET(s)
        
        #tick = 0
        
        
        time.sleep(3)
        SendDEFINE_SERVER_LOGGER_PACKET(s)
    
        
        
                      
def parseLogPacket(message):
       
	incomingSwarmID = setAndReturnSwarmID((message[2]))
	print("Log From SwarmID:",(message[2]))
	print("Master time:", (message[4]))
	mastertime = message[4]
	print("StringLength:",(message[3]))
	logString = ""
	for i in range(0,(message[3])):
		logString = logString + chr((message[i+5]))

	#print("logString:", logString)	
	return logString, mastertime



# build Webmap


def buildWebMapToFile(logString, swarmSize ):
    max_val = 0
    swarm_no = [0,0,0]
    device_data = [0,0,0]
    webresponse = ""

    swarmList = logString.split("|")
    for i in range(0,swarmSize):
        swarmElement = swarmList[i].split(",")	
        print("swarmElement=", swarmElement)
        #data = swarmElement[3]
        device_data[i] = swarmElement[3]
        swarm_no[i] = swarmElement[5]
        for k in range(0,swarmSize):
            if max_val < int(device_data[i]):
                max_val = int(device_data[i])
        
    return max_val, device_data, swarm_no

def setAndReturnSwarmID(incomingID):
 
    
    for i in range(0,SWARMSIZE):
        if (swarmStatus[i][5] == incomingID):
           # print(swarmStatus[i][2])
            
                return i
        
        else:
            if (swarmStatus[i][5] == 0):  # not in the system, so put it in
                
                swarmStatus[i][5] = incomingID;
                print("incomingID %d " % incomingID)
                print("assigned #%d" % i)
                return i
    
  
    # if we get here, then we have a new swarm member.   
    # Delete the oldest swarm member and add the new one in 
    # (this will probably be the one that dropped out)
  
    oldTime = time.time();
    oldSwarmID = 0
    for i in range(0,SWARMSIZE):
        if (oldTime > swarmStatus[i][1]):
            ldTime = swarmStatus[i][1]
            oldSwarmID = i
  		
 
 

    # remove the old one and put this one in....
    swarmStatus[oldSwarmID][5] = incomingID;
    # the rest will be filled in by Light Packet Receive
    print("oldSwarmID %i" % oldSwarmID)
 
    return oldSwarmID 


#if __name__=='__main__':
GPIO.setmode(GPIO.BCM)
GPIO.setup((columnDataPin,rowDataPin,latchPIN,clockPIN),GPIO.OUT)

#GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(BUTTON_GPIO, GPIO.FALLING,
            callback=SendRESET_SWARM_PACKET, bouncetime=300)
    #bouncetime ensure callback is triggered once in 100ms
signal.signal(signal.SIGINT, signal_handler)


# set up sockets for UDP

s=socket(AF_INET, SOCK_DGRAM)
host = 'localhost';
s.bind(('',MYPORT))

print("--------------")
print("LightSwarm Logger")
print("Version ", VERSIONNUMBER)
print("--------------")

 
# first send out DEFINE_SERVER_LOGGER_PACKET to tell swarm where to send logging information 

SendDEFINE_SERVER_LOGGER_PACKET(s)
time.sleep(3)
SendDEFINE_SERVER_LOGGER_PACKET(s)



# swarmStatus
swarmStatus = [[0 for x  in range(6)] for x in range(SWARMSIZE)]

# 6 items per swarm item

# 0 - NP  Not present, P = present, TO = time out
# 1 - timestamp of last LIGHT_UPDATE_PACKET received
# 2 - Master or slave status   M S
# 3 - Current Test Item - 0 - CC 1 - Lux 2 - Red 3 - Green  4 - Blue
# 4 - Current Test Direction  0 >=   1 <=
# 5 - IP Address of Swarm


for i in range(0,SWARMSIZE):
    swarmStatus[i][0] = "NP"
    swarmStatus[i][5] = 0


#300 seconds round
seconds_300_round = time.time() + 300
ID_1 = time.time()
ID_2 = time.time()
ID_3 = time.time()
LED_DELAY = time.time()
PLOT_DELAY = time.time()

#fig = plt.figure()


while(1):    
    # receive datclient (data, addr)
    d = s.recvfrom(1024)
    
    message = d[0]
    addr = d[1]
    
    if (len(message) == 14):


        if (message[1] == LIGHT_UPDATE_PACKET):
            incomingSwarmID = setAndReturnSwarmID((message[2]))
            
            
               
            swarmStatus[incomingSwarmID][0] = "P"
            swarmStatus[incomingSwarmID][1] = time.time()  
            
               
        if ((message[1]) == RESET_SWARM_PACKET):
            print("Swarm RESET_SWARM_PACKET Received")
            print("received from addr:",addr)	

        

       

        if ((message[1]) == DEFINE_SERVER_LOGGER_PACKET):
            print("Swarm DEFINE_SERVER_LOGGER_PACKET Received")
            print("received from addr:",addr)	
        
        

        #for i in range(0,14):  
        #    print("ls["+str(i)+"]="+format((message[i]), "#04x"))

    else:
        if ((message[1]) == LOG_TO_SERVER_PACKET):
            print("Swarm LOG_TO_SERVER_PACKET Received")

            # process the Log Packet
            logString, mastertime = parseLogPacket(message)
            max_val,device_data,swarm_no = buildWebMapToFile(logString, SWARMSIZE)
            
            if str(message[2]) not in swarms:
                print(swarms)
                if swarms[0] == '0':
                    swarms[0] = str(message[2])
                elif swarms[1] == '0':
                    swarms[1] = str(message[2])
                elif swarms[2] == '0':
                    swarms[2] = str(message[2])
            if str(message[2]) in swarms:
                           
                masterID = swarms.index(str(message[2]))
                
                mastertimes[masterID] = mastertime
                if masterID == 0:
                    ID_1 = time.time()
                  
                    time_1.append(tick)
                    light_packet_1.append(max_val)
                    
                                          
                elif masterID == 1:
                    ID_2 = time.time()
                    
                    time_2.append(tick)
                    light_packet_2.append(max_val)
                   
                    
                elif masterID == 2:
                    ID_3 = time.time()
                    
                    time_3.append(tick)
                    light_packet_3.append(max_val)
                   
                    
                
                if tick == 30:
                    
                    if ((ID_1 > ID_2) & (ID_1 > ID_3)):
                        try:
                            if ID_2 > ID_3:
                                time_3.pop(0)
                                light_packet_3.pop(0)
                            else:
                                time_2.pop(0)
                                light_packet_2.pop(0)
                        except:
                            pass
                    elif((ID_2 > ID_1) & (ID_2 > ID_3)):
                        try:
                            if ID_1 > ID_3:
                                time_3.pop(0)
                                light_packet_3.pop(0)
                            else:
                                time_1.pop(0)
                                light_packet_1.pop(0)
                        except:
                            pass
                    elif((ID_3 > ID_1) & (ID_3 > ID_2)):
                        try:
                            if ID_1 > ID_2:
                                time_2.pop(0)
                                light_packet_2.pop(0)
                            else:
                                time_1.pop(0)
                                light_packet_1.pop(0)
                        except:
                            pass
                ref = db.reference('/')
                users_ref = ref.child("CurrentData")
                users_ref.update({time.time() : (masterID * 1000) + maxValue})
                if data_map == True:
                    
                    
                    if IDmaster != masterID:
                        
                        if IDmaster == 0:
                            
                            time_1.append(None)
                            light_packet_1.append(None)
                        elif IDmaster == 1:
                           
                            time_2.append(None)
                            light_packet_2.append(None)
                        elif IDmaster == 2:
                            
                            time_3.append(None)
                            light_packet_3.append(None)
                    IDmaster = masterID
                    data_logger(device_data,mastertimes,swarm_no,file_name)
                    four_sec_val = four_sec_val + max_val
                    loop_count = loop_count + 1
                    if (time.time() >= PLOT_DELAY):
                        PLOT_DELAY = time.time() + 4
                        by = floor(tick/30)
                        intermediate = tick - (30*by)
                        #bar_time[intermediate] = str(message[2])
                        four_sec_val = four_sec_val/loop_count
                        LED_Matrix_graph(tick,four_sec_val)
                        four_sec_val = 0
                        loop_count = 0
                        tick = tick + 4
                        
                                                                                           
                
                

        else:
            print("error message length = ",len(message))

    if (time.time() >  seconds_300_round):
        # do our 2 minute round
        print(">>>>doing 300 second task")
        SendDEFINE_SERVER_LOGGER_PACKET(s)
        seconds_300_round = time.time() + 300

   # processCommand(s)
signal.pause()
    #print swarmStatus 
