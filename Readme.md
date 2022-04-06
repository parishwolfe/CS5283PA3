# Milestone 1
This is a basic solution for the milestone 1.

The code implements the bare minimum requirement with no error control like packet loss.

# Milestone 2

For milestone 2, you need to implement `send_reliable_message` in client.py. For simplicity, MSS (maximum segment size) is set to 12 bytes. You can assume each character is 1 byte (no special encoding).

## Client

- The client will send messages in packets maximum size by MSS (12 bytes).
- If any of the messages are not `ACKed`, the client will retransmit them.

## Server

- The server will send `ACK` messages to the client.
- The server will print the message in whole after it received all pieces. (you are free to determine the end of the message.)
  + end of message can be similar '\r\n\r\n' sequence as in http headers
  + or you can print every once in a while depending on your buffer size
- Server is required to order the messages by their sequence numbers and server should send the correct `ack_number` in case any of the messages are missing.

## Test

Your code will be tested for out of order messages and packet loss. You can test your code for these cases by manipulating your client code or server code.
- Client can swap some of the packages while sending and see if the server will print them in correct order.
- You can skip some of the messages to send by client and see if the server is sending ack messages for the missing packets.
- Server can miss sending ack messages to check if the client will retransmit the same message.


## Submission

Please provide a readme document for any of your assumptions and additional features.

## Caveats / Notes

Sequence number is determined by number of bytes sent. If you send 10 bytes of data, the sequence number will increase by 10.
