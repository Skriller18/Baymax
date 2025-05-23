import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import pygame
from io import BytesIO
import speech_recognition as sr

# Initialize pygame mixer
pygame.mixer.init()

# Initialize session state variables
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key_valid" not in st.session_state:
    st.session_state.api_key_valid = None # Can be True, False, or None (unknown)
if "current_api_key" not in st.session_state:
    st.session_state.current_api_key = None

# Set page title and subheader
st.title("Gemini Voice Assistant")
st.subheader("Interact with Gemini using voice or text")

# --- Sidebar ---
st.sidebar.header("Configuration")
api_key_input = st.sidebar.text_input("Enter your Gemini API Key:", type="password", key="api_key_widget")
tts_enabled = st.sidebar.toggle("Enable Voice Output", value=True)

st.sidebar.header("Actions")
if st.sidebar.button("Clear Chat History", key="clear_chat"):
    st.session_state.messages = []
    st.session_state.transcribed_text = None # Also clear any pending transcribed text
    st.rerun()

# API Key Configuration
gemini_model = None
if api_key_input:
    if st.session_state.current_api_key != api_key_input: # Key has changed
        st.session_state.current_api_key = api_key_input
        st.session_state.api_key_valid = None # Reset validity on new key

    if st.session_state.api_key_valid is None: # Only try to configure if unknown or changed
        try:
            genai.configure(api_key=st.session_state.current_api_key)
            gemini_model = genai.GenerativeModel('gemini-pro')
            # Try a dummy call to validate the key (optional, but good for immediate feedback)
            # gemini_model.generate_content("test") 
            st.session_state.api_key_valid = True
            st.sidebar.success("API Key configured successfully!")
        except Exception as e:
            st.session_state.api_key_valid = False
            st.sidebar.error(f"API Key Configuration Failed: {e}. Please check your key.")
    elif st.session_state.api_key_valid is True:
         # Key is valid and already configured
        genai.configure(api_key=st.session_state.current_api_key) # Ensure it's set for the session
        gemini_model = genai.GenerativeModel('gemini-pro')
    else: # api_key_valid is False
        st.sidebar.error("API Key is invalid. Please enter a valid key.")
elif not api_key_input and st.session_state.api_key_valid is not False : # only show warning if key is not typed and not already marked as invalid
    st.sidebar.warning("Please enter your Gemini API Key to use the app.")


# --- Main App Area ---

# Text-to-Speech function
def text_to_speech_and_play(text):
    if not text:
        return
    try:
        tts = gTTS(text=text, lang='en')
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        pygame.mixer.music.load(mp3_fp, "mp3")
        pygame.mixer.music.play()
    except Exception as e:
        st.error(f"Error in TTS: {e}")

# Display conversation history
chat_container = st.container() # Using a container for better scrolling/layout control
with chat_container:
    for message in st.session_state.messages:
        st.chat_message(message["role"]).markdown(message["content"])

# Input area: Text and Speak button
input_col1, input_col2 = st.columns([4, 1])

with input_col1:
    user_input_text = st.chat_input("Type your message here...", key="chat_input_main")

with input_col2:
    speak_button = st.button("🎤 Speak", use_container_width=True, key="speak_button")

user_input = user_input_text # Default to text input

if speak_button:
    if not st.session_state.api_key_valid:
        st.error("Please enter and validate your API key before using voice input.")
    else:
        r = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                st.info("Listening... (Say something!)")
                try:
                    audio = r.listen(source)
                    with st.spinner("Transcribing..."):
                        text = r.recognize_google(audio)
                    st.session_state.transcribed_text = text # Store transcribed text
                    st.rerun() # Rerun to process the transcribed text
                except sr.UnknownValueError:
                    st.error("Sorry, I could not understand the audio.")
                    st.session_state.transcribed_text = None
                except sr.RequestError as e:
                    st.error(f"STT Service Error: {e}")
                    st.session_state.transcribed_text = None
                except Exception as e: # Catch other potential STT errors
                    st.error(f"An unexpected error occurred during speech recognition: {e}")
                    st.session_state.transcribed_text = None
        except sr.WaitTimeoutError:
            st.error("No speech detected. Microphone timed out.")
        except OSError as e:
             st.error(f"Microphone Error: {e}. Ensure a microphone is connected and access is allowed.")
        except Exception as e: # Catch other potential microphone errors
            st.error(f"Error initializing microphone: {e}. Please check your microphone setup and permissions.")
            st.session_state.transcribed_text = None


# Check if there's transcribed text from a previous run (after st.rerun)
if st.session_state.get("transcribed_text"): # Use .get for safety
    user_input = st.session_state.transcribed_text 
    st.session_state.transcribed_text = None # Clear it

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with chat_container:
        st.chat_message("user").markdown(user_input)

    if not st.session_state.api_key_valid: # Check key validity before calling Gemini
        bot_response = "Error: API Key is invalid or not configured. Please check the sidebar."
    elif not gemini_model: # Should be caught by api_key_valid, but as a fallback
        bot_response = "Error: Gemini model not available. Please ensure your API key is correctly entered."
    else:
        try:
            with st.spinner("Gemini is thinking..."):
                response = gemini_model.generate_content(user_input)
                bot_response = response.text
        except Exception as e:
            # More specific error handling for Gemini can be added here if a more specific exception type is known for auth
            st.session_state.api_key_valid = False # Assume key is bad if call fails
            bot_response = f"Error from Gemini: {e}. Your API key might be invalid or quota exceeded. Please check and re-enter."
            st.sidebar.error("Gemini API call failed. Please verify your API key.")


    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    with chat_container:
        st.chat_message("assistant").markdown(bot_response)
    
    if tts_enabled and bot_response and not bot_response.startswith("Error") and not "API Key" in bot_response :
        text_to_speech_and_play(bot_response)
else:
    # Initial placeholder messages in the chat area
    if not st.session_state.get("messages"): # Only show if chat is empty
        if not st.session_state.current_api_key:
            st.info("👋 Welcome! To get started, please enter your Gemini API Key in the sidebar. \n\nThen, you can type your message or click the '🎤 Speak' button.")
        elif not st.session_state.api_key_valid:
            st.warning("⚠️ Your Gemini API Key is invalid or failed to configure. Please correct it in the sidebar. Chat functionality is disabled.")
        # If API key is valid and no messages yet, no placeholder needed, user can start.
