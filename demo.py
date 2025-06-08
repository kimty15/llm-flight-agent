from gtts import gTTS
import os

def create_test_audio():
    # Text to convert
    text = "Hello, I'm Lucy. Good bye"
    
    # Create gTTS object
    tts = gTTS(text=text, lang='en', slow=False)
    
    # Save as WAV file
    tts.save("test_audio.wav")
    
    print("Audio file created: test_audio.wav")

if __name__ == "__main__":
    create_test_audio()