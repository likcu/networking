# This example is using Python 3
import socket
import struct

# Make a TCP socket object.
#
# API: socket(address_family, socket_type)
#
# Address family
#   AF_INET: IPv4
#   AF_INET6: IPv6
#
# Socket type
#   SOCK_STREAM: TCP socket
#   SOCK_DGRAM: UDP socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server machine and port.
#
# API: connect(address)
#   connect to a remote socket at the given address.
server_ip = '10.142.0.3'
server_port = 8181
s.connect((server_ip, server_port))
print('Connected to server ', server_ip, ':', server_port)

# messages to send to server.
message = [2, 11, '(1+2)*(3+4)', 21, '(((-11+6)*5+6)*9+7)/4']

# Send messages to server over socket.
#
# API: send(bytes)
#   Sends data to the connected remote socket.
#   Returns the number of bytes sent. Applications
#   are responsible for checking that all data
#   has been sent
#
# API: recv(bufsize)
#   Receive data from the socket. The return value is
#   a string representing the data received. The
#   maximum amount of data to be received at once is
#   specified by bufsize
#
# API: sendall(bytes)
#   Sends data to the connected remote socket.
#   This method continues to send data from string
#   until either all data has been sent or an error
#   occurs.


# transform the message into required the format
def transform(message):
    res = b''
    res += struct.pack('!h',message[0])
    isExpression = False
    for i in range(1,len(message)):
        if not isExpression:
            res += struct.pack('!h',message[i])
            isExpression = True
        else:
            res += message[i].encode('utf-8')
            isExpression = False
    return res

#recieve the whole reponse and return the response as a bytearray
def recieveAll(bufsize):
    message = bytearray()
    message += s.recv(2)
    len = struct.unpack('!h', message)[0]
    for i in range(0, len):
        message += s.recv(2)
        res_len = struct.unpack('!h', message[-2:])[0]
        if res_len <= bufsize:
            message += s.recv(res_len)
        else :
            message += s.recv(bufsize) + s.recv(res_len - bufsize)
    return message

#print the result
def printResult(res):
    print('Client received:')
    print(struct.unpack('!h',res[0:2])[0])
    index = 2
    while index < len(res):
        res_len = struct.unpack('!h',res[index:index+2])[0]
        print(res_len)
        result = res[index+2:index+2+res_len].decode('utf-8')
        print(result)
        index += 2 + res_len

#the cilent process of send and receive
bufsize = 16
s.sendall(transform(message))
print('Client sent:',message)
result = recieveAll(bufsize)
printResult(result)
# Close socket to send EOF to server.
s.close()
