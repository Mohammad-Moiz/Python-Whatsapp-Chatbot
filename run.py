import requests, datetime, os, tempfile
from pydantic import BaseModel
from typing import Optional
from PIL import Image
from io import BytesIO
# import speech_recognition as sr
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from fastapi import FastAPI, HTTPException, Request, Response
from voiceclone import speech_to_text

app = FastAPI()

WEBHOOK_VERIFY_TOKEN = "12345"
GRAPH_API_TOKEN = "EABpxzwZBj7ZCkBO8bj5HsnoEjLExD9SzfJZCI4lKYurDMIXSPx35C2LiIO9581jXshJyYZAYqkcnGlF3I8JPlBMUeUlZCkjZB6Fdpnz63sZAK4PAiIikJPZCsUs32bePxCRfFrASgdjFQSb2gIzIt8OaTE1tLGIYKUZB33kWCOIcvigf58cACHRXRqKueYmsPJSiymGNGihJr1kzZBozaoQjZBlNExAZABRzBcVU6IsZD"
PORT = 5000
RECIPIENT_WAID="+923353694152"
ACCESS_TOKEN="EABpxzwZBj7ZCkBO4FblMD7MpssPmT0a8SuZA7P1yNnsEgWm1ZBQZAOZCZCP4PMcvb8gP4Ad2vkEdwgZC8Tq2HTgZArjBRTyg9zSRuv3ZC83PpmGU7z5DYvsQGL2NcfSkVt7Pb7gOBMaXvEYZBRetyAzqedihUiCP380ccDJFI3MYuSuy9jI0xV9jq8l5F0OpEsVuaOcmQeQszrfmUqYpbOz9pwdsG6RqLAZD"
VERSION="v19.0"
PHONE_NUMBER_ID="284426971410101"
TEST_NUMBER_ID="+15550861731"

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

# Function to send a image message
def send_image_message(recipient, image_path):
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/media"
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN
    }
    params = {
    'messaging_product': 'whatsapp'
    }

    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        # print(type(image_data))

    files = {
        "file": (
            "image.jpeg",
            image_data,
            "image/jpeg"
        )
    }
    # print(f"files: {files}")
    response = requests.post(url, headers=headers, files=files, params=params)
    # print(response)

    if response.status_code == 200:
        # Parse the response to get the media ID
        response_json = response.json()
        media_id = response_json.get("id")
        print(media_id)

        if media_id:
            url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
            message_data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": RECIPIENT_WAID,
                "type": "image",
                "image": {"id": media_id},
                # "image": {"id": "270739389424306"}
            }
            headers = {
                "Authorization": "Bearer " + ACCESS_TOKEN,
                "Content-Type": "application/json",
            }
            message_response = requests.post(url=url, headers=headers, json=message_data)
            # print(message_response)

            if message_response.status_code == 200:
                print(f"Image sent successfully. Media ID: {media_id}")
                return media_id  # Return the media ID for potential tracking
            else:
                print(f"Error sending image message: {message_response.text}")
                return None 
        else:
            print(f"Error getting media ID from upload response: {response.text}")
            return None 
    else:
        print(f"Error uploading image: {response.text}")
        return None 

# Function to send a audio message
def send_audio_message(recipient, audio_path):
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/media"
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN
    }
    params = {
        'messaging_product': 'whatsapp'
    }

    with open(audio_path, "rb") as audio_file:
        audio_data = audio_file.read()

    files = {
        "file": (
            "audio.ogg",  # Assuming the audio format is ogg
            audio_data,
            "audio/ogg"
        )
    }

    response = requests.post(url, headers=headers, files=files, params=params)

    if response.status_code == 200:
        # Parse the response to get the media ID
        response_json = response.json()
        media_id = response_json.get("id")
        print(media_id)

        if media_id:
            url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
            message_data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": RECIPIENT_WAID,
                "type": "audio",
                "audio": {"id": media_id},
            }
            headers = {
                "Authorization": "Bearer " + ACCESS_TOKEN,
                "Content-Type": "application/json",
            }
            message_response = requests.post(url=url, headers=headers, json=message_data)

            if message_response.status_code == 200:
                print(f"Audio sent successfully. Media ID: {media_id}")
                return media_id  # Return the media ID for potential tracking
            else:
                print(f"Error sending audio message: {message_response.text}")
                return None
        else:
            print(f"Error getting media ID from upload response: {response.text}")
            return None
    else:
        print(f"Error uploading audio: {response.text}")
        return None


class WebhookPayload(BaseModel):
    object: str
    entry: list[dict]

conversation = []  
last_received_message = None

