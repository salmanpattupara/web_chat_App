import logging
from model import Message_Data,Message
from fileinput import filename
from model import User
import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict


def extract_name(msg,data="from"):
    if msg['type']=='setname':
        name=msg[data]
        return name
    elif msg['type']=='message':
        name=msg[data]
        return name
    else:
        return None
def is_user_exist(name):
    if os.path.exists("client.json"):
        try:
            with open("client.json", "r") as fp:
                users = json.load(fp)
                if isinstance(users, list):
                    for user in users:
                        if isinstance(user, dict) and user.get("username") == name:
                            return True
        except:
            pass
    return False
    
def save(client:User):
    user = client
    # Check if file exists
    if os.path.exists("client.json"):
        try:
            with open("client.json", "r") as fp:
                users = json.load(fp)
                if not isinstance(users, list):
                    users = []
        except:
            users = []
    else:
        users = []
        
    # Remove any existing duplicates for this username to heal the database!
    users = [u for u in users if isinstance(u, dict) and u.get("username") != user.username]
    
    # Append the fresh single user record
    users.append(asdict(user))

    with open("client.json", "w") as f:
        json.dump(users, f, indent=4)

    return True

def update_onlinestatus(username, online=False):
    if os.path.exists("client.json"):
        try:
            with open("client.json", "r") as fp:
                users = json.load(fp)
            
            updated = False
            if isinstance(users, list):
                # Update status of ALL matching items in the list (healing any duplicates)
                for u in users:
                    if isinstance(u, dict) and u.get("username") == username:
                        if "userdata" not in u or not isinstance(u["userdata"], dict):
                            u["userdata"] = {}
                        u["userdata"]["status"] = "online" if online else "offline"
                        u["userdata"]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        updated = True
            elif isinstance(users, dict) and username in users:
                if "userdata" in users[username]:
                    users[username]["userdata"]["status"] = "online" if online else "offline"
                    users[username]["userdata"]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
            if updated:
                with open("client.json", "w") as fp:
                    json.dump(users, fp, indent=4)
                return True
        except Exception as e:
            logging.ERROR("erro updating status {e}")
            
    return False


def load_users():
    if os.path.exists("client.json"):
        try:
            with open("client.json", "r") as fp:
                users = json.load(fp)
                return users
        except:
            pass
    return []


def check_client_exist(name:str,client:dict)->str:
    if name in client:
        return client[name]
    else:
        return None

def save_message(msg:Message):
    try:
        with open("message.json","r") as fp:
            messages=json.load(fp)
            if not isinstance(messages, list):
                messages = []
    except:
        messages=[]
    for message in messages:
        if isinstance(message, dict) and message.get('from_') == msg.from_ and message.get('to') == msg.to:
            if 'history' not in message or not isinstance(message['history'], list):
                message['history'] = []
            
            # Serialize the new history item
            history_item = asdict(msg.history) if hasattr(msg.history, '__dataclass_fields__') else msg.history
            
            # Append history_item cleanly
            if isinstance(history_item, list):
                message['history'].extend(history_item)
            else:
                message['history'].append(history_item)
                
            with open("message.json", "w") as f:
                json.dump(messages, f, indent=4)
            return True
            
    # If the session doesn't exist, create a new one with history as a list of dicts
    history_item = asdict(msg.history) if hasattr(msg.history, '__dataclass_fields__') else msg.history
    history_list = history_item if isinstance(history_item, list) else [history_item]
    new_session = {
        "type": msg.type,
        "from_": msg.from_,
        "to": msg.to,
        "history": history_list
    }
    messages.append(new_session)
    with open("message.json", "w") as f:
        json.dump(messages, f, indent=4)
    return True
     
 
def load_messages(sender:str,reciever:str)->dict:
    try:
        with open("message.json","r") as fp:
            messages=json.load(fp)
            
            # Support the new list of sessions format
            if isinstance(messages, list):
                for session in messages:
                    if isinstance(session, dict):
                        if session.get('from_') == sender and session.get('to') == reciever:
                            return {
                                'type': 'messages',
                                'sender': sender,
                                'reciever': reciever,
                                'messages': session.get('history', [])
                            }
                return {
                    'type': 'messages',
                    'sender': sender,
                    'reciever': reciever,
                    'messages': []
                }
            
            # Support the old dictionary format
            elif isinstance(messages, dict):
                if sender in messages:
                    if reciever in messages[sender]:
                        return {
                            'type':'messages',
                            'sender':sender,
                            'reciever':reciever,
                            'messages':messages[sender][reciever]
                        }
        return {
            'type': 'messages',
            'sender': sender,
            'reciever': reciever,
            'messages': []
        }
    except:
        return {
            'type': 'messages',
            'sender': sender,
            'reciever': reciever,
            'messages': []
        }

def get_undelivered_messages(receiver: str) -> list[dict]:
    undelivered = []
    try:
        if os.path.exists("message.json"):
            with open("message.json", "r") as fp:
                messages = json.load(fp)
                if not isinstance(messages, list):
                    messages = []
        else:
            messages = []
            
        for session in messages:
            if isinstance(session, dict) and session.get('to') == receiver:
                history = session.get('history', [])
                if isinstance(history, list):
                    for msg in history:
                        if isinstance(msg, dict) and not msg.get('delivered', False):
                            undelivered.append({
                                "session_from": session.get('from_'),
                                "session_to": receiver,
                                "message": msg.get('message'),
                                "timestamp": msg.get('timestamp')
                            })
    except Exception as e:
        print(f"Error getting undelivered messages: {e}")
    return undelivered

def mark_single_message_delivered(sender: str, receiver: str, timestamp: str) -> bool:
    try:
        if os.path.exists("message.json"):
            with open("message.json", "r") as fp:
                messages = json.load(fp)
                if not isinstance(messages, list):
                    messages = []
        else:
            messages = []
            
        updated = False
        for session in messages:
            if isinstance(session, dict) and session.get('from_') == sender and session.get('to') == receiver:
                history = session.get('history', [])
                if isinstance(history, list):
                    for msg in history:
                        if isinstance(msg, dict) and msg.get('timestamp') == timestamp:
                            if not msg.get('delivered', False):
                                msg['delivered'] = True
                                updated = True
                            break
                            
        if updated:
            with open("message.json", "w") as fp:
                json.dump(messages, fp, indent=4)
            return True
    except Exception as e:
        print(f"Error marking single message delivered: {e}")
    return False