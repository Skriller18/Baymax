# Baymax

This repository contains a server and client implementation for processing audio files. The server receives audio files from the client, transcribes the audio to text, processes the text using a zero-shot classification model, converts the processed text back to speech, and sends the audio response back to the client which can be useful as a medical assistant. The name of the service is called Baymax, inspired from the movie Big Hero 6


## Prerequisites

- Python 3.10 or higher
- `pip` (Python package installer)

## Installation

1. Clone the repository:

```sh
git clone https://github.com/Skriller18/Baymax.git
```
2. Install the required packages:
```bash
pip install -r requirements.txt
```
3. Install the required models and packages for the zero-shot classification model and the speech synthesis model:

## Running the Server

1. Navigate to the root directory of the repository.
2. Start the server:
```bash
python server.py
```

## Running the client

1. Start the client to record your audio/query that you would like to ask Baymax
```bash
python client.py
```
The client will record audio, send it to the server, receive the processed audio, and play it.

## Configuration
1. The server reads instructions from instructions.txt.
2. The client and server IP and port can be configured in client.py and server.py.

