"""_summary_
    This script sends example packet to the java server to check behaviour.
"""
from socket import socket, AF_INET, SOCK_STREAM

IP = '192.168.0.102'
PORT = 880
PACKET = bytes("X[0]#[TEST]#[TEMPERATURE]#[HUMIDITY]#[PRESSURE]#[DEWPOINT]XX", encoding='utf-8')


sock = socket(AF_INET, SOCK_STREAM)

try:
    sock.connect((IP,PORT))
    sock.sendall(PACKET)

except Exception as err:
    print(err)