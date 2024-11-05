import socket
import pyaudio
import wave
import os

def record_audio(filename, duration=5, fs=44100):
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

def send_audio(filename, server_ip, server_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, server_port))
        with open(filename, 'rb') as f:
            s.sendall(f.read())
        print("Audio file sent.")

def receive_audio(filename, server_ip, server_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((server_ip, server_port))
        s.listen(1)
        conn, addr = s.accept()
        with conn:
            with open(filename, 'wb') as f:
                data = conn.recv(1024)
                while data:
                    f.write(data)
                    #data = conn.recv(1024)
        print("Processed audio received.")

def play_audio(filename):
    os.system(f"mpg321 {filename}")  # Using mpg321 to play the audio

server_ip = '192.168.1.15'
server_port = 12345

# Record audio and send to server
record_audio('recording.wav')
send_audio('recording.wav', server_ip, server_port)

# Standby to receive the processed audio
receive_audio('response_output.mp3', server_ip, server_port + 1)
play_audio('response_output.mp3')
