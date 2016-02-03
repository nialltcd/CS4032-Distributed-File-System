#!/usr/bin/python

import socket
import sys
from threading import *
from Queue import Queue
import re
import os
import subprocess

global port
global host

"""
Class represents a client object
Each Connection to the server created a new client object that keeps track of their current working directory and the connection
"""
class Client:
    def __init__(self, connection):
	self.connection = connection
	self.working_dir = '/'

class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            client = self.tasks.get()
            try: self.process_message(client)
            except Exception, e: print e
            self.tasks.task_done()
    
    def process_message(self,client):
	data=client.connection.recv(1024)#[2:-2]
	self.process_command(client,data)	
	pool.add_task(client)

    """
    Changes to the working directory of the Client and performs the command  
    """
    def process_command(self, client, data):
	client.working_dir = data.split(' ')[0]
	command = data.split(' ')[1]
	temp = data.split()
	os.chdir(client.working_dir)
	data = data.split(' ')[1:]
	#This command allows user to input any command that is acceptable to a Linux command line.
	#This provides a lot of functionality 
	proc = subprocess.Popen(data, stdout=subprocess.PIPE)
	(out,err) = proc.communicate()
	self.send_to_client(client,out)

    #Formats and sends data to client
    def send_to_client(self, client, data):
	data_to_send = "user@Niall'sServer:~"+client.working_dir+': \n'+str(data)
	#print data_to_send
	client.connection.send(data_to_send)

class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads): Worker(self.tasks)

    def add_task(self,client ):
        """Add a task to the queue"""
        self.tasks.put(client)

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
global host
host="127.0.0.1"
global port
os.chdir('/')
port = int(sys.argv[1])
serversocket.bind((host, port))
pool = ThreadPool(5)
serversocket.listen(10)
while 1:
    clientsocket, address = serversocket.accept()
    client = Client(clientsocket)
    pool.add_task(client)
