from datetime import datetime
from enum import auto
from dataclasses import field
from sqlite3.dbapi2 import Timestamp
from dataclasses import dataclass


@dataclass  
class User_Data:
    status: str
    last_seen: str

  

@dataclass
class User:
    username: str
    userdata:User_Data

    def update_status(self,status):
        self.userdata.status=status
        self.userdata.last_seen=datetime.now().replace(microsecond=0).isoformat()
        return True



@dataclass
class Message_Data:  
    message:str
    timestamp:str
    delivered:bool=False
    read:bool=False


    def  update_delivered_status(self):
        try:
            self.delivered=True
            return True
        except:
            return False
    


@dataclass
class Message:
    type:str
    from_: str
    to: str
    history:Message_Data=field(default_factory=list)


    