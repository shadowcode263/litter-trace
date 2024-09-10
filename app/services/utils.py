from functools import wraps
import json
import requests
from decouple import config
import datetime
import uuid

def is_valid_uuid(value):
    try:
        uuid_obj = uuid.UUID(value, version=4)
    except ValueError:
        return False
    return str(uuid_obj) == value

def convert_timestamp_to_date(timestamp_ms):
    """
    Convert a timestamp in milliseconds to a formatted date string.
    
    Args:
    timestamp_ms (int): The timestamp in milliseconds.

    Returns:
    str: The formatted date string in 'YYYY-MM-DD HH:MM:SS' format.
    """
    # Convert milliseconds to seconds
    timestamp_s = timestamp_ms / 1000

    # Convert to datetime
    date = datetime.datetime.fromtimestamp(timestamp_s)

    # Format the date
    formatted_date = date.strftime('%Y-%m-%d')
    
    return formatted_date


def add_method(cls):
    def decorator(func):
        @wraps(func) 
        def wrapper(self, *args, **kwargs): 
            return func(*args, **kwargs)
        setattr(cls, func.__name__, wrapper)
        # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
        return func # returning func means func can still be used normally
    return decorator

class LitterTraceWhatsappService:
    """Whatsapp client"""

    def __init__(self, payload: dict, message="hi", phone_number_id=config('WHATSAPP_PHONE_NUMBER_ID')):
        self.url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
        self.headers = {
            'Content-Type': "application/json",
            'Authorization': f"Bearer {config('WHATSAPP_ACCESS_TOKEN')}"
        }
        self.payload = payload
        self.message = message  

    def send_message(self):
        """Send message"""
        try:
            # print("BOT.REQ ", self.payload)
            response = requests.post(
                url=self.url,
                headers=self.headers,
                data=json.dumps(self.payload)
            )
            data = response.json()
            # print('MegaMarket', " REPLIED TO ", self.payload.get('to'))
            print("BOT.RESP ", data)
                
        except Exception as e:
            print("ERROR SENDING MESSAGE TO WHATSAPP", e)
            return {"status": "error", "message": str(e)}

    def notify(self):
        """Send message"""
        try:
            resp = requests.post(
                url=self.url,
                headers=self.headers,
                json=self.payload
            )
            print("RESPONSE : ", resp.content)
            return {"status": "Successful", "message": "Sent"}
        except Exception as e:
            # print("ERROR SENDING MESSAGE TO WHATSAPP", e)
            return {"status": "Error", "message": str(e)}

    