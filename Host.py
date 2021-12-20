import paho.mqtt.client as mqtt
from pyModbusTCP.client import ModbusClient
import time
import matplotlib.pyplot as plt
import json
import threading
import datetime

broker="broker.hivemq.com"
port=1883

SERVER_HOST = "10.0.0.1"
SERVER_PORT = 502

c = ModbusClient()

c.host(SERVER_HOST)
c.port(SERVER_PORT)

# set decimal value to be sent
setpointRPM = 0
Kp = 0
Ki = 0
Kd = 0

#For calculating PID
setpointStep = [0]
actualRPMStep = [0]
e=[0]
integral_e =[0]
derivative_e=[0]
timeStep=[0]
processTime=[0]
n=0
inverterRelay=0
logSecond=[0] #just for testing delete later
logMinute=[0] #just for testing delete later

array={}
newval ={}
flag_connected = 0

def on_publish(client,userdata,result):             #create function for callback
    print("data published \n")
    pass

def on_connect(client, userdata, flags, rc):
  global flag_connected
  print("Connected with result code "+str(rc))
  client.subscribe("topic/deployrandom")
  
def on_disconnect(client, userdata, rc):
   global flag_connected
   flag_connected = 0

def on_message(client, userdata, msg):
  global array
  print("new content!")
  newval = msg.payload.decode()
  newval = json.loads(newval)
  print(newval)
  print(type(newval))
  array=newval
  return array

client = mqtt.Client()
client.connect(broker,port,60)

def localprocess():
    global inverterRelay
    global setpointRPM
    while True:
        client.loop_start()
        client.on_connect = on_connect
        client.on_message = on_message
        client.loop_stop()
        try:
            inverterRelay = int(array.get('start'))
            AI1 = int(array.get('setpoint'))
            Kp = float(array.get('KP'))
            Ki = float(array.get('KI'))
            Kd = float(array.get('KD'))
            setpointRPM = AI1
        except TypeError:
            print("Waiting for Data")
            localprocess()
            
        if not c.is_open():
            if not c.open():
                print("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))

        if c.is_open():
            if not setpointRPM == 0 :
              startTime = time.time()
              UDIO = c.read_coils (0,16)
              AI = c.read_holding_registers(8, 8)
              AO = c.read_holding_registers(16, 4)
            
              if UDIO:
                print("ADAM5050:"+str(UDIO))
              if AI:
                print("ADAM5017:"+str(AI))
              if AO:
                print("ADAM5024:"+str(AO))

              actualRPMDec = AI[3]
              actualRPMVoltage = (actualRPMDec-32767)*0.00030517578125
              actualRPM = actualRPMVoltage*(100/3)

              actualRPMStep.append(actualRPM)
              setpointStep.append(setpointRPM)
            
              setpointVoltage = (3*setpointRPM)/100
            
              e.append(setpointVoltage - actualRPMVoltage)
            
              integral_e.append(integral_e[-1]+e[-1]);
              derivative_e.append(e[-1] - e[-2]);

              PID = (Kp*e[-1]) + (Ki*integral_e[-1]) + (Kd*derivative_e[-1])

              controlSignalVolt = PID

              controlSignal = controlSignalVolt/0.00244140625
              controlSignal = int(controlSignal)

              if controlSignal > 2900 :
                controlSignal = 2900
                print("==============================")
                print("DANGER!, OVERVOLTAGE BEHAHIOUR")
                print("==============================")

              if controlSignal < 0:
                controlSignal = 0
                print("=================================")
                print("WARNING!, NEGATIVE CONTROL SIGNAL")
                print("=================================")

              print("Setpoint: "+str(setpointRPM))
              print("Control Signal: "+str(controlSignalVolt))
              print("Output: "+str(actualRPM))

              # send single register
              sent1 = c.write_single_register(16,controlSignal)
              sent2 = c.write_single_coil(0,inverterRelay)

              # if success display status
              if sent1:
                print("sent to reg 16: "+str(controlSignal))
              if sent2:
                print("sent to coil 0: "+str(inverterRelay))

              runTime = time.time() - startTime
              processTime.append(runTime)
              pTime = timeStep[-1]+runTime
              timeStep.append(pTime)
           
    print("\n")

    # sleep 1s before next polling
    time.sleep(0.0001)
    return inverterRelay

def communicationProcess():
  global n
  global timeStep
  global setpointStep
  global actualRPMStep
  global processTime
  global dateTimeNow #just for testing delete later
  global secondsNow #just for testing delete later
  global mocrosecondNow # just for testing
  global minuteNow #just for testing
  global logSecond #just for testing delete later
  dataout = {'timeStamp':timeStep, 'setpointStamp':setpointStep, 'actualStamp':actualRPMStep, 'processTimeStamp':processTime,'run':[0]}
  while True :
    try:
        if inverterRelay == 0:
            sent1 = c.write_single_register(16,0)
            if not len(dataout.get("actualStamp"))==1:
                timeStep=[0]
                setpointStep=[0]
                actualRPMStep=[0]
                processTime=[0]
                dataout = {'timeStamp':timeStep, 'setpointStamp':setpointStep, 'actualStamp':actualRPMStep, 'processTimeStamp':processTime,'run':[0]}
                datasent =json.dumps(dataout)
                client1= mqtt.Client("control1")                           #create client object
                client1.on_publish = on_publish                          #assign function to callback
                client1.connect(broker,port)                                 #establish connection
                ret= client1.publish("topic/fromhost",datasent)     
                print("simulation stopped reset data to 0")
                time.sleep(5)
            else:
                print("simulation stopped")
                time.sleep(5)
                pass
        else :
            dateTimeNow=datetime.datetime.now() #just for testing delete later
            secondsNow=float(dateTimeNow.second) #just for testing delete later
            microsecondNow=float(dateTimeNow.microsecond)/1000000 #just for testing delete later
            minuteNow=float(dateTimeNow.minute) #just for testing delete later
            logMinute.append(minuteNow) #just for testing delete later
            logSecond.append(secondsNow+microsecondNow) #just for testing delete later
            dataout = {'timeStamp':timeStep, 'setpointStamp':setpointStep, 'actualStamp':actualRPMStep, 'processTimeStamp':processTime, 'run':inverterRelay}
            datasent =json.dumps(dataout)
            client1= mqtt.Client("control1")                           #create client object
            client1.on_publish = on_publish                          #assign function to callback
            client1.connect(broker,port)                                 #establish connection
            ret= client1.publish("topic/fromhost",datasent)                 #publish
            print("\n")
            print(logMinute) #just for testing delete later
            print("\n")
            print(logSecond) #just for testing delete later
            print("\n")
            print("harusnya data terkirim, no error from host")
    except:
        print("No data to be sent")
    time.sleep(0.5)
    
thread1 = threading.Thread(target=localprocess)
thread1.start()

thread2 = threading.Thread(target=communicationProcess)
thread2.start()
