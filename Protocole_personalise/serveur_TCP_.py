import socket

# XOR key for encryption
XOR_KEY = 0x55

def xor_encrypt_decrypt(data, key):
    return bytearray([b ^ key for b in data])

def start_server(host='10.2.13.200', port=8080):
    """Start the custom protocol server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server started, listening on {host}:{port}")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection established with {addr}")
        
        try:
            while True:  # Keep the connection open
                encrypted_data = client_socket.recv(1024)
                if not encrypted_data:
                    break  # Client closed the connection
                
                # Decrypt the message using XOR
                decrypted_data = xor_encrypt_decrypt(encrypted_data, XOR_KEY).decode()
                
                # Process the message
                device_id = decrypted_data[:5]
                status = decrypted_data[5:]
                print(f"Decrypted data received:\n          Device ID: {device_id}, DATA: {status}")
                
                # Encrypt the message to send back to the client
                response = f"Received successfully: Device ID: {device_id}, DATA: {status}"
                encrypted_response = xor_encrypt_decrypt(response.encode(), XOR_KEY)
                print(f"encrypted response:\n          {list(encrypted_response)}")
                # Send the encrypted response back to the client
                client_socket.sendall(encrypted_response)

        except Exception as e:
            print(f"Error during connection: {e}")
        finally:
            print(f"Closing connection with {addr}")
            client_socket.close()

if __name__ == "__main__":
    start_server()