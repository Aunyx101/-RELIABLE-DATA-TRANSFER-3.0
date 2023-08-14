import socket

def calculate_checksum(packet):
    # Simple checksum calculation
    return sum([ord(c) for c in packet]) % 256

def rdt_send(sock, data, packet_size=1024, timeout=0.0001, seq_no=0):
    MAX_RESENDS = 3  # maximum number of times a packet can be resent
    #server_address = ('localhost', 10000)
    # Break data into packets
    packets = data.split(" ")
    print(packets)
    for packet in packets:
        # Add sequence number and checksum to packet
        packet_with_seqno =  str(seq_no)+ ':'+ packet 
        checksum = calculate_checksum(packet_with_seqno)
        packet = packet_with_seqno + ":" + str(checksum).zfill(3)
        print('\n\n\n'+packet)
        # Send packet to server
        sock.send(packet.encode())
        print("Sent packet:", seq_no)
        # Wait for acknowledgment
        sock.settimeout(timeout)
        num_resends = 0  # counter for number of times packet has been resent
        while True:
            try:
                ack = sock.recv(packet_size)
                ack_seq_no, ack_checksum = ack.decode().split(":")[1:3]
                if int(ack_seq_no) == seq_no and int(ack_checksum) == calculate_checksum("ACK:" + ack_seq_no):
                    print("Received ACK:", seq_no)
                    seq_no = 1 - seq_no
                    break  # exit the loop and send the next packet
                else:
                    print("Received NAK:", 1 - seq_no)
                    if num_resends < MAX_RESENDS:
                        num_resends += 1
                        print(f"Resending packet ({num_resends}/{MAX_RESENDS}):", seq_no)
                        # resend the packet
                        sock.send(packet.encode())
                        print("Sent packet:", seq_no)
                        continue
                    else:
                        print(f"Max resends ({MAX_RESENDS}) reached. Aborting transmission.")
                        return
            except socket.timeout:
                if num_resends < MAX_RESENDS:
                    num_resends += 1
                    print(f"Timeout: Resending packet ({num_resends}/{MAX_RESENDS}):", seq_no)
                    # resend the packet
                    sock.send(packet.encode())
                    print("Sent packet:", seq_no)
                    continue
                else:
                    print(f"Max resends ({MAX_RESENDS}) reached. Aborting transmission.")
                    return
            except ConnectionAbortedError:
                print("Connection closed unexpectedly. Aborting transmission.")
                return

def main():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the server's IP address and port
    server_address = ('localhost', 10000)
    print('Connecting to %s port %s' % server_address)
    sock.connect(server_address)

    # Send data
    data = ''
    
    with open('./example.txt') as file:
        data = file.read()
   
    rdt_send(sock, data)

    # Close the socket
    #print('Closing socket')
    #sock.close()

if __name__ == '__main__':
    main()
