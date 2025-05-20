import os
import json
from dotenv import load_dotenv
from twilio.rest import Client

def init_twilio_client():
    """Getting the Twilio service client running for usw getting the ISaaaaaaaaa ID"""
    load_dotenv()
    account_sid = os.getenv("MS_TWILIO_ACCOUNT_SID")
    api_sid = os.getenv("MS_TWILIO_API_KEY_SID")
    api_secret = os.getenv("MS_TWILIO_SECRET")
    chat_service_sid = os.getenv("MS_TWILIO_CHAT_SERVICE_SID")
    client = Client(api_sid, api_secret, account_sid)
    return client.conversations.v1.services(chat_service_sid)


def identify_conversation():
    """loops through all conversations and returns the conversation with your Phone number"""
    client = init_twilio_client()
    for conv in client.conversations.list():
        participants = conv.participants.list()
        for part in participants:
            if part.messaging_binding and part.messaging_binding["address"] == f"whatsapp:{os.getenv("PHONE_NUMBER")}":
                return conv
    return None


def binding_number_to_conversation(new_number):
    address = f"whatsapp:{new_number}"
    ms_address = f"whatsapp:{os.getenv('MS_WHATSAPP_NUMBER')}"
    identify_conversation().participants.create(messaging_binding_address=address, messaging_binding_proxy_address=ms_address)


def delete_conversation(conversationSID):
    client = init_twilio_client()
    client.conversations(conversationSID).delete()
    print("Conversation deleted")