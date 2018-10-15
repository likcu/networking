# This example is using Python 3
import socket
import time
import _thread
import struct

# Get host name, IP address, and port number.
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print(host_ip)
host_port = 8181

# Make a TCP socket object.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind to server IP and port number.
s.bind((host_ip, host_port))

# Listen allow 5 pending connects.
s.listen(5)

print('\nProxy Server started. Waiting for connection...\n')
print(host_ip)

# Current time on the server.
def now():
    return time.ctime(time.time())

# get Server Name
def getServerName(conn):
    webServerName = b''
    while True:
        temp = conn.recv(1)
        if(temp.decode("utf-8") == '/'): break
        webServerName += temp
    return webServerName.decode('utf-8')
# get rest files path
def getFile(conn):
    filePath = bytearray()
    filePath += '/'.encode('utf-8')
    while True:
        temp = conn.recv(1)
        if(temp.decode("utf-8") == ' '): break
        filePath += temp
    return filePath.decode('utf-8')

getInByte = 'GET'.encode('utf-8')
def handler(conn,bufsize):
    request = conn.recv(3)
    GET = 'GET'
    if request == getInByte:
        conn.recv(8)
        webServerName = getServerName(conn)
        filePath = getFile(conn)
        # connect to remote server
        server_ip = socket.gethostbyname(webServerName)
        server_port = 80
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.connect((server_ip,server_port))
        print('Connected to remote server',server_ip,':',server_port)
        # send request to remote server
        newRequest = GET + ' http://' + webServerName + filePath + ' ' + 'HTTP/1.1\r\nHost: ' + webServerName + '\r\nConnection: close\r\n\r\n'
        s2.sendall(newRequest.encode('utf-8'))
        # receive server's response
        while True:
            message = s2.recv(bufsize)
            if not message:
                break
            conn.sendall(message)
        s2.close()
    else:
        bad_request = '400 Bad Request'
        conn.sendall(bad_request.encode('utf-8'))
    conn.close()

while True:
    conn, addr = s.accept()
    print('Server connected by', addr,'at', now())
    _thread.start_new(handler, (conn,1024))