@app.post('/webhook')
async def webhook(payload: WebhookPayload, response: Response):
    global last_received_message
    message_data = payload.entry[0].get('changes', [{}])[0].get('value', {}).get('messages', [{}])[0]
    # print(message_data)
    phone_number = message_data.get('from')
    timestamp = message_data.get('timestamp')
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text = message_data.get('text')
    text_body = None  
    
    if text and 'body' in text:
        text_body = text.get('body')
        print(text_body)
        print(f"Recipient Phone Number: {phone_number}")
        print(f"Timestamp: {timestamp}")
        print(f"Time: {current_time}")
        print(f"text: {text}")

        user_input = input("Enter your message (text, 'image' to send image or 'audio' to send audio): ")
        if user_input.lower() == 'q':
            return {'status': 'Conversation ended'}

        if user_input.lower() == 'image':
            # Handle image sending
            image_path = input("Enter the path to the image file: ")
            try:
                media_id = send_image_message(RECIPIENT_WAID, image_path)
                if media_id:  
                    print(f"Image uploaded successfully. Media ID: {media_id}")
                    conversation.append({'from': 'User', 'text': f"Sent Image: {image_path}"})
            except Exception as e:
                print(f"Error sending image: {e}")
        
        if user_input.lower() == 'audio':
            # Handle audio sending
            audio_path = input("Enter the path to the audio file: ")
            try:
                media_id = send_audio_message(RECIPIENT_WAID, audio_path)
                if media_id:  
                    print(f"Audio uploaded successfully. Media ID: {media_id}")
                    conversation.append({'from': 'User', 'text': f"Sent Audio: {audio_path}"})
            except Exception as e:
                print(f"Error sending audio: {e}")

        else:
            send_text_message(RECIPIENT_WAID, user_input)
            conversation.append({'from': 'User', 'text': user_input})

    elif message_data.get('type') == 'image':
        print(f"Recipient Phone Number: {phone_number}")
        print(f"Timestamp: {timestamp}")
        print(f"Time: {current_time}")

        MEDIA_ID = message_data.get('image').get('id')
        print(MEDIA_ID)

        headers = {
            "Authorization": "Bearer " + ACCESS_TOKEN,
        }
        response = requests.get(f'https://graph.facebook.com/{VERSION}/{MEDIA_ID}', headers=headers)
        IMAGE_URL = response.json()['url']
        print(IMAGE_URL)
        print("An image message has been received from the recipient.")

        headers = {
            "Authorization": "Bearer " + ACCESS_TOKEN,
        }
        url_response = requests.get(f'{IMAGE_URL}', headers=headers)
        if url_response.status_code == 200:
            image = Image.open(BytesIO(url_response.content))
            image.save('output_image.jpg')  
            print("Image saved successfully as 'output_image.jpg'")
        else:
            print("Failed to download image. Status code:", response.status_code)
 
    elif message_data.get('type') == 'audio':
        print(f"Recipient Phone Number: {phone_number}")
        print(f"Timestamp: {timestamp}")
        print(f"Time: {current_time}")

        AUDIO_ID = message_data.get('audio').get('id')
        print(AUDIO_ID)
        print("An audio message has been received from the recipient.")

        # temp_dir = tempfile.mkdtemp(prefix="whatsapp_audio_")
        # audio_path = os.path.join(temp_dir, f"{AUDIO_ID}.ogg")
        headers = {
            "Authorization": "Bearer " + ACCESS_TOKEN,
        }
        response = requests.get(f'https://graph.facebook.com/{VERSION}/{AUDIO_ID}', headers=headers)
        if response.status_code == 200:
            audio = response.content
            save_path = f"received_audio_{AUDIO_ID}.ogg"
            with open(save_path, "wb") as audio_file:
                audio_file.write(audio)
                print(f"Audio downloaded and saved successfully to: {save_path}")
                text = speech_to_text(save_path)
                print("Transcribed Text:", text)
        else:
            print(f"Error downloading audio: {response.text}")
    
    # Return a success response after processing
    return {'status': 'success'}

    
@app.get('/webhook')
async def verify_webhook(request: Request, mode: Optional[str] = None, token: Optional[str] = None, challenge: Optional[str] = None):
    mode = request.query_params.get('hub.mode')
    token = request.query_params.get('hub.verify_token')
    challenge = request.query_params.get('hub.challenge')
    # Check the mode and token sent are correct
    if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
        # Respond with challenge token from the request
        print("Webhook verified successfully!")
        return Response(content=challenge, status_code=200)
    else:
        # Respond with '403 Forbidden' if verify tokens do not match
        raise HTTPException(status_code=403, detail="Verification failed")
    
@app.get('/')
async def home():
    return "<pre>Nothing to see here. Checkout README.md to start.</pre>"

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

