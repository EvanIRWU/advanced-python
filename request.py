#!/usr/bin/python3

import requests
import argparse
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser()

parser.add_argument('-f', '--file', required=True, type=argparse.FileType('r'), help='Input a file to be parsed.')

args = parser.parse_args()

if args.file:
	file_content = args.file.readlines()

for host in file_content:
	host = host.strip()
	try:
		r = requests.get(f'https://{host}', verify=False)
	except requests.exceptions.SSLError:
		r = requests.get(f'http://{host}', verify=False)
	title = re.search('(?<=<title>).+?(?=</title>)', r.text, re.DOTALL).group().strip()
	print("Title: " + title)
	print(f"{r.text} \n\n" + "-"*50 + "\n")