import json
from dotenv import load_dotenv
import os
import requests
import time
import requests
from urllib.parse import urljoin

# Load environment variables
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
RECIPIENT_WAID = os.getenv("RECIPIENT_WAID")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERSION = os.getenv("VERSION")

# Send a template WhatsApp message
def send_whatsapp_message(recipient, template_name):
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "template",
        "template": {"name": template_name, "language": {"code": "en_US"}},
    }
    response = requests.post(url, headers=headers, json=data)
    return response

# Function to send a text message
def send_text_message(recipient, text):
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    }
    response = requests.post(url, headers=headers, json=data)
    return response


# Function to send a text message
def send_image_message(recipient, image_path):
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json",
    }

    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    # Use multipart/form-data encoding for image upload
    data = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "image",
        "image": (
            "image.jpeg",  # Filename for the API
            image_data,
            "image/jpeg"  # Adjust for other image types
        )
    }
    response = requests.post(url, headers=headers, files=data)
    return response

# # Function to check replies of recipient
# def check_replies():
#     replies = []
#     while True:
#         # Check for new messages specifically from the recipient
#         messages = check_new_messages()
#         for message in messages:
#             sender = message.get("sender")
#             if sender == RECIPIENT_WAID:  # Only process messages from the recipient
#                 text = message.get("text")
#                 replies.append(text)
#                 break  # Exit loop after finding a reply

#         if replies:
#             return replies  # Return replies if any were found

#         # Wait briefly before checking again
#         time.sleep(1)  # Adjust the delay as needed


# Main function to handle conversation
def main():
    while True:
        try:
            # messages = check_new_messages()
            # print_chat_messages(messages)

            # User input handling
            user_input = input("Enter your message : ")
            if user_input.lower() == 'q':
                break  # Exit the program if user enters 'q'

            # Send text message or image based on user input
            if user_input.startswith("image "):
                image_path = user_input.split()[1]  # Extract image path
                # Validate image format (optional)
                send_image_message(RECIPIENT_WAID, image_path)
            else:
                send_text_message(RECIPIENT_WAID, user_input)

            # # Check for replies after sending a message
            # replies = check_replies()
            # if replies:
            #     for reply in replies:
            #         # Handle text or image replies (optional)
            #         if reply.startswith("image "):
            #             # Implement logic to download and process the image
            #             image_url = "..."  # Extract image URL (replace with actual logic)
            #             print(f"Received image from recipient: {image_url}")
            #         else:
            #             print("Recipient (Reply):", reply)

        except Exception as e:  # Handle potential errors gracefully
            print(f"An error occurred: {e}")

        # Add a short delay before checking for new messages again
        time.sleep(1)


# # Function to check for new messages
# def check_new_messages():


#     print('hi call me ')
#     url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
#     headers = {"Authorization": "Bearer " + ACCESS_TOKEN}
#     params = {"recipient": RECIPIENT_WAID}  # Include recipient WAID for filtering
#     response = requests.get(url, headers=headers, params=params)
#     # messages = response.json().get("data", [])
#     print(url)
#     print(response.text)


    # headers = {
    #     "Authorization": "Bearer " + ACCESS_TOKEN,
    #     "Content-Type": "application/json"
    # }
    # data = {
    #     "messaging_product": "whatsapp",
    #     "to": RECIPIENT_WAID,
    #     "text": {"body": "Echo: arshad"},
    #     "context": {
    #         "message_id": 'wamid.HBgMOTIzMzUzNjk0MTUyFQIAEhggQzA5RTBGNzQ5RDUxMzAyQTM0RUY0ODBFMDg3N0FCMzMA'
    #     }
    # }

    # response = requests.post(url, headers=headers, json=data)
    # print(response.text)


    # # Filter out messages sent by the test number (echo messages)
    # messages = [message for message in messages if message.get("sender") != RECIPIENT_WAID]

    # # Add message origin (optional)
    # for message in messages:
    #     sender = message.get("sender")
    #     if sender == RECIPIENT_WAID:
    #         message["origin"] = "user"  # Flag for user origin
    #     else:
    #         message["origin"] = "bot"  # Flag for bot origin

    #     if message.get("type") == "image":
    #         image_url = message.get("image").get("link")  # Get the image URL
    #         image_content = requests.get(image_url).content  # Download the image
    #         # Do something with the image content, e.g., save it to a file

    # return messages


# # Function to print chat messages of the bot and the user
# def print_chat_messages(messages):
#     for message in messages:
#         sender = message.get("sender")
#         text = message.get("text")
#         origin = message.get("origin")
#         if origin == "user":
#             print(f"User: {text}")  # Print user's message
#         elif origin == "bot":
#             print(f"Bot: {text}")  # Print bot's message



