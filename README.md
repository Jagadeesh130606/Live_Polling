# 🔐 Secure UDP Voting System

A secure, event-driven voting system built using UDP sockets and AES-GCM encryption.  
This project demonstrates networking, security, and performance analysis concepts.

---

## 🚀 Features

- 🔒 End-to-end encryption using AES-GCM  
- ⚡ Fast UDP-based communication  
- 🖥️ GUI Voting Client (Tkinter)  
- 💻 CLI Voting Client  
- 📊 Performance testing & metrics analysis  
- 🛡️ Duplicate vote detection  
- 📁 Server logging system  

---

## 📂 Project Structure


├── server.py # Main UDP server
├── client.py # GUI voting client
├── client_cli.py # CLI voting client
├── performance.py # Performance testing tool
├── server.log # Server logs (auto-generated)


---

## 🧠 How It Works

1. Client sends encrypted vote packet (client_id, poll_id, choice, sequence)  
2. Server decrypts and processes the vote  
3. Duplicate votes are detected and rejected  
4. Server sends encrypted acknowledgment (ACK)  
5. Results are stored and logged  

Example log:


VOTE_COUNTED | Client 123 | Choice 1
DUPLICATE_VOTE | Client 9999 | Seq 2


---

## ⚙️ Requirements

- Python 3.x  

Install dependency:


pip install cryptography


---

## ▶️ How to Run

### 1️⃣ Start Server


python server.py


---

### 2️⃣ Run GUI Client


python client.py


- Enter Client ID  
- Select option  
- Submit vote  

---

### 3️⃣ Run CLI Client


python client_cli.py


- Enter client ID and choice  

---

### 4️⃣ Run Performance Test


python performance.py


- Tests latency, throughput, and scalability  

---

## 🔐 Security

- Uses AES-GCM for authenticated encryption  
- Prevents replay attacks using sequence numbers  
- Duplicate vote protection using `(client_id, poll_id)` tracking  

---

## 📊 Performance Insights

- Low latency UDP communication  
- Scales to multiple concurrent clients  
- Real-time metrics validation from logs  

---
