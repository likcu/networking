# This example is using Python 3
import socket
import time
import _thread
import struct



# Get host name, IP address, and port number.
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
host_port = 8181

# Make a TCP socket object.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind to server IP and port number.
s.bind((host_ip, host_port))

# Listen allow 5 pending connects.
s.listen(5)

print('\nServer started. Waiting for connection...\n')
print(host_ip)

# Current time on the server.
def now():
    return time.ctime(time.time())

# Calculator
def calc(s):  
    def update(op, num):
        if op == '+':
            stack.append(num)
        elif op == '-':
            stack.append(-num)
        elif op == '*':
            stack.append(stack.pop() * num)
        elif op == '/':
            stack.append(stack.pop() // num)
    
    stack = []
    num, op = 0, '+'
    for i in range(len(s)):
        if s[i].isdigit():
            num = num * 10 + int(s[i])
        elif s[i] in ['+', '-', '*', '/', ')']:
            update(op, num)
            if s[i] == ')':
                num = 0
                while isinstance(stack[-1], int):
                    num += stack.pop() 
                op = stack.pop()
                update(op, num)
            num, op = 0, s[i]
        elif s[i] == '(':
            stack.append(op)
            num, op = 0, '+'
    update(op, num)
    return str(sum(stack))

#recieve the whole message,return the massage as bytearray
def recieveAll(conn,bufsize):
    message = bytearray()
    message += conn.recv(2)
    len = struct.unpack('!h', message)[0]
    for i in range(0, len):
        message += conn.recv(2)
        exp_len = struct.unpack('!h', message[-2:])[0]
        if exp_len <= bufsize:
            message += conn.recv(exp_len)
        else :
            message += conn.recv(bufsize) + conn.recv(exp_len - bufsize)
    return message

#calculate all expression and reserialize it into response result, return the response as bytearray
def process(message):
    response = bytearray()
    numOfExpress = message[0:2]
    response += numOfExpress
    index = 2
    while index < len(message):
        lenOfExpression = struct.unpack('!h',message[index:index+2])[0] 
        expression = message[index+2:index+2+lenOfExpression].decode('utf-8') 
        result = calc(expression) 
        lenOfResult = len(result)
        response += struct.pack('!h',lenOfResult)
        response += result.encode('utf-8')
        index += 2+lenOfExpression
    return response

# handler the whole process
def handler(conn):
    bufsize = 16
    message = recieveAll(conn,bufsize)
    result = process(message)
    conn.sendall(result)
    conn.close()

while True:
    conn, addr = s.accept()
    print('Server connected by', addr,'at', now())
    _thread.start_new(handler, (conn,))
