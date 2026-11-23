import os
import socket
import uvicorn

def find_available_port(preferred_port=8001):
    """Check if preferred port is open, otherwise choose next available."""
    for port in [preferred_port, 8000, 8080, 5000]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return preferred_port

if __name__ == "__main__":
    configured_port = os.getenv("PORT")
    port = int(configured_port) if configured_port else find_available_port(8001)
    print(f"Starting BusFlow Backend on http://127.0.0.1:{port}")
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=False)
