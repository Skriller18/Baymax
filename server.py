import socket
import pyaudio
import wave
import whisper
from transformers import pipeline
from gtts import gTTS
from pydub import AudioSegment

# Load the Whisper model for speech-to-text
stt_model = whisper.load_model("small")

# Load the BART model for zero-shot classification
nlp = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def load_instructions(file_path):
    instructions = {}
    with open(file_path, 'r') as file:
        for line in file:
            if ':' in line:
                key, value = line.strip().split(":", 1)
                instructions[key.strip()] = value.strip()
    return instructions

def process_input(user_input, instructions):
    labels = list(instructions.keys())
    result = nlp(user_input, labels)
    best_label = result['labels'][0]
    return instructions.get(best_label, "I'm sorry, I didn't understand that.")

def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang='en')
    tts.save(output_file)

def handle_client(conn, addr, instructions):
    print(f"Connected to {addr}")
    
    # Receive the audio file from the client
    with open('recording.wav', 'wb') as f:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            f.write(data)
    
    print("Received recording from client.")
    
    # Transcribe the audio
    result = stt_model.transcribe("recording.wav")
    user_input_text = result['text']
    print(f"Transcribed Text: {user_input_text}")
    
    # Process the text
    response_text = process_input(user_input_text, instructions)
    
    # Convert text to speech
    output_audio_file = "response_output.wav"
    text_to_speech(response_text, output_audio_file)
    
    # Send the processed audio back to the client
    with open(output_audio_file, 'rb') as f:
        while chunk := f.read(1024):
            conn.sendall(chunk)
    
    print("Sent processed audio back to client.")
    conn.close()

def start_server(server_ip, server_port, instructions):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((server_ip, server_port))
        s.listen(1)
        print(f"Server listening on {server_ip}:{server_port}")
        
        while True:
            conn, addr = s.accept()
            handle_client(conn, addr, instructions)

instructions = load_instructions('instructions.txt')

server_ip = '0.0.0.0'  # Bind to all available interfaces
server_port = 12345

# Start the server
start_server(server_ip, server_port, instructions)
