# This code build by
# Ade Oktavianus Kurniawan
# Kevin Natio Banjarnahor
# Ahmad Rofif Hakiki
# This code built as part of the internship in Control System Laboratory Aj104 ITS

# If there is any error occur, please contact any laboratory assistant

from tkinter import *
from tkinter import messagebox
import tkinter
import urllib.request
import json
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np
from PIL import ImageTk, Image
import paho.mqtt.client as mqtt
import time
import matplotlib.pyplot as plt
import webbrowser
import statistics

# For assistant, please edit the following code for limit Kp, Ki, Kd
limit_kp= 20
limit_ki= 10
limit_kd= 5
url= 'https://www.youtube.com/watch?v=DWcJFNfaw9c' # Edit the streaming link here

## Motor DC Rating
voltage= 30 #Voltage
speed= 1000 #RPM

# Never ever ever edit below this code

value_sp= 0.000
default_kp= 0.000
default_ki= 0.000
default_kd= 0.000

setpointStep = [0]
actualRPMStep = [0]
timeStep=[0]
processTime=[0]

result=[]
run=0
data ={}

#Test, Erase after test
x=[0]
y=[0]
n=0

array={}
newval={}

broker="broker.hivemq.com"
port=1883
client = mqtt.Client()
client.connect(broker,port,60)

def on_connect(client, userdata, flags, rc):
  global flag_connected
  print("Connected with result code "+str(rc))
  client.subscribe("topic/fromhost")

def on_disconnect(client, userdata, rc):
   global flag_connected
   flag_connected = 0

def on_message(client, userdata, msg):
  global array
  newval = msg.payload.decode()
  newval = json.loads(newval)
  print(newval)
  print(type(newval))
  array=newval
  return array

def on_publish(client,userdata,result):             #create function for callback
    pass

def set_param():
    global data
    global value_sp
    global data_kp
    global data_ki
    global data_kd
    global run
    global sp_voltage
    value_sp=scale_sp1.get()
    data_kp=entry_sp1.get()
    data_ki=entry_sp2.get()
    data_kd=entry_sp3.get()
    value_sp=int(value_sp)
    if data_kp== '' or data_ki== '' or data_kd== '':
        print("Please input the value!")
    else:
        data_kp=float(data_kp)
        data_ki=float(data_ki)
        data_kd=float(data_kd)
        if data_kp>= limit_kp or data_ki>= limit_ki or data_kd>= limit_kd:
            print("Please input the value below the limit!")
        else:
            if data_kp< 0 or data_ki< 0 or data_kd< 0:
                print("Please input the value above zero")
            else:
                print("Your parameter has been set")
                print("Your parameter is: "+"\nSetting Point: "+ str(value_sp)+" RPM"+"\nKp: "+ str(data_kp)+"\nKi: "+str(data_ki)+"\nKi: "+str(data_kd))
                update_log= "Your parameter is: "+"\nSetting Point: "+ str(value_sp)+" RPM"+"\nKp: "+ str(data_kp)+"\nKi: "+str(data_ki)+"\nKi: "+str(data_kd)
                log.config(state= 'normal')
                log.delete('1.0', END)
                log.insert(tkinter.INSERT, update_log)
                log.config(state= 'disabled')
    return data, value_sp, data_kp, data_ki, data_kd, run

def run_simulation():
    global run
    global timeStep
    global setpointStep
    global actualRPMStep
    global processTime
    global array
    timeStep=[]
    actualRPMStep=[]
    run = 1
    client1= mqtt.Client("control 1")
    client1.on_publish = on_publish
    client1.connect(broker,port)
    data={"setpoint" : value_sp,"KP" : data_kp,"KI" : data_ki,"KD" : data_kd,"start" : run}
    ret= client1.publish("topic/deployrandom",json.dumps(data))
    status_log= "Status:"+"\nConnected"+"\nStart= True"
    log.config(state= 'normal')
    log.delete('1.0', END)
    log.insert(tkinter.INSERT, status_log)
    log.config(state= 'disabled')
    localprocess()
    return run, timeStep, actualRPMStep

