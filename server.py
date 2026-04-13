import socket
import struct
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ================= CONFIG =================
SERVER_PORT = 9999

# AES key (must be EXACTLY same as client)
AES_KEY = b'12345678901234567890123456789012'
aesgcm = AESGCM(AES_KEY)

# ================= SOCKET =================
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind(("", SERVER_PORT))

print("Secure UDP Voting Server running...")

# ================= DATA STRUCTURES =================
seen_votes = set()
poll_results = {}

def print_results_table(poll_results):
    print("\nPollID | Choice | Count")
    print("----------------------")
    for poll_id, choices in poll_results.items():
        for choice, count in choices.items():
            print(f"{poll_id:^6} | {choice:^6} | {count:^5}")

# ================= SERVER LOOP =================
while True:
    data, clientAddress = serverSocket.recvfrom(1024)

    try:
        # ================= DECRYPT PACKET =================
        nonce = data[:12]
        ciphertext = data[12:]

        decrypted = aesgcm.decrypt(nonce, ciphertext, None)

        client_id, poll_id, choice, seq_no = struct.unpack("!I H B I", decrypted)

        vote_key = (client_id, poll_id)

        # ================= PROCESS VOTE =================
        if vote_key not in seen_votes:
            seen_votes.add(vote_key)

            if poll_id not in poll_results:
                poll_results[poll_id] = {}

            if choice not in poll_results[poll_id]:
                poll_results[poll_id][choice] = 0

            poll_results[poll_id][choice] += 1

            msg = f"VOTE_COUNTED | Client {client_id} | Choice {choice}"
            print(msg)
            with open("server.log", "a") as f:
                f.write(msg + "\n")

        else:
            msg = f"DUPLICATE_VOTE | Client {client_id} | Seq {seq_no}"
            print(msg)
            with open("server.log", "a") as f:
                f.write(msg + "\n")

        # ================= CREATE ACK =================
        ack_packet = struct.pack(
            "!I H I B",
            client_id,
            poll_id,
            seq_no,
            1
        )

        # ================= ENCRYPT ACK =================
        ack_nonce = os.urandom(12)
        encrypted_ack = aesgcm.encrypt(ack_nonce, ack_packet, None)

        serverSocket.sendto(ack_nonce + encrypted_ack, clientAddress)

        print_results_table(poll_results)

    except Exception as e:
        print("Decryption / processing error:", e)
        
        
        