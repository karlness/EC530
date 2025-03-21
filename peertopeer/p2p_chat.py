import socket
import sys
import threading

# ANSI escape codes for colors
GREEN = "\033[92m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

def receive_messages(sock, peer_label):
    """
    Continuously receive messages from the socket and print them in a colored format.
    """
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                # Connection closed
                print(f"{CYAN}[System]{RESET} Peer has disconnected.")
                break
            message = data.decode()
            print(f"{peer_label}{message}{RESET}")
        except:
            print(f"{CYAN}[System]{RESET} Connection lost.")
            break

def send_messages(sock, self_label):
    """
    Continuously read user input and send it over the socket.
    """
    while True:
        try:
            msg = input("")
            if msg.strip() == "":
                continue 
            # Send message
            sock.sendall(msg.encode())
            # display message locally
            print(f"{self_label}{msg}{RESET}")
        except:
            print(f"{CYAN}[System]{RESET} Unable to send message. Exiting.")
            break

def run_server(port):
    """
    Start a server that waits for a single incoming connection, then starts chatting.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(1)
    print(f"{CYAN}[System]{RESET} Server listening on port {port}...")

    client_socket, client_address = server_socket.accept()
    print(f"{CYAN}[System]{RESET} Connected by {client_address}")

    
    threading.Thread(
        target=receive_messages,
        args=(client_socket, f"{GREEN}<{client_address}> "),
        daemon=True
    ).start()

    threading.Thread(
        target=send_messages,
        args=(client_socket, f"{BOLD}<You> {RESET}{GREEN}"),
        daemon=True
    ).start()

    
    while True:
        pass

def run_client(host, port):
    """
    Connect to the server and start chatting.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print(f"{CYAN}[System]{RESET} Connected to server at {host}:{port}")

    
    threading.Thread(
        target=receive_messages,
        args=(client_socket, f"{GREEN}<Server> "),
        daemon=True
    ).start()

    threading.Thread(
        target=send_messages,
        args=(client_socket, f"{BOLD}<You> {RESET}{GREEN}"),
        daemon=True
    ).start()

    while True:
        pass

if __name__ == "__main__":
    """
    Usage:
      python p2p_chat.py server <port>
      python p2p_chat.py client <host> <port>
    """
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python p2p_chat.py server <port>")
        print("  python p2p_chat.py client <host> <port>")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "server":
        if len(sys.argv) != 3:
            print("Usage: python p2p_chat.py server <port>")
            sys.exit(1)
        port = int(sys.argv[2])
        run_server(port)
    elif mode == "client":
        if len(sys.argv) != 4:
            print("Usage: python p2p_chat.py client <host> <port>")
            sys.exit(1)
        host = sys.argv[2]
        port = int(sys.argv[3])
        run_client(host, port)
    else:
        print("Unknown mode. Use 'server' or 'client'.")