def localprocess():
  global n
  global timeStep
  global setpointStep
  global actualRPMStep
  global processTime
  global runhost
  n=0
  while True:
    try:
      client.loop_start()
      client.on_connect= on_connect
      client.on_message= on_message
      client.loop_stop()
      timeStep=array.get('timeStamp')
      setpointStep=array.get('setpointStamp')
      actualRPMStep=array.get('actualStamp')
      processTime= array.get('processTimeStamp')
      runhost=array.get('run')
      print(array)
      if timeStep== None:
        c = [0]
        actualRPMStep = [0]
        timeStep=[0]
        processTime=[0]
        window.update()
      elif runhost==1 and run==0:
        status_log= "Status:"+"\nTrying to disconnect"
        log.config(state= 'normal')
        log.delete('1.0', END)
        log.insert(tkinter.INSERT, status_log)
        log.config(state= 'disabled')
        fig = Figure(figsize=(4,3), dpi=100)
        ax= fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=window)
        ax.cla()
        ax.plot(timeStep,actualRPMStep)
        ax.set_ylabel('RPM')
        ax.set_xlabel('Waktu(detik)')
        fig.tight_layout()
        canvas.draw()
        canvas.get_tk_widget().grid(column=5, row=2)
        time.sleep(0.1)
        window.update()
        stop_simulation()
        pass
      elif runhost==0 and run==1:
        window.update()
        time.sleep(10)
        status_log= "Status:"+"\nRequest Time Out"+"\nTrying to start again"
        log.config(state= 'normal')
        log.delete('1.0', END)
        log.insert(tkinter.INSERT, status_log)
        log.config(state= 'disabled')
        run_simulation()
      elif runhost==0 and run==0:
        window.update()
        time.sleep(0.1)
        stop_simulation()
      else:
        try:
          fig = Figure(figsize=(4,3), dpi=100)
          ax = fig.add_subplot(111)
          canvas = FigureCanvasTkAgg(fig, master=window)
          ax.cla()
          ax.plot(timeStep,actualRPMStep)
          ax.set_ylabel('RPM')
          ax.set_xlabel('Waktu(detik)')
          fig.tight_layout()
          canvas.draw()
          canvas.get_tk_widget().grid(column=5, row=2)
          time.sleep(0.1)
          window.update()
        except:
          print("time pass")#
          time.sleep(0.2)#
          window.update()#
    except :
        status_log= "Status:"+"\nDisconnected"
        log.config(state= 'normal')
        log.delete('1.0', END)
        log.insert(tkinter.INSERT, status_log)
        log.config(state= 'disabled')
        window.update()
        stop_simulation
        break
  window.update()
  avg=statistics.mean(processTime)
  print(avg)
 # runhost=0 #
 # stop_simulation() #
  return x,y, timeStep, setpointStep, actualRPMStep, processTime, runhost
    
def stop_simulation():
    global run
    value_sp=0
    run = 0
    client1= mqtt.Client("control 1")
    client1.on_publish = on_publish
    client1.connect(broker,port)
    data={"setpoint" : value_sp,"KP" : data_kp,"KI" : data_ki,"KD" : data_kd,"start" : run }
    ret= client1.publish("topic/deployrandom",json.dumps(data))
    print("Stopping Simulation")
    if runhost==1 and run==0:
      time.sleep(5)
      window.update()
      localprocess()
    status_log= "Status:"+"\nStart= False"
    log.config(state= 'normal')
    log.delete('1.0', END)
    log.insert(tkinter.INSERT, status_log)
    log.config(state= 'disabled')
    timeStep=[]
    actualRPMStep=[]
    window.update()
    return run,timeStep,actualRPMStep

def close_window():
    window.destroy()

window = Tk()
window.title("Testing GUI")
window.geometry('850x550')

label_text1 = Label(window, text="Welcome to Remote Laboratory AJ104")
label_text1.grid(column=0, row=0)

variable1= StringVar(window)
variable1.set("Step")
dropdown_sp = OptionMenu(window, variable1,"Step","Sinus")
dropdown_sp.grid(column=0,row=1)

label_sp1 = Label(window, text="Set Speed value")
label_sp1.grid(column=0, row=2)

scale_sp1 = Scale(window, variable="Int", from_=0, to=300, orient=tkinter.HORIZONTAL)
scale_sp1.grid(column=1, row=2)

label_sp2 = Label(window, text="Set PID Parameter")
label_sp2.grid(column=0, row=3)

label_sp3 = Label(window, text="Set Kp")
label_sp3.grid(column=0, row=4)

entry_sp1 = Entry(window)
entry_sp1.grid(column=1,row=4)

label_sp4 = Label(window, text="Set Ki")
label_sp4.grid(column=0, row=5)

entry_sp2 = Entry(window)
entry_sp2.grid(column=1,row=5)

label_sp5 = Label(window, text="Set Kd")
label_sp5.grid(column=0, row=6)

entry_sp3 = Entry(window)
entry_sp3.grid(column=1,row=6)

button_set_param = Button(window, text="Set Parameter", command=set_param)
button_set_param.grid(column=1, row=8)

button_run = Button(window, text="Run Simulation", command=run_simulation)
button_run.grid(column=1, row=9)

button_stop = Button(window, text="Stop Simulation", command=stop_simulation)
button_stop.grid(column=2, row=9)

exit_button= Button(window, text="Exit", command=close_window)
exit_button.grid(column=1, row=10)

status_log= "Status:"+"\nStand by"
log= Text(window, height= 5, width= 37)
log.insert(INSERT, status_log)
log.config(state= 'disabled')
log.grid(column=5, row=4 ,rowspan= 3)

window.mainloop()
#webbrowser.open(url)
