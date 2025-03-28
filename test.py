import streamlit as st
import socket
import threading
import time
from collections import defaultdict

# Konfiguracja dynamiczna
BUFFER_SIZE = st.slider("Buffer Size", 512, 4096, 1024)
FLOOD_LIMIT = st.slider("Flood Limit", 10, 5000, 1000)
TIME_WINDOW = st.slider("Time Window (s)", 1, 10, 2)
BLACKLIST_TIME = st.slider("Blacklist Time (s)", 60, 3600, 600)
MAX_MESSAGE_LENGTH = st.slider("Max Message Length", 256, 1024, 512)
PORT = 8080

# Zmienna przechowująca dane o połączeniach
client_data = defaultdict(list)

# Funkcja do zarządzania połączeniami (weryfikacja flood ataku)
def handle_client(client, addr):
    ip = addr[0]
    current_time = time.time()
    
    # Sprawdzamy, czy IP jest zablokowane
    if is_blacklisted(ip, current_time):
        st.write(f"Adres IP {ip} jest zablokowany. Ignorowanie połączenia.")
        client.close()
        return
    
    # Dodajemy czas połączenia do listy
    client_data[ip].append(current_time)
    
    # Usuwamy stare dane, które wykraczają poza ustalony limit czasowy
    client_data[ip] = [t for t in client_data[ip] if current_time - t <= TIME_WINDOW]
    
    # Jeśli przekroczono limit połączeń w danym czasie, blokujemy IP
    if len(client_data[ip]) > FLOOD_LIMIT:
        blacklist(ip, current_time)
        st.write(f"Adres IP {ip} przekroczył limit połączeń i został zablokowany.")
        client.close()
        return
    
    # Odbieramy dane od klienta
    data = client.recv(BUFFER_SIZE)
    if len(data) > MAX_MESSAGE_LENGTH:
        st.write(f"Odebrano zbyt długą wiadomość od {ip}. Blokowanie!")
    else:
        st.write(f"Odebrano od {ip}: {data.decode()}")
    
    client.sendall(b"OK")
    client.close()

# Funkcja sprawdzająca, czy IP jest zablokowane
def is_blacklisted(ip, current_time):
    if ip in blacklist:
        return current_time - blacklist[ip] < BLACKLIST_TIME
    return False

# Funkcja dodająca IP do czarnej listy
def blacklist(ip, current_time):
    blacklist[ip] = current_time

# Funkcja serwera
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", PORT))
    server.listen(5)
    st.write(f"Serwer nasłuchuje na porcie {PORT}")
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client, addr)).start()

# Klient TCP
def tcp_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", PORT))
    client.sendall(b"Hello, Server")
    response = client.recv(BUFFER_SIZE)
    st.write(f"Serwer odpowiedział: {response.decode()}")
    client.close()

# Flood klient (na potrzeby testów)
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
        t = threading.Thread(target=attack)
        t.start()
        threads.append(t)
        time.sleep(0.01)
    
    for t in threads:
        t.join()

# Interfejs Streamlit
st.title("TCP Server & Client GUI")
if st.button("Start Server"):
    threading.Thread(target=start_server, daemon=True).start()
if st.button("Send TCP Message"):
    tcp_client()
if st.button("Start Flood Attack"):
    flood_client()

