import socket
import sys

def Main():
        host = '127.0.0.1'
        port = 8081

        s = socket.socket()
        s.connect((host, port))

        message = input("->")
        while message != 'q':
            messageBytes = message.encode('utf-8')
            print(messageBytes)
            dataLength = len(messageBytes)
            print(dataLength)
            dataLengthRaw = bin(dataLength)

            print(dataLengthRaw)
            s.send(dataLengthRaw.encode('utf-8'))
            s.send(messageBytes)
            message = input("->")
        s.close()

if __name__ == '__main__':
    Main()
