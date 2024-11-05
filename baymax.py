import whisper
from transformers import pipeline
from gtts import gTTS
import os
import numpy as np
import pyaudio
import wave
from pydub import AudioSegment
from pydub.playback import play

#Loading the whisper model
stt_model = whisper.load_model("small")

#Loading the bart model which is our LLM
nlp = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

#Loading the Instructions for the receptionist
def load_instructions(file_path):
    instructions = {}
    with open(file_path, 'r') as file:
        for line in file:
            if ':' in line:
                key, value = line.strip().split(":", 1)
                instructions[key.strip()] = value.strip()
    return instructions

#Processing instructions on the LLM
def process_input(user_input, instructions):
    labels = list(instructions.keys())
    result = nlp(user_input, labels)
    best_label = result['labels'][0]
    return instructions.get(best_label, "I'm sorry, I didn't understand that.")

#Loading our Text-to-Speech model,i.e, gTTS
def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang='en')
    tts.save(output_file)

#Recording the audio
def record_audio(filename, duration=10, fs=44100):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=fs, input=True, frames_per_buffer=1024)
    frames = []

    print("Recording...")
    for _ in range(0, int(fs / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)
    print("Recording finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

instructions = load_instructions('instructions.txt')
print("Recoring starting now....")
record_audio("recording.wav")
result = stt_model.transcribe("recording.wav")
user_input_text = result['text']
print(user_input_text)
response_text = process_input(user_input_text, instructions)
#Output audio file
output_audio_file = "response_output.mp3"
text_to_speech(response_text, output_audio_file)
# Load the audio file
audio = AudioSegment.from_file("response_output.mp3")
# Play the audio file
play(audio)