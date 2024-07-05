from deepgram import DeepgramClient, PrerecordedOptions, FileSource

DEEPGRAM_KEY="cff48a48449a561982d3a5de23938ea499f57f52"

def speech_to_text(save_path):
    try:
        deepgram = DeepgramClient(DEEPGRAM_KEY)
        with open(save_path, "rb") as file:
            buffer_data = file.read()
        payload: FileSource = {
            "buffer": buffer_data,
        }
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
        )
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
        print(transcript)
        return transcript
    
    except Exception as e:
        print(f"Exception: {e}")