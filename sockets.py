import socket

raspberry_pi_address = 'raspberrypi'
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the Raspberry Pi server
client_socket.connect((raspberry_pi_address, 5000))
print("Connected to Raspberry Pi.")

while True:
    message = input("Enter a message (or 'exit' to close): ")
    client_socket.sendall(message.encode('utf-8'))

    if message.lower() == 'exit':
        # Close the connection if the user enters 'exit'
        break

# Close the socket
client_socket.close()
