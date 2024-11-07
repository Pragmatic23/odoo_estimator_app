from app import app
import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('0.0.0.0', port))
            return False
        except socket.error:
            return True

if __name__ == "__main__":
    # Try ports from 5000 to 5010
    port = 5000
    while is_port_in_use(port) and port < 5010:
        port += 1
        
    if port >= 5010:
        print("No available ports found between 5000 and 5009")
        exit(1)
        
    print(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port)
