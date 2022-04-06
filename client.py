from multiprocessing import Value
from threading import Timer
from utils import States
import multiprocessing
import random
import socket
import time
import utils

UDP_IP = "127.0.0.1"
UDP_PORT = 5005 # for testing without channel
#UDP_PORT = 5007 # for testing with channel
MSS = 12 # maximum segment size

sock = socket.socket(socket.AF_INET,    # Internet
                     socket.SOCK_DGRAM) # UDP

def send_udp(message):
  sock.sendto(message, (UDP_IP, UDP_PORT))

class Client:
  def __init__(self):
    self.client_state = States.CLOSED
    self.last_received_ack = 0
    self.last_received_seq_num = 0
    self.handshake()

  def handshake(self):
    while self.client_state != States.ESTABLISHED:
      if self.client_state == States.CLOSED:
        seq_num = utils.rand_int()
        self.next_seq_num = seq_num + 1
        syn_header = utils.Header(seq_num, 0, syn = 1, ack = 0, fin = 0)
        send_udp(syn_header.bits())
        self.update_state(States.SYN_SENT)
      elif self.client_state == States.SYN_SENT:
        recv_data, addr = sock.recvfrom(1024)
        syn_ack_header = utils.bits_to_header(recv_data)
        self.last_received_seq_num = syn_ack_header.seq_num
        if syn_ack_header.syn == 1 and syn_ack_header.ack == 1:
          ack_header = utils.Header( self.next_seq_num
                                   , self.last_received_seq_num + 1
                                   , syn = 0, ack = 1, fin = 0)
          self.next_seq_num += 1
          send_udp(ack_header.bits())
          self.update_state(States.ESTABLISHED)
      else:
        pass

  def terminate(self):
    while self.client_state != States.CLOSED:
      if self.client_state == States.ESTABLISHED:
        terminate_header = utils.Header(self.next_seq_num, self.last_received_seq_num + 1, syn = 0, ack = 1, fin = 1)
        self.next_seq_num += 1
        send_udp(terminate_header.bits())
        self.update_state(States.FIN_WAIT_1)
      elif self.client_state == States.FIN_WAIT_1:
        recv_data, addr = sock.recvfrom(1024)
        fin_ack_header = utils.bits_to_header(recv_data)
        self.last_received_seq_num = fin_ack_header.seq_num
        if fin_ack_header.ack == 1:
          self.update_state(States.FIN_WAIT_2)
      elif self.client_state == States.FIN_WAIT_2:
        recv_data, addr = sock.recvfrom(1024)
        fin_fin_header = utils.bits_to_header(recv_data)
        self.last_received_seq_num = fin_fin_header.seq_num
        if fin_fin_header.fin == 1:
          terminate_ack_header = utils.Header(self.next_seq_num, self.last_received_seq_num + 1, syn = 0, ack = 1, fin = 0)
          self.next_seq_num += 1
          send_udp(terminate_ack_header.bits())
          # self.update_state(States.TIME_WAIT) # not implemented
          self.update_state(States.CLOSED)
      else:
        pass

  def update_state(self, new_state):
    if utils.DEBUG:
      print(self.client_state, '->', new_state)
    self.client_state = new_state

  def send_reliable_message(self, message):
    # header could reuse seq so far, or just start back at 0 for sending message as this does
    # but need to keep track of the sequence number when doing 
    msg_header = utils.Header(0, 0, syn = 0, ack = 0, fin = 0)
    send_udp(msg_header.bits() + message.encode())
    
    
    # handle mss to send in pieces
    # our pa03 solution does something like:
    #     chunks=list(chunkstring(message, MSS)) # divide message into appropriate length segments
    # then sends each of these, appropriately handling message size=MSS and seq numbers
    # handle seq / ack appropriately
    # handle stop and wait: resend if lost, detected by no ack in time
    # recommend handling this via a recv and waiting until socket.timeout exception occurs, then resending

if __name__ == "__main__":
  client = Client()

  # be sure to test with several messages of varying length as discussed
  # particularly, be sure things work when (1) client->server msgs are lost
  # and (2) server->client acks are lost
  # the server should display the received full message at the end, in 
  # the correct order, with all pieces and no missing/duplicated data
  client.send_reliable_message("This message should be received in pieces.")
  
  # increasing number test message (useful for debugging)
  #n_seg = 50
  #x = [str(i) + ' ' for i in range(0,MSS * n_seg)]
  #x_str = ''.join(x)
  #client.send_reliable_message(x_str)

  client.terminate()
