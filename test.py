import socket
import threading
import time
import json
import streamlit as st
from datetime import datetime, timedelta

# Konfiguracja serwera
HOST = "0.0.0.0"
PORT = 8080
BUFFER_SIZE = 1024
FLOOD_LIMIT = 1000
TIME_WINDOW = 2  # w sekundach
BLACKLIST_TIME = 600  # w sekundach
MAX_MESSAGE_LENGTH = 512

# Globalne zmienne
connections = {}
flood_stats = {}
blacklist = {}
log_file = "server_log.txt"
lock = threading.Lock()

# Funkcja logowania zdarzeń
def log_event(message, is_attack=False, is_error=False):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_type = "INFO"
    if is_attack:
        log_type = "ATTACK"
    elif is_error:
        log_type = "ERROR"
    log_message = f"{timestamp} [{log_type}] {message}\n"
    with lock:
        with open(log_file, "a") as f:
            f.write(log_message)
    st.write(log_message)

# Sprawdzanie floodowania
def is_flooding(ip):
    now = time.time()
    if ip not in flood_stats:
        flood_stats[ip] = []
    flood_stats[ip].append(now)
    flood_stats[ip] = [t for t in flood_stats[ip] if now - t < TIME_WINDOW]
    return len(flood_stats[ip]) > FLOOD_LIMIT

# Dodawanie do czarnej listy
def add_to_blacklist(ip):
    blacklist[ip] = time.time() + BLACKLIST_TIME
    log_event(f"IP {ip} dodane do czarnej listy.", is_attack=True)

# Sprawdzanie czarnej listy
def is_blacklisted(ip):
    return ip in blacklist and time.time() < blacklist[ip]

# Obsługa klienta
def handle_client(client_sock, client_ip):
    if is_blacklisted(client_ip):
        log_event(f"Połączenie odrzucone - {client_ip} jest na czarnej liście.", is_attack=True)
        client_sock.close()
        return
    
    if is_flooding(client_ip):
        log_event(f"Wykryto floodowanie z {client_ip}, blokowanie.", is_attack=True)
        add_to_blacklist(client_ip)
        client_sock.close()
        return
    
    try:
        data = client_sock.recv(BUFFER_SIZE).decode("utf-8")
        if len(data) > MAX_MESSAGE_LENGTH:
            log_event(f"Zbyt długa wiadomość od {client_ip}, możliwy atak.", is_attack=True, is_error=True)
            client_sock.close()
            return
        log_event(f"Odebrano od {client_ip}: {data}")
        client_sock.sendall(b"OK")
    except Exception as e:
        log_event(f"Błąd od {client_ip}: {str(e)}", is_error=True)
    finally:
        client_sock.close()

# Główna funkcja serwera
def start_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen()
    log_event(f"Serwer nasłuchuje na {HOST}:{PORT}")
    
    while True:
        client_sock, client_addr = server_sock.accept()
        client_ip = client_addr[0]
        threading.Thread(target=handle_client, args=(client_sock, client_ip), daemon=True).start()

# Interfejs Streamlit
def main():
    st.title("Serwer TCP z ochroną przed atakami")
    if st.button("Uruchom serwer"):
        threading.Thread(target=start_server, daemon=True).start()
        st.write("Serwer działa...")
    st.write("### Logi serwera")
    if st.button("Odśwież logi"):
        with open(log_file, "r") as f:
            logs = f.read()
        st.text_area("Logi", logs, height=300)

if __name__ == "__main__":
    main()
