#!/usr/bin/python3

import requests
import argparse
import re
import urllib3
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_title(text):
    title = re.search('(?<=<title>).+?(?=</title>)',
                      text, re.DOTALL).group().strip()
    return title


def get_links(text):
    links = re.findall(r'href[ ]{0,1}=[ ]{0,1}"([^\"]{0,})"', text)
    return links


def get_request(host):
    try:
        r = requests.get(host, verify=False, timeout=3)
        print(f"[{r.status_code}] Found {host}", end=" ")  # | Title: {title}")
        if args.title:
            title = get_title(r.text)
            print(f"| Title {title}", end=" ")
        if args.links:
            links = get_links(r.text)
            # Check to see is link startswith http(s), if it does, pass, else append variable host to the link.
            print(f"| Links ", end="")
            print(*links, sep=f', ')
    except (requests.RequestException, requests.exceptions.SSLError):
        print(f"Not Reachable: {host}")


def get_hosts(content):
    for host in content:
        host = host.strip()
        if not host.startswith("#") and (host.startswith("http://") or host.startswith("https://")):
            get_request(host)
        elif host.startswith("#") or args.skip:  # or args.http or args.https:
            pass
        # Add option if user wants to auto-extend protocol (add argument --skip to skip this step)
        elif args.http:
            get_request(f"http://{host}")
        elif args.https:
            get_request(f"https://{host}")
        else:
            print(f"There does not appear to be an http(s):// in the URL provided {host}")


def print_error():
    print("""Please choose one of the following arguments:
    * -H - Host
    * -f - File
        """)
    exit()


def argument_check():
    if args.file is not None and args.host is not None:
        print_error()

    if args.skip and (args.http or args.https):
        print("Cant use --skip with --http/s")
        exit()


def get_args():

    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--file', type=argparse.FileType('r'), help='Input a file to be parsed.')
    parser.add_argument('-H', '--host', type=str, help='Input a file to be parsed.')
    parser.add_argument('-s', '--skip', action='store_true', help='Input a file to be parsed.')
    parser.add_argument('-p', '--http', action='store_true', help='Input a file to be parsed.')
    parser.add_argument('-ps', '--https', action='store_true', help='Input a file to be parsed.')
    parser.add_argument('-t', '--title', action='store_true', help='Input a file to be parsed.')
    parser.add_argument('-l', '--links', action='store_true', help='Input a file to be parsed.')

    return parser


def main():

    argument_check()

    if args.host:
        host = args.host
        get_hosts([host])
    if args.file:
        file_content = args.file.readlines()
        get_hosts(file_content)
    if not sys.stdin.isatty():
        stdin_get_lines = sys.stdin.readlines()
        get_hosts(stdin_get_lines)


args = get_args().parse_args()

main()
