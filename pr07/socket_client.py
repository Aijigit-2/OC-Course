#!/usr/bin/env python3
import socket
import sys

expression = " ".join(sys.argv[1:]) or "2 + 2 * 2"
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
with client:
    client.connect("/tmp/os_calc.sock")
    client.sendall((expression + "\n").encode())
    print(client.makefile("r").readline().strip())
