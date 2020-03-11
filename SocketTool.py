#!/usr/bin/python3
import socket

class SocketTool(object):
    def __init__(self, ip, port):
        sock_timeout_secs = 4
        self.packet_end = bytes('\r\n','ascii')
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(sock_timeout_secs)
        self.s.connect((ip, port))
        print('Successfully connect socket, Using port', port)

    def send_only(self, cmd):
        self.s.sendall(bytes(cmd,'ascii'))

    def recv_end(self):
        total_data=[]
        data=''
        while True:
            data=self.s.recv(1024)
            if self.packet_end in data:
                total_data.append(data[:data.find(self.packet_end)])
                break
            total_data.append(data)
            if len(total_data)>1:
                #check if end_of_data was split
                last_pair=total_data[-2]+total_data[-1]
                if self.packet_end in last_pair:
                    total_data[-2]=last_pair[:last_pair.find(self.packet_end)]
                    total_data.pop()
                    break
        return b''.join(total_data)

    def send_receive_string(self, cmd):
        self.s.sendall(bytes(cmd,'ascii'))

        #print('Cmd', repr(cmd))
        data = self.recv_end()

        #print('Received', repr(data))
        return data.decode('ascii')
