import Twilio_Setup


def send_message(message_text):
    Twilio_Setup.identify_conversation().messages.create(body=message_text)


def get_new_message():
    conversation = Twilio_Setup.identify_conversation().messages.list()
    new_message_indicator = len(conversation)
    while len(conversation) <= new_message_indicator:
        conversation = Twilio_Setup.identify_conversation().messages.list()
    return conversation[-1]


def main():
    view_history = input("Do you want to read the Message history - (y/n)? ")
    if view_history == "y":
        conversation = Twilio_Setup.identify_conversation().messages.list()
        for message in conversation:
            print(f"{message.author} send the message - {message.body}")
    print()
    print("Waiting for new Message")
    while True:
        new_message = get_new_message()
        print(f"\nNew message from {new_message.author}  : {new_message.body}")
        reply = input("Do you want to answer directly - (y/n)? ")
        if reply == "y":
            answer = input("Type the answer: ")
            send_message(answer)



if __name__ == "__main__":
    main()




