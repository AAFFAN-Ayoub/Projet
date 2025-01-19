import socket 
import time
import network
from machine import Pin, time_pulse_us

# XOR key for encryption
XOR_KEY = 0x55  # Arbitrary key for XOR encryption

# Wi-Fi configuration
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print("Connected to Wi-Fi:", wlan.ifconfig())

# Ultrasonic sensor setup
TRIG_PIN = 14
ECHO_PIN = 35

trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

def get_ultrasonic_distance():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    duration = time_pulse_us(echo, 1, 30000)
    if duration < 0:
        return -1  # Invalid reading

    distance = (duration / 2) * 0.0343  # Speed of sound in cm/us
    return round(distance, 2)

# XOR encryption function
def xor_encrypt_decrypt(data, key):
    return bytearray([b ^ key for b in data])

# Main function to send data
def send_data(host='192.168.0.120', port=8080):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        
        while True:
            distance = get_ultrasonic_distance()
            if distance < 0:
                print("Ultrasonic sensor reading failed.")
                continue
            
            if distance > 50:
                status = "No object"  # No object
            else:
                status = str(distance)  # Distance value
            
            # Prepare the message and encrypt it using XOR
            message = f"ESP32{status}".encode()  # Encode the message to bytes
            encrypted_message = xor_encrypt_decrypt(message, XOR_KEY)
            print(f"Sending encrypted message:\n          {list(encrypted_message)}")
            client_socket.send(encrypted_message)  # Send encrypted message
            
            # Receive response from server (encrypted)
            encrypted_response = client_socket.recv(1024)
            decrypted_response = xor_encrypt_decrypt(encrypted_response, XOR_KEY).decode()
            print(f"Decrypted server response:\n          {decrypted_response}")
            
            time.sleep(1)  # Wait 1 second before sending again

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    SSID = "kama"
    PASSWORD = "00000000"
    
    connect_to_wifi(SSID, PASSWORD)
    send_data()