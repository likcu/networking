import udt
import util
import helper
import struct
import config
from datetime import datetime


# Go-Back-N reliable transport protocol.
class GoBackN:
  # "msg_handler" is used to deliver messages to application layer
  # when it's ready.
  def __init__(self, local_ip, local_port,
               remote_ip, remote_port, msg_handler):
    self.network_layer = udt.NetworkLayer(local_ip, local_port,
                                          remote_ip, remote_port, self)
    self.msg_handler = msg_handler
    self.base = 0
    self.nextSeqnum = 0
    self.pktarray = []
    self.expectedSeqnum = 0
    self.timer = util.PeriodicClosure(self.time_out,0.3)
    self.starttime = datetime.utcnow()

  #implement the fucntion when time out triggerd
  def time_out(self):
    for i in range(self.base,self.nextSeqnum):
      self.network_layer.send(self.pktarray[i])


  # "send" is called by application. Return true on success, false
  # otherwise.
  def send(self, msg):
    # TODO: impl protocol to send packet from application layer.
    # call self.network_layer.send() to send to network layer.
    if self.nextSeqnum < self.base + config.WINDOW_SIZE:
      self.pktarray.append(helper.make_pkt(config.MSG_TYPE_DATA,self.nextSeqnum,msg))
      # print('send data',self.nextSeqnum) 
      self.network_layer.send(self.pktarray[self.nextSeqnum])
      if self.base == self.nextSeqnum:
        self.timer.start()
      self.nextSeqnum += 1
      return True
    else:
      return False


  # "handler" to be called by network layer when packet is ready.
  def handle_arrival_msg(self):
    msg = self.network_layer.recv()
    # TODO: impl protocol to handle arrived packet from network layer.
    # call self.msg_handler() to deliver to application layer.
    typ = struct.unpack('!h',msg[0:2])[0]
    seqnum = struct.unpack('!h',msg[2:4])[0]
    #if receive ACK
    if typ == config.MSG_TYPE_ACK: 
      checksum = struct.pack('!h',helper.checksum(typ,seqnum,b''))
      if msg[4:6] == checksum:
        self.base = seqnum + 1
        if self.base == self.nextSeqnum:
          self.timer.stop()
        else:
          self.timer.start()
    #if receive Data
    elif typ == config.MSG_TYPE_DATA: 
      extract_data = msg[6:len(msg)]
      checksum = struct.pack('!h',helper.checksum(typ,seqnum,extract_data))
      if msg[4:6] == checksum and self.expectedSeqnum == seqnum:
        self.msg_handler(extract_data)
        #calculate the latency
        endtime = datetime.utcnow()
        diftime = endtime - self.starttime
        print (str(diftime.seconds) + " seconds")
        sndpkt = helper.make_pkt(config.MSG_TYPE_ACK,self.expectedSeqnum,b'')
        self.network_layer.send(sndpkt)
        self.expectedSeqnum += 1
      #if corrupted or not expected seqnum, send again
      else:
        sndpkt = helper.make_pkt(config.MSG_TYPE_ACK,self.expectedSeqnum-1,b'')
        self.network_layer.send(sndpkt)


  # Cleanup resources.
  def shutdown(self):
    # TODO: cleanup anything else you may have when implementing this
    # class.
    print("shutdown")
    self.network_layer.shutdown()
