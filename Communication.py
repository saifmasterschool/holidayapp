import Twilio_Setup
import user_input


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
    get_new_message()
    send_message(user_input.generate_greeting_response())
    send_message("Lets Make a Plan together!\nThe next available Agent will get in touch with you!\n")
    vacation_data_dict = user_input.ask_user_questions()
    print(vacation_data_dict)
    send_message("We will process your answer and provide you with the best Holiday Package in the next Step")



if __name__ == "__main__":
    main()




