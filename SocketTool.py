#!/usr/bin/python3
import socket

class SocketTool(object):
    def __init__(self, ip, port, packet_end_string):
        sock_timeout_secs = 4
        self.packet_end_string = packet_end_string
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(sock_timeout_secs)
        self.s.connect((ip, port))
        print('Successfully connect socket, Using port', port)

    def send_only(self, cmd):
        self.s.sendall(bytes(cmd+"\r\n",'ascii'))
        #print('Cmd', repr(cmd))

    def recv_end(self, end_string, isPrint):
        end_byte = bytes(end_string ,'ascii')
        total_data=[]
        data=''
        while True:
            data=self.s.recv(1024)
            if isPrint: print(data)
            if end_byte in data:
                total_data.append(data[:data.find(end_byte)])
                break
            total_data.append(data)
            if len(total_data)>1:
                #check if end_of_data was split
                last_pair=total_data[-2]+total_data[-1]
                if end_byte in last_pair:
                    total_data[-2]=last_pair[:last_pair.find(end_byte)]
                    total_data.pop()
                    break
        return b''.join(total_data)

    def send_receive_string(self, cmd, end_string = None, isPrint = False):
        self.s.sendall(bytes(cmd+"\r\n",'ascii'))
        #print('Cmd', repr(cmd))

        if end_string == None:
            data = self.recv_end(self.packet_end_string, isPrint)
        else:
            data = self.recv_end(end_string, isPrint)

        #print('Received', repr(data))
        return data.decode('ascii')
