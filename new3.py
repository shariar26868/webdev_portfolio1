import openai
import pyttsx3
import speech_recognition as sr
import threading
import time

# Set your OpenAI API key

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Global variables for conversation and corrections
conversation = []
corrections = []

chatbot_speaking = False
SILENCE_TIMEOUT = 10  # Timeout for silence in seconds

# Locks for thread safety
conversation_lock = threading.Lock()
corrections_lock = threading.Lock()

# System message for the chatbot's role
system_message = "You are a helpful assistant. You are here to correct grammar mistakes. And continue the conversation with the user."

# Corrects the grammar of the user's input using OpenAI's API
def correct_grammar_with_openai(text):
    """Use OpenAI to correct the grammar of the user's input."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant that corrects grammar mistakes."},
        {"role": "user", "content": text}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=200,
        temperature=0.7,
        top_p=1,
        n=1,
    )
    return response['choices'][0]['message']['content'].strip()

# Generate a response from GPT-4 based on user input
def generate_gpt4_response(user_input):
    """Generate a response from GPT-4 based on user input."""
    
    messages = [
        {"role": "system", "content": system_message},  # System message
        {"role": "user", "content": user_input}        # User's input
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Chat model
        messages=messages,  # Use the messages parameter
        max_tokens=2000,
        temperature=0.7,
        top_p=1,
        n=1,
    )
    
    return response['choices'][0]['message']['content'].strip()

# Speak the given text using pyttsx3
def speak(text):
    global chatbot_speaking
    chatbot_speaking = True
    engine.say(text)
    engine.runAndWait()
    chatbot_speaking = False

# Listen to the user and process the conversation
def listen_to_user():
    global chatbot_speaking, conversation, corrections
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening to user... (Say something to interrupt)")

        while True:
            try:
                audio = recognizer.listen(source, timeout=SILENCE_TIMEOUT)
                print("Recognizing...")
                user_input = recognizer.recognize_google(audio)
                print(f"User: {user_input}")

                # Add the user input to the conversation
                with conversation_lock:
                    conversation.append(f"User: {user_input}")

                # Correct the user's grammar
                corrected_input = correct_grammar_with_openai(user_input)
                print(f"Corrected: {corrected_input}")
                
                # Log the corrections
                with corrections_lock:
                    corrections.append(f"User input: {user_input} -> Corrected: {corrected_input}")

                # Generate the response from GPT-4
                gpt_response = generate_gpt4_response(corrected_input)
                with conversation_lock:
                    conversation.append(f"Chatbot: {gpt_response}")

                # Speak the GPT response
                speak(gpt_response)

            except sr.UnknownValueError:
                print("Sorry, I couldn't understand. Can you please repeat?")
            except sr.RequestError as e:
                print(f"Error with the speech recognition service: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

# Save the entire conversation and grammar corrections to a text file
def save_conversation():
    with open("Chat_History.txt", "w") as file:
        for line in conversation:
            file.write(line + "\n")
        file.write("\n--- Grammar Corrections ---\n")
        for correction in corrections:
            file.write(correction + "\n")
    print("Conversation saved to Chat_History.txt.")

# Start the listener thread
listener_thread = threading.Thread(target=listen_to_user, daemon=True)
listener_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    save_conversation()
