import Twilio_Setup


def send_message(message_text):
    """Takes the conversation and sends a new Message"""
    Twilio_Setup.identify_conversation().messages.create(body=message_text)


def get_new_message():
    """While loop, to check if there are new messages, if so - return the whole message object"""
    conversation = Twilio_Setup.identify_conversation().messages.list()
    new_message_indicator = len(conversation)
    while len(conversation) <= new_message_indicator:
        conversation = Twilio_Setup.identify_conversation().messages.list()
    return conversation[-1]


def main():
    #DENNIS.generate_greeting_response()
    view_history = input("Do you want to read the Message history - (y/n)? ")
    if view_history == "y":
        conversation = Twilio_Setup.identify_conversation().messages.list()
        for message in conversation:
            print(f"{message.author} send the message - {message.body}")
    print()
    send_message("Lets Make a Plan together!")
    #vacation_data_dict = DENNIS.ask_user_questions()
    send_message("We will process your answer and provide you with the best Holiday Package in the next Step")



if __name__ == "__main__":
    main()




