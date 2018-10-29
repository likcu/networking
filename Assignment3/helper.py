import struct

# helper function that both gbn and ss will use

# calculate the checksum(calculation type seqnum and data 's checksum')
def checksum(typ,seqnum,msg):
	s = 0
	s = typ
	s += seqnum
	i = 0
	if len(msg) == 0:
		return s
	string = msg.decode('utf-8','ignore')
	while i < len(string):
	    s = s ^ ord(string[i])
	    i += 1
	return s

# make new packt(including type,seqnum,checksum,msg) 
def make_pkt(typ,seqnum,msg):
    pkt = b''
    pkt += struct.pack('!h',typ)
    pkt += struct.pack('!h',seqnum)
    chcks = checksum(typ,seqnum,msg)
    pkt += struct.pack('!h',chcks)
    pkt += msg
    return pkt