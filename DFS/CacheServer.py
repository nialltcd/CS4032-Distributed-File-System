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

class Cache:
	
	#Dictionary for holding the cache data
	cache = {}

	#Adds a file to the cache
	def add_to_cache(file_path, data):
		cache[file_path] = data

	#returns the cached data for the corresponding file
	def get_cache_data(file_path):
		return cache[file_path]

	#returns true if the file is already cached
	def is_cached(file_path):
		if(file_path in cache):
			return True
		else:
			return False
	
class Client:
    def __init__(self, connection, cache):
	self.connection = connection
	self.working_dir = '/'
	self.cache = cache

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

    #If the file is in the cache then the data from the cache is returned to the user, else the user is notified that there is no cached data for the file.
    def process_command(self, client, data):
	if cache.is_cached(data):
		self.send_to_client(client,cache.get_cache_data())
	else:
		self.send_to_client(client,'not cached')

    #Sends the message to the client
    def send_to_client(self, client, data):
	data_to_send = "user@Niall'sServer:~"+client.working_dir+': \n'+str(data)
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
