import sys
import os
import time
import subprocess
import signal
import socket
from pathlib import Path

try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
FRONTEND_PORT = 8501

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((BACKEND_HOST, port)) == 0

def run():
    print("=" * 60)
    print("🚀 STARTING CLAUSECLEAR (Legal Tech Assistant)")
    print("🏆 Srijan Hackathon • GH Raisoni College of Engineering, Pune")
    print("=" * 60)

    # 1. Start FastAPI Backend
    print(f"\n[1/2] Starting FastAPI Backend on http://{BACKEND_HOST}:{BACKEND_PORT}...")
    backend_cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--host", BACKEND_HOST,
        "--port", str(BACKEND_PORT),
        "--reload"
    ]
    backend_proc = subprocess.Popen(backend_cmd, cwd=str(BASE_DIR))

    # Wait for backend to be ready
    for _ in range(20):
        if is_port_in_use(BACKEND_PORT):
            print(f"✅ Backend is live at http://{BACKEND_HOST}:{BACKEND_PORT}")
            break
        time.sleep(0.5)

    # 2. Start Streamlit Frontend
    print(f"\n[2/2] Starting Streamlit Frontend on http://localhost:{FRONTEND_PORT}...")
    frontend_cmd = [
        sys.executable, "-m", "streamlit", "run",
        "frontend/app.py",
        "--server.port", str(FRONTEND_PORT),
        "--server.headless", "false"
    ]
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=str(BASE_DIR))

    print("\n" + "=" * 60)
    print("🎉 CLAUSECLEAR IS RUNNING!")
    print(f"👉 Open in browser: http://localhost:{FRONTEND_PORT}")
    print(f"👉 Backend API docs: http://{BACKEND_HOST}:{BACKEND_PORT}/docs")
    print("👉 Press Ctrl+C to terminate both servers cleanly.")
    print("=" * 60 + "\n")

    def signal_handler(sig, frame):
        print("\n🛑 Stopping ClauseClear services...")
        try:
            frontend_proc.terminate()
            backend_proc.terminate()
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    run()
