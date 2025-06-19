import socket
import time
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

HOST = 'localhost'
PORT = 65432
server_socket = None
server_running = False

def run_key_server(key):
    global server_socket, server_running
    logging.debug("Starting key server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)  # Allow up to 5 queued connections
        server_running = True
        logging.info(f"Key server listening on {HOST}:{PORT}")
        
        while server_running:
            try:
                conn, addr = server_socket.accept()
                logging.info(f"Key server accepted connection from {addr}")
                with conn:
                    conn.sendall(key)
                    logging.debug(f"Sent key: {key.hex()}")
            except socket.error as e:
                if not server_running:
                    logging.debug("Key server stopped, ignoring socket error")
                    break
                logging.warning(f"Connection handling error: {e}")
                continue
            except Exception as e:
                logging.warning(f"Unexpected error in key server: {e}")
                continue
    except Exception as e:
        logging.error(f"Key server error: {e}")
    finally:
        if server_socket:
            server_socket.close()
        server_running = False
        logging.debug("Key server closed")

def receive_key():
    logging.debug("Attempting to receive key...")
    for attempt in range(20):  # 20 retries
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)  # 3-second timeout per attempt
                s.connect((HOST, PORT))
                key = s.recv(16)  # Receive exactly 16 bytes
                logging.info(f"Received key: {key.hex()}")
                return key
        except Exception as e:
            logging.warning(f"Connection attempt {attempt + 1} failed: {e}")
            time.sleep(1)  # Wait 1 second before retrying
    logging.error("Failed to connect to key server after all retries")
    raise Exception("Failed to connect to key server")

def stop_key_server():
    global server_socket, server_running
    logging.debug("Stopping key server...")
    server_running = False
    if server_socket:
        try:
            server_socket.close()
            logging.debug("Key server socket closed")
        except Exception as e:
            logging.error(f"Error closing key server socket: {e}")
    logging.debug("Key server stopped")