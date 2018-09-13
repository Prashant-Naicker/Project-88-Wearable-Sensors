import socket
import sys
import struct

def Main():
        host = '165.227.60.238'
        port = 8081

        s = socket.socket()
        s.connect((host, port))

        message = input("->")
        while message != 'q':
            messageBytes = str(message).decode('utf-8')
            dataLength = len(messageBytes)
            dataLengthRaw = bytearray(struct.pack("<H", dataLength))
            
            s.send(dataLengthRaw)
            s.send(messageBytes)
            message = input("->")
        s.close()

if __name__ == '__main__':
    Main()
