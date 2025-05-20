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
    client = init_twilio_client()
    for conv in client.conversations.list():
        participants = conv.participants.list()
        for part in participants:
            if part.messaging_binding and part.messaging_binding["address"] == "whatsapp:+4915128847093":
                return conv
    return None


def binding_number_to_conversation(new_number):
    address = f"whatsapp:{new_number}"
    ms_address = f"whatsapp:{os.getenv('MS_WHATSAPP_NUMBER')}"
    identify_conversation().participants.create(messaging_binding_address=address, messaging_binding_proxy_address=ms_address)


def send_message(message_text):
    identify_conversation().messages.create(body=message_text)


def get_new_message():
    conversation = identify_conversation().messages.list()
    new_message_indicator = len(conversation)
    while len(conversation) <= new_message_indicator:
        conversation = identify_conversation().messages.list()
    return conversation[-1]


def main():
    old_messages = input("Do you want to read the Message history - (y/n)? ")
    if old_messages == "y":
        conversation = identify_conversation().messages.list()
        for message in conversation:
            print(f"{message.author} send the message - {message.body}")
    print()
    print("Waiting for new Message")
    while True:
        new_message = get_new_message()
        print(f"\nNew message from {new_message.author}  : {new_message.body}")




if __name__ == "__main__":
    main()



"""Maybe helpfull"""
#client.conversations("CH3dc3427ca1b247f3860d3a94f69e4d65").delete()