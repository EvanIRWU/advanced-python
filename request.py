#!/usr/bin/python3

import requests
import argparse
import re
import urllib3
import sys
import socket

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_title(text):
    if args.title:
        title = re.search('(?<=<title>).+?(?=</title>)',
                          text, re.DOTALL).group().strip()
        return title
    return None


def get_links(text):
    if args.links:
        links = re.findall(r'href[ ]{0,1}=[ ]{0,1}"([^\"]{0,})"', text)
        return links
    return None


def check_valid_link(host, url_links):

    links = url_links
    for counter, link in enumerate(links):
        link = link.strip()
        if not link.startswith("http://") and not link.startswith("https://"):
            links[counter] = f"{host}/{link}"
    return links


def request_to_url(host):
    try:
        r = requests.get(host, verify=False, timeout=3)
        print_line = f"[{r.status_code}] Found {host}"
        title = get_title(r.text)
        links = get_links(r.text)
        if title is not None:
            print_line += f" | Title {title}"
        if links is not None:
            links = check_valid_link(host, links)
            print_line += f" | Links {', '.join(links)}"
        print(print_line)

    except (requests.RequestException, requests.exceptions.SSLError):
        print(f"Not Reachable: {host}")


def check_url(content):
    for host in content:
        host = host.strip()
        if not host.startswith("#") and (host.startswith("http://") or host.startswith("https://")):
            request_to_url(host)
        elif host.startswith("#") or args.skip:
            pass
        elif args.http:
            request_to_url(f"http://{host}")
        elif args.https:
            request_to_url(f"https://{host}")
        else:
            print(f"There does not appear to be an http(s):// in the URL: {host}")


def print_error():
    print("""Please choose one of the following arguments:
    * -u - Host
    * -f - File
    * Pipe to a file using (|)
        """)
    exit()


def arg_check():
    if (args.file is not None and args.url is not None) or (not sys.stdin.isatty() and args.file is not None) or (not sys.stdin.isatty() and args.url is not None):
        print_error()

    if args.file is None and args.url is None and sys.stdin.isatty():
        print("No arguments specfied! Use python request.py -h to see the help menu.")

    if args.skip and (args.http or args.https):
        print("Cant use --skip with --http/s")
        exit()


def get_args():

    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--file', type=argparse.FileType('r'), help='Input a file to be parsed.')
    parser.add_argument('-u', '--url', type=str, help='Input URL.')
    parser.add_argument('-s', '--skip', action='store_true', help='Skips any URLs that do not have http/https.')
    parser.add_argument('-p', '--http', action='store_true', help='Forces any URLs that do not have http/https to have http:// URL.')
    parser.add_argument('-ps', '--https', action='store_true', help='Forces any URLs that do not have http/https to have https:// URL.')
    parser.add_argument('-t', '--title', action='store_true', help='Parses the title from the website.')
    parser.add_argument('-l', '--links', action='store_true', help='Parses the links from the website.')
    parser.add_argument('-c', '--connect', action='store_true', help='Parses the links from the website.')

    return parser


def remove_http(host):
    for url in host:
        port = 0
        url = url.strip()
        if url.startswith("http://"):
            url = url[7:]
            port = 80
        if url.startswith("https://"):
            url = url[8:]
            port = 443
        if ":" not in url:
            return [url, port]
        else:
            url, port = url.split(':')[0], url.split(':')[1]
            return [url, port]


def connect_to_socket(host, port):
    if port != 0:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, int(port)))
                print(f"The host {host}:{port} has successfully connected.")
        except ConnectionRefusedError:
            print(f"The host {host}:{port} was not able to connect.")


def main():

    arg_check()
    url = ""
    if args.url:
        url = args.url
        check_url([url])
    if args.file:
        url = args.file.readlines()
        check_url(url)
    if not sys.stdin.isatty():
        url = sys.stdin.readlines()
        check_url(url)

    if args.connect:
        for urls in url:
            new_url = remove_http([urls])
            domain_name, port = new_url[0], new_url[1]
            connect_to_socket(domain_name, port)
            # print(socket.gethostbyname('google.com'))


args = get_args().parse_args()

if __name__ == '__main__':
    main()
