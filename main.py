# pyrefly: ignore [missing-import]
from schemas import save_message
from schemas import save
from typing import List
from model import User_Data
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import json
from schemas import *
from model import User,Message,Message_Data
import logging



def set_logger():
    # Console handler to output logs in the terminal
    console_handler = logging.StreamHandler()
    
    # File handler to save logs to app.log
    file_handler = logging.FileHandler("app.log", encoding="utf-8")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [%(levelname)s] - %(message)s',
        handlers=[console_handler, file_handler],
        force=True
    )



app = FastAPI()

ROOT_DIR = Path(__file__).resolve().parent
set_logger()



active_connection:dict={}
buffer_message={}

@app.get("/", response_class=HTMLResponse)
def home():
    html_path = ROOT_DIR / "home.html"
    logging.info("loading home")
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.websocket("/ws")
async def websoket_endpoint(websocket: WebSocket):
    await websocket.accept()
    recieved_data = await websocket.receive_text()
    web=websocket
    name_json=json.loads(recieved_data)
    name=extract_name(name_json,'from')
    exist=is_user_exist(name)
    logging.info(f"connected by {name}")
    active_connection[name] = websocket
    update_onlinestatus(username=name,online=True)
    if not exist:
        user=User(username=name,userdata=User_Data(status="online",last_seen=datetime.now().replace(microsecond=0).isoformat()))
        logging.info(f"{name} has saved as a new user")
        save(user)
   
    # Deliver pending messages for this newly online user atomically!
    pending = get_undelivered_messages(name)
    for p in pending:
        try:
            # 1. Send the message to the recipient over websocket
            await web.send_text(json.dumps({
                "type": "message",
                "from": p["session_from"],
                "to": p["session_to"],
                "message": p["message"],
                "timestamp": p["timestamp"]
            }))
            
            # 2. Mark this specific message as delivered in the database
            mark_single_message_delivered(sender=p["session_from"], receiver=p["session_to"], timestamp=p["timestamp"])
            
            # 3. If the sender is online, send them an 'ack' packet
            sender_name = p["session_from"]
            if sender_name in active_connection:
                await active_connection[sender_name].send_text(json.dumps({
                    "type": "ack",
                    "to": name,
                    "from": sender_name
                }))
        except Exception as e:
            logging.error(f"error delivering pending messages {e}")
            break # Connection died, stop delivering the rest!

    try:
        while True:
            data = await web.receive_text()
            resp=json.loads(data)
            to=extract_name(resp,'to')
            if to in active_connection:
                try:
                    await active_connection[to].send_text(json.dumps(resp))
                    message=Message_Data(message=resp['message'],timestamp=datetime.now().replace(microsecond=0).isoformat(),
                    delivered=True)
                    msg=Message(type='message',from_=name,to=to,history=message)
                    await web.send_text(json.dumps({'type':'ack','to':to,'from':name}))
                    save_message(msg)

                except Exception as e:
                    logging.error(f"error occured {e}")
                    await web.send_text(json.dumps({'type':'non-ack','to':to,'from':name}))
            else:
                message=Message_Data(message=resp['message'],timestamp=datetime.now().replace(microsecond=0).isoformat(),delivered=False)
                msg=Message(type='message',from_=name,to=to,history=message)
                save_message(msg)
                await web.send_text(json.dumps({'type':'non-ack','to':to,'from':name}))

    except:
        active_connection.pop(name)
        update_onlinestatus(username=name,online=False)
        logging.info(f"{name} disconnected")
        #update_status(name,status="offline",timestamp=datetime.now().replace(microsecond=0).isoformat())


@app.get("/alluser")
def get_all_user() -> dict:
    users = load_users()
    return {"users": users}

@app.get("/history")
def get_chat_history(sender: str, receiver: str):
    history1 = load_messages(sender, receiver)
    history2 = load_messages(receiver, sender)
    
    all_messages = []
    
    def extract_msgs(hist, role):
        msgs = []
        if isinstance(hist, dict) and 'messages' in hist:
            for m in hist['messages']:
                msgs.append({
                    "message": m.get("message", ""),
                    "timestamp": m.get("timestamp"),
                    "role": role,
                    "delivered": m.get("delivered", False)
                })
        return msgs

    all_messages.extend(extract_msgs(history1, "user"))
    all_messages.extend(extract_msgs(history2, "server"))
    
    # Sort messages chronologically by timestamp
    all_messages.sort(key=lambda x: x.get("timestamp", ""))
    
    return {"messages": all_messages}