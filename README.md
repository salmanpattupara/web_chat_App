# 💬 FastAPI Glassmorphism WebSocket Chat Application

A high-performance, real-time private messaging application built with a modern **FastAPI** backend and an extremely premium **Glassmorphism CSS dark-theme** frontend. It leverages native WebSockets for active chat communication, handles offline message queuing atomically, and logs all events locally.

---

## ✨ Key Features

*   **🔒 Premium Landing Overlay**: Users are presented with a gorgeous blur-glassmorphic entrance card on first load or refresh. A WebSocket handshake must succeed before they can enter the chat space.
*   **👥 Real-Time User Sidebar**: Displays all registered chat users. Displays dynamic green/gray status dots (Online/Offline) and precise "Last seen" timestamps read from the database in real-time.
*   **👤 Integrated User Profile**: Shows the currently logged-in user's personalized avatar initials (e.g., `SA` for `Salman`) and a pulsing active status bar at the bottom of the sidebar.
*   **🎨 Clean Empty-State Canvas**: If no user is selected in the sidebar, the chat window displays a clean glass-blur welcome card with a floating talk icon. Raw input boxes and disabled buttons are completely hidden.
*   **📬 Delivery Acknowledgments (ACK)**:
    *   **Delivered**: Outgoing messages show a green tick `✓ Delivered to [name]` as soon as the recipient receives the packet.
    *   **Pending (Offline)**: If the recipient is currently offline, a rotating loading icon `Pending (user offline) 🔃` appears in the conversation log.
*   **🔄 Atomic Offline Message Sync**: If a user sends a message to an offline contact, it is held in a pending state inside `message.json`. The split-second the contact goes online, the backend delivers all pending items atomically and triggers real-time delivery notifications back to the sender.
*   **📜 Dual-Output Event Logging**: Logging is customized to output clean, formatted trace information simultaneously to the active **terminal shell** and to a persistent local log file named **`app.log`**.
*   **💾 Self-Healing JSON Database**: Fully file-based JSON storage (`client.json` and `message.json`) equipped with list-deduplication logic to prevent data corruption.

---

## 📁 Project Structure

```bash
websoket/
├── main.py          # FastAPI application server & WebSocket endpoints
├── schemas.py       # JSON database read/write queries & connection helpers
├── model.py         # Pydantic/Dataclass schemas for Users & Messages
├── home.html        # Premium glassmorphic responsive client interface
├── client.py        # Terminal WebSocket client script for testing
├── client.json      # Registered users database
├── message.json     # Private chat history & session records
├── app.log          # System logs output (runtime logs)
└── venv/            # Python Virtual Environment
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have **Python 3.12+** installed on your system.

### 2. Set Up the Virtual Environment
Activate your virtual environment and install the required libraries:

```powershell
# Activate the venv (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install FastAPI, Uvicorn, and Websockets
pip install fastapi uvicorn websockets
```

### 3. Run the FastAPI Server
Start your local development server using `uvicorn`:

```powershell
uvicorn main:app --reload
```

The server will boot on `http://127.0.0.1:8000/`.

---

## 💻 Developer & Linter Best Practices

### Editor Import Warnings
If your editor/IDE (like VS Code or PyCharm) complains about `Cannot find module 'fastapi'` or `Cannot find module 'websockets'`, ensure you have selected your **virtual environment's Python interpreter**:

1.  Open the Command Palette (`Ctrl + Shift + P`).
2.  Search for **`Python: Select Interpreter`**.
3.  Choose the interpreter path inside your project's venv:
    `.\venv\Scripts\python.exe`
