#!/usr/bin/env python3

import json, os, socket, sys
from concurrent.futures import ThreadPoolExecutor

# References:
# - https://www.geeksforgeeks.org/socket-programming-multi-threading-python/
# - https://realpython.com/python-sockets/
# - https://www.tutorialspoint.com/concurrency_in_python/concurrency_in_python_pool_of_threads.htm
# - https://github.com/tusharlock10/Dictionary
# NOTE: On Windows, use CTRL+Pause/Break key combination to terminate server.

def main():
	# Get the user-provided port number, update the dictionary, and start the server.
	port = get_port_num()
	start_server(port)

def get_port_num():
	# Returns the port number specified by the user on the CLI. If none is given, program exits.
	try:
		port = int(sys.argv[1])
	except IndexError:
		print("Error: No port number provided as command line argument.")
		sys.exit(2) # Unix programs typically use 2 as the return code for CLI input errors.
	except ValueError:
		print("Error: Invalid port number provided as command line argument.")
		sys.exit(2) # Unix programs typically use 2 as the return code for CLI input errors.
	return port

def get_word(word):
	# Given an input word, search the dictionary for the word. If the word is not in the dictionary, return "NOENTRY".
	# If the word is in the dictionary, return a string-formatted JSON.
	# Dictionary stores words in all uppercase letters, so convert word to all uppercase to perform search.
	word = word.upper()
	
	# Open relevant JSON file to search for the word.
	try:
		json_file = open("dictionary/data/D" + word[0] + ".json")
		json_dict = json.load(json_file)
		json_file.close()
		json_dict = json_dict[word]['MEANINGS']
	except:
		# If no valid file exists, then the word is not present in the dictionary.
		return "NOENTRY"

	# If no meanings are present, return NOENTRY.
	if len(json_dict) == 0:
		return "NOENTRY"

	# Remove extra unwanted JSON fields.
	for key in json_dict:
		json_dict[key] = json_dict[key][:2]

	return json.dumps({word: json_dict})

def client_thread_mgr(conn, addr):
	# Manages a client connection on a separate thread.
	print('Connection from ' + str(addr[0]) + ':' + str(addr[1]) + ' accepted.')
	while True:
		# Receive data from client. If the receive attempt fails, close the connection.
		try:
			data = conn.recv(1024)
		except:
			break
		
		# Break if no data is received.
		if not data:
			break

		# Try to send the response to the client. If the attempt fails, print an error message.
		try:
			conn.sendall(get_word(data.decode('UTF-8')).encode('UTF-8'))
		except:
			print('Error: Send attempt to ' + str(addr[0]) + ':' + str(addr[1]) + ' failed.')

	conn.close()
	print('Connection from ' + str(addr[0]) + ':' + str(addr[1]) + ' closed.')

def start_server(port):
	# Create thread pool with a number of threads equal to the number of CPUs available on the system.
	thread_pool = ThreadPoolExecutor(os.cpu_count())

	# Try to bind socket to specified port. If unsuccessful, print error and exit.
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(('0.0.0.0', port))
		print('Socket bind to port', port, 'successful.')
	except:
		print("Error: Attempt to bind socket failed. Server will exit.")
		sys.exit(1)

	# Start socket listening for 20000 clients.
	s.listen(20000)
	print('Socket listening initiated.')

	# Repeatedly wait for and process client connections.
	while True:
		conn, addr = s.accept()
		
		# Handle client connection on a separate thread.
		thread_pool.submit(client_thread_mgr, conn, addr)
	
	# Close socket
	s.close()

if __name__=="__main__":
	main()