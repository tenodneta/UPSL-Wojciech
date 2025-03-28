import streamlit as st
import socket
import threading
import time

# Konfiguracja dynamiczna
BUFFER_SIZE = st.slider("Buffer Size", 512, 4096, 1024)
FLOOD_LIMIT = st.slider("Flood Limit", 10, 5000, 1000)
TIME_WINDOW = st.slider("Time Window (s)", 1, 10, 2)
BLACKLIST_TIME = st.slider("Blacklist Time (s)", 60, 3600, 600)
MAX_MESSAGE_LENGTH = st.slider("Max Message Length", 256, 1024, 512)
PORT = 8080

# Flaga do zatrzymania ataku
stop_attack = False

# Funkcja serwera
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", PORT))
    server.listen(5)
    st.write(f"Serwer nasłuchuje na porcie {PORT}")
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client, addr)).start()

def handle_client(client, addr):
    ip = addr[0]
    data = client.recv(BUFFER_SIZE)
    if len(data) > MAX_MESSAGE_LENGTH:
        st.write(f"Odebrano zbyt długą wiadomość od {ip}. Blokowanie!")
    else:
        st.write(f"Odebrano od {ip}: {data.decode()}")
    client.sendall(b"OK")
    client.close()

# Klient TCP
def tcp_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", PORT))
    client.sendall(b"Hello, Server")
    response = client.recv(BUFFER_SIZE)
    st.write(f"Serwer odpowiedział: {response.decode()}")
    client.close()

# Flood klient
def flood_client():
    def attack():
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect(("127.0.0.1", PORT))
            client.sendall(b"FLOOD_ATTACK!")
            client.close()
        except:
            pass
    
    threads = []
    for _ in range(FLOOD_LIMIT):
        if stop_attack:
            st.write("Atak zatrzymany!")
            break  # Zatrzymanie ataku, jeśli flaga jest ustawiona
        t = threading.Thread(target=attack)
        t.start()
        threads.append(t)
        time.sleep(0.01)
    
    for t in threads:
        t.join()

# Funkcja do zatrzymania ataku
def stop_flood_attack():
    global stop_attack
    stop_attack = True  # Ustawienie flagi, aby zatrzymać atak

# Interfejs Streamlit
st.title("TCP Server & Client GUI")
if st.button("Start Server"):
    threading.Thread(target=start_server, daemon=True).start()
if st.button("Send TCP Message"):
    tcp_client()
if st.button("Start Flood Attack"):
    stop_attack = False  # Resetowanie flagi przed uruchomieniem ataku
    threading.Thread(target=flood_client, daemon=True).start()
if st.button("Stop Flood Attack"):
    stop_flood_attack()  # Zatrzymanie ataku
