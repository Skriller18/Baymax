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

---

## Gemini Voice Assistant Streamlit App

This application allows you to interact with Google's Gemini model using either text or voice input. It features voice output for Gemini's responses and maintains a conversation history.

### Prerequisites

*   Python 3.7+
*   `pip` (Python package installer)
*   A connected microphone (for voice input)
*   Speakers or headphones (for voice output)

### Setup

1.  **Clone the repository (if you haven't already):**
    ```sh
    git clone https://github.com/Skriller18/Baymax.git
    cd Baymax 
    ```
    (If you've already cloned for Baymax, just navigate to the repository directory.)

2.  **Create and activate a virtual environment (recommended):**
    *   On Linux/macOS:
        ```sh
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   On Windows:
        ```sh
        python -m venv venv
        venv\Scripts\activate
        ```

3.  **Install dependencies:**
    Ensure your `requirements.txt` file includes `streamlit`, `google-generativeai`, `gTTS`, `pygame`, and `SpeechRecognition`. Then run:
    ```sh
    pip install -r requirements.txt
    ```
    You might need to install system libraries for PyAudio (used by SpeechRecognition) or PortAudio (used by Pygame) if you encounter issues:
    *   On Debian/Ubuntu: `sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg`
    *   On macOS: `brew install portaudio libsndfile ffmpeg` (libsndfile for some audio formats if needed)
    *   On Windows: PyAudio and Pygame wheels usually bundle necessary components, but ensure your microphone is correctly configured in system settings.

### Running the App

1.  **Run the Streamlit application:**
    ```sh
    streamlit run gemini_streamlit_app.py
    ```

2.  **Enter your API Key:**
    Once the app opens in your browser, locate the sidebar. You will need to enter your Google Gemini API key in the designated text input field to enable communication with the Gemini model. You can obtain an API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### Features

*   **Text and Voice Interaction:** Communicate with Gemini using typed text or spoken voice.
*   **Voice Input:** Click the "🎤 Speak" button to provide your queries via microphone.
*   **Voice Output:** Hear Gemini's responses spoken back to you. This can be toggled on/off in the sidebar.
*   **Conversation History:** View the history of your interaction with Gemini.
*   **Clear Chat:** A button in the sidebar allows you to clear the current conversation history.
*   **API Key Management:** Securely enter your API key in the sidebar. The app provides feedback on key validity.
