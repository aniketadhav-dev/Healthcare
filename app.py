import subprocess
import sys
import time

def start_services():
    print("🚀 Starting MediBook Services via bot.py...\n")

    # 1. Start Backend
    print("📡 Starting Backend (FastAPI) on Port 8000...")
    # Using python backend/main.py as per your setup instructions
    backend_process = subprocess.Popen([sys.executable, "backend/main.py"])

    # Wait for 2 seconds to let the backend DB initialize
    time.sleep(2)

    # 2. Start Frontend
    print("🌐 Starting Frontend (HTTP Server) on Port 3000...")
    frontend_process = subprocess.Popen([sys.executable, "frontend/server.py"])

    print("\n✅ All services are running!")
    print("👉 Frontend: http://localhost:3000/login.html")
    print("👉 Backend API: http://localhost:8000/docs\n")

    try:
        # Keep the script running so Docker container doesn't exit
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("Done.")

if __name__ == "__main__":
    start_services()
