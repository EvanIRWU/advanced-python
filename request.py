#!/usr/bin/python3

import requests
import argparse
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_title(text, host):
	title = re.search('(?<=<title>).+?(?=</title>)', text, re.DOTALL).group().strip()
	return title
def get_request(host):
	try:
		r = requests.get(f'https://{host}', verify=False)
		title = get_title(r.text, host)
		print(f"Found: {host} | Title: {title}")
	except requests.exceptions.SSLError:
		r = requests.get(f'http://{host}', verify=False)
		title = get_title(r.text, host)
		print(f"Found: {host} | Title: {title}")
	except requests.RequestException:
		print(f"Not Reachable: {host}")
		return

def get_hosts(file):
	for host in file_content:
		if not host.startswith("#"):
			host = host.strip()
			get_request(host)
parser = argparse.ArgumentParser()

parser.add_argument('-f', '--file', required=True, type=argparse.FileType('r'), help='Input a file to be parsed.')

args = parser.parse_args()

if args.file:
	file_content = args.file.readlines()

# for host in file_content:
# 	if not host.startswith("#"):
# 		host = host.strip()
# 		try:
# 			r = requests.get(f'https://{host}', verify=False)
# 		except requests.exceptions.SSLError:
# 			r = requests.get(f'http://{host}', verify=False)
# 		except requests.RequestException:
# 			print(f"Not Reachable: {host}")
# 		title = get_title()
# 	# print(f"{r.text} \n\n" + "-"*50 + "\n")

get_hosts(file_content)