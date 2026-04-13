import socket
import struct
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SERVER_IP = "127.0.0.1"
SERVER_PORT = 9999
POLL_ID = 1

AES_KEY = b'12345678901234567890123456789012'
aesgcm = AESGCM(AES_KEY)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
seq_no = 1

def send_vote(client_id, choice):
    global seq_no
    try:
        # Create packet
        packet = struct.pack("!I H B I", client_id, POLL_ID, choice, seq_no)
        
        # Encrypt packet
        nonce = os.urandom(12)
        encrypted = aesgcm.encrypt(nonce, packet, None)
        
        # Send
        sock.sendto(nonce + encrypted, (SERVER_IP, SERVER_PORT))
        
        # Receive ACK
        sock.settimeout(2.0)
        data, _ = sock.recvfrom(1024)
        
        # Decrypt ACK
        ack_nonce = data[:12]
        ack_cipher = data[12:]
        decrypted = aesgcm.decrypt(ack_nonce, ack_cipher, None)
        
        ack_client, ack_poll, ack_seq, status = struct.unpack("!I H I B", decrypted)
        print(f"\n[+] VOTE RECORDED  ·  client {ack_client}  ·  poll {ack_poll}  ·  seq {ack_seq}")
        seq_no += 1
        
    except socket.timeout:
        print("\n[-] Error: Server request timed out.")
    except Exception as e:
        print(f"\n[-] Error: {e}")

def main():
    print("====================================")
    print("    SECURE UDP VOTING TERMINAL CLI  ")
    print("====================================")
    
    while True:
        try:
            cid_raw = input("\nEnter Client ID (integer), or 'q' to quit: ").strip()
            if cid_raw.lower() == 'q':
                break
                
            client_id = int(cid_raw)
            
            print("Options: \n 1. Option A\n 2. Option B\n 3. Option C")
            choice_raw = input("Enter Choice (1, 2, or 3): ").strip()
            choice = int(choice_raw)
            
            if choice not in [1, 2, 3]:
                print("[-] Invalid choice.")
                continue
                
            send_vote(client_id, choice)
            
        except ValueError:
            print("[-] Please enter valid numbers.")
        except KeyboardInterrupt:
            break
            
if __name__ == "__main__":
    main()
