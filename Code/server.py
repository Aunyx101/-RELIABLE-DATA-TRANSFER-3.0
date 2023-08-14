import socket
import time

def calculate_checksum(packet):
    # Simple checksum calculation
    return sum([ord(c) for c in packet]) % 256

def rdt_recv(connection,seq_no, packet_size=1024, timeout=10,last_seq_no=-1):
    while True:
        # Wait for packet
        #connection.settimeout(timeout)
        try:
            packet = connection.recv(packet_size)
            if packet == b'':
                exit(0)
            # Split packet into sequence number, data, and checksum
            packet_seq_no, packet_data, packet_checksum = packet.decode().split(":")
            packet_checksum = int(packet_checksum)
            packet_seq_no = int(packet_seq_no)
            # Check if received packet has the expected sequence number
            if packet_seq_no == seq_no:
                # Check checksum
                if packet_checksum != calculate_checksum(str(packet_seq_no) + ":" + packet_data):
                    print("Received packet with invalid checksum. Discarding packet.")
                    continue
                # Send ACK
                ack = "ACK:" + str(seq_no) + ":" + str(calculate_checksum("ACK:" + str(seq_no)))
               
                connection.send(ack.encode())
                print("Sent ACK:", seq_no)
                # Update sequence number
                seq_no = 1 - seq_no
                # Update last_seq_no
                last_seq_no = packet_seq_no
                # Return data
                return packet_data
            elif packet_seq_no <= last_seq_no:
                # Discard old packet
                print(packet)
                print("Received old packet. Discarding packet.")
            else:
                # Discard out-of-order packet
                print(packet)
                print("Received out-of-order packet. Discarding packet.")
        except socket.timeout:
            print("Timeout: no packets received in the last {} seconds".format(timeout))



def main():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific IP address and port
    server_address = ('localhost', 10000)
    print('Starting up on %s port %s' % server_address)
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)
    print('Waiting for a connection')
    connection, client_address = sock.accept()
    seq_no = 0
    while True:
        # Wait for a connection
        try:
            #print('Connection from', client_address)
            
            # Receive data
            data = rdt_recv(connection,seq_no)
            print("Received data:", data)

        finally:
            # Clean up the connection
            #print('Closing connection')
            #connection.close()
            #print('finnaly')
            seq_no = 1 - seq_no

if __name__ == '__main__':
    main()
