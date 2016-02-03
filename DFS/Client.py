#!/usr/bin/python

import socket
import sys

fileserver_port_number = int(sys.argv[1])
directoryserver_port_number = int(sys.argv[2])
lockserver_port_number = int(sys.argv[3])
cacheserver_port_number = int(sys.argv[4])


#Create a socket for each server
fileserver_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
directoryserver_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lockserver_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cacheserver_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


#Connect to each server
fileserver_sock.connect(('localhost', fileserver_port_number))
directoryserver_sock.connect(('localhost', directoryserver_port_number))
lockserver_sock.connect(('localhost', lockserver_port_number))
cacheserver_sock.connect(('localhost', cacheserver_port_number))

current_working_directory='/'
while(1):
	user_input=raw_input('user@NiallsServer~/')
	command = user_input.split(' ')[0]
	lockserver_sock.send(current_working_directory+' '+user_input)
	data=lockserver_sock.recv(1000000)
	#If the location is Unlocked
	if(data == 'Not locked'):
		if command == 'cd':
			directoryserver_sock.send(user_input)
			current_working_directory=directoryserver_sock.recv(1000000)
			current_working_directory=current_working_directory
			print 'cwd: '+current_working_directory
		else:
			cacheserver_sock.send(current_working_directory, user_input)
			cache_data=cacheserver_sock.recv(1000000)
			if(cache_data=='Not cached'):
				fileserver_sock.send(current_working_directory+' '+user_input)
				data=fileserver_sock.recv(1000000)
				print data
			else:
				print cache_data
	else:
		print data
