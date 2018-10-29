import udt
import config
import util
import struct
import helper
from datetime import datetime

# Stop-And-Wait reliable transport protocol.
class StopAndWait:
  # "msg_handler" is used to deliver messages to application layer
  # when it's ready.
  
  def __init__(self, local_ip, local_port, 
               remote_ip, remote_port, msg_handler):
    self.network_layer = udt.NetworkLayer(local_ip, local_port,
                                          remote_ip, remote_port, self)
    self.msg_handler = msg_handler
    self.type = config.MSG_TYPE_DATA
    self.seqnum = 0
    self.lastSeqnum = -1 
    self.oldpkt = b''
    self.timer = util.PeriodicClosure(self.time_out,0.5)
    self.expectedSeqnum = 0
    self.starttime = datetime.utcnow()
  
  def time_out(self):
    self.network_layer.send(self.oldpkt)


  # "send" is called by application. Return true on success, false
  # otherwise.
  def send(self, msg):
    # TODO: impl protocol to send packet from application layer.
    # call self.network_layer.send() to send to network layer.
    if self.seqnum == self.lastSeqnum+1:
      sndpkt = helper.make_pkt(self.type,self.seqnum,msg)
      self.oldpkt = sndpkt
      self.network_layer.send(sndpkt)
      self.seqnum += 1
      self.timer.start()
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
      if msg[4:6] == checksum and self.lastSeqnum == seqnum - 1:
        self.timer.stop()
        self.lastSeqnum += 1
    #if receive Data
    elif typ == config.MSG_TYPE_DATA: 
      extract_data = msg[6:len(msg)]
      checksum = struct.pack('!h',helper.checksum(typ,seqnum,extract_data))
      if msg[4:6] == checksum and self.expectedSeqnum == seqnum:
        self.msg_handler(extract_data)
        endtime = datetime.utcnow()
        diftime = endtime - self.starttime
        print (str(diftime.seconds) + " seconds")
        sndpkt = helper.make_pkt(config.MSG_TYPE_ACK,seqnum,b'')
        self.network_layer.send(sndpkt)
        self.expectedSeqnum += 1
      else:
        sndpkt = helper.make_pkt(config.MSG_TYPE_ACK,self.expectedSeqnum-1,b'')
        self.network_layer.send(sndpkt)

  # Cleanup resources.
  def shutdown(self):
    # TODO: cleanup anything else you may have when implementing this
    # class.
    self.network_layer.shutdown()
