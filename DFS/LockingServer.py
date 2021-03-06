#!/usr/bin/python

from lockfile import LockFile
import socket
import sys
from threading import *
from Queue import Queue
import re
import os
import subprocess

global port
global host


class Locker:

	#list to hold all locked files
	locked_files = [] 
	
	def __init__(self):
		pass
	
	#Locks the file and adds it to the locked files list
	def lock_file(self,file_path):
		self.locked_files.append(file_path)

	#Releases a file and removes it from the locked files list
	def unlock_file(self,file_path):
		self.locked_files.remove(file_path)

	#Returns true if a file is locked. Returns false otherwise
	def file_locked(self):
		if file_path in self.locked_files:
			return True
		else:
			return False

class Client:
    def __init__(self, connection, locker):
	self.connection = connection
	self.working_dir = '/'
	self.locker = locker

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
	file_path=client.connection.recv(1024)#[2:-2]
	self.process_command(client,file_path)	
	pool.add_task(client)

    #Notifies the user whether the file is locked or not
    def process_command(self, client, data):
		if(client.locker.file_locked()):
			self.send_to_client(client,'File Locked')
		else:
			self.send_to_client(client,'File Unlocked')

    def send_to_client(self, client, data):
	#Send data to user
	client.connection.send(data)
		

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
locker = Locker()
while 1:
    clientsocket, address = serversocket.accept()
    client = Client(clientsocket,locker)
    pool.add_task(client)
