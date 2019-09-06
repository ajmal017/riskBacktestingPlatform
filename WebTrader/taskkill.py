import psutil
import os 
pids = psutil.pids()
for pid in pids:
        p = psutil.Process(pid)
        # print('pid-%s,pname-%s' % (pid, p.name()))
        if p.name() == 'python.exe':
            cmd = 'taskkill /F /IM python.exe'
            os.system(cmd)
#import time
#import zmq
#context = zmq.Context()
#socket = context.socket(zmq.REP)
#socket.bind("tcp://*:6688")
 
#while True:
     #message = socket.recv()
     #print message
     ##time.sleep(1)
     #socket.send("server response!")
