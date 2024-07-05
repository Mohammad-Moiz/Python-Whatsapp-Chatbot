from deepgram import DeepgramClient, PrerecordedOptions, FileSource

DEEPGRAM_KEY="cff48a48449a561982d3a5de23938ea499f57f52"
audio_file = "/home/muhammadmoizkhan/Downloads/Moiz_English.ogg"

def speech_to_text(audio_file):
    try:
        deepgram = DeepgramClient(DEEPGRAM_KEY)
        with open(audio_file, "rb") as file:
            buffer_data = file.read()
        payload: FileSource = {
            "buffer": buffer_data,
        }
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
        )
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        print(response)
        transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
        print(transcript)
        return transcript
    
    except Exception as e:
        print(f"Exception: {e}")


if __name__ == "__main__":
    speech_to_text(audio_file)