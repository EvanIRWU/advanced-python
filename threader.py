import argparse
import threading
from queue import Queue
import socket
import re
import time

def scan_all_ports(host):
	for port in range(1, 65535):
		q.put(port)

def scan_specific_ports(host, ports):
	for port in range(len(ports)):
		q.put(ports[port])

# def get_portname(port):
# 	try:
# 		socket.getservbyport(port, "tcp")
# 	except socket.timeout:
# 		return None
# 	except OSError:
# 		return "Unknown"
def connect_to_port(host):
	while True:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			port = q.get()
			s.connect((host, port))
			with threading.Lock():
				# portname = get_portname(port)
				# if portname == None:
				# 	portname = socket.getservbyport(port, "tcp")
				print(f"Port open {port}")# - {portname}")
			s.close()
		except (ConnectionError, OSError, AttributeError):
			pass
		except socket.timeout:
			print(f"Port filtered {port}")
		q.task_done()
def start_threads():
	for i in range(threads):
		thread = threading.Thread(target=connect_to_port, args=(target,), daemon=True)
		thread.start()

parser = argparse.ArgumentParser(exit_on_error=False)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("ip", nargs='?', help="Get an IP")
group.add_argument('-f', '--file', type=argparse.FileType('r'), help='Input a file to be parsed.')
parser.add_argument("-p", "--port", nargs='*', type=int, help="No port means it will scan all 65535 ports")
parser.add_argument("-t", "--threads", type=int, help=f"Sets number of threads (Default: 200)")
args = parser.parse_args()

if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",args.ip):
	parser.error("Invalid IP")

target = args.ip
ports = args.port

q = Queue()

if not args.threads:
	threads = 200
else:
	threads = args.threads

if not args.port:
	scan_all_ports(target)
	start_threads()
else:
	scan_specific_ports(target, ports)
	start_threads()

q.join()

print("Done")
