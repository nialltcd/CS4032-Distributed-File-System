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

    def process_command(self, client, data):
	command = data.split(' ')[0]
	temp = data.split()
	#os.system(data)
	#self.send_to_client(client, data)
	os.chdir(client.working_dir)
	self.change_directory(client, data.split(' ')[1])

    """
    This function is called if the command passed is a 'change directory' command
    """
    def change_directory(self, client, new_path):
	if new_path[0] == '/':  #If the user is changing to a directory using an absolute path
		new_working_directory = new_path
	elif client.working_dir == '/': #If user is currently in the root directory
		new_working_directory = '/' + new_path
	elif new_path == '..':  #If user is moving up a directory
		new, sep, old = client.working_dir.rpartition('/')
		new_working_directory = new + sep
	else:	#If the user is performing any other changing of directories
		new_working_directory = client.working_dir + '/' + new_path
	
	if os.path.isdir(new_working_directory): #If the chosen directory exists
		print 'new dir: ' + new_working_directory
		client.working_dir = new_working_directory
		self.send_to_client(client,new_working_directory)
	else:	#The chosen directory doesn't exist
		self.send_to_client(client,client.working_dir)

    def send_to_client(self, client, data):
	data_to_send = "user@Niall'sServer:~"+client.working_dir+': \n'+str(data)
	#print data_to_send
	#client.connection.send(data_to_send)
	client.connection.send(str(data))

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
