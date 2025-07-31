import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import requests
from random import choice

# Initialize text-to-speech engine
try:
    engine = pyttsx3.init()
    engine.setProperty('voice', r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0')  # Male voice (David)
except Exception as e:
    print(f"Error initializing text-to-speech: {e}")
    exit()

# Greetings based on time
def greet():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        return "Good morning, sir!"
    elif 12 <= hour < 18:
        return "Good afternoon, sir!"
    else:
        return "Good evening, sir!"

# Speak function
def speak(text):
    print(f"JARVIS: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in text-to-speech: {e}")

# Listen for voice input
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
            query = recognizer.recognize_google(audio).lower()
            print(f"You said: {query}")
            return query
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that.")
            return ""
        except sr.RequestError as e:
            speak(f"Sorry, my speech service is down: {e}")
            return ""
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return ""

# Process commands
def process_command(query):
    if "exit" in query or "stop" in query:
        speak("Goodbye, sir.")
        exit()
    elif "time" in query:
        time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {time}.")
    elif "open browser" in query:
        webbrowser.open("https://www.google.com")
        speak("Opening the browser, sir.")
    elif "who are you" in query:
        speak("I am JARVIS, your personal assistant, inspired by Tony Stark's AI.")
    else:
        speak(choice(["I'm working on it, sir.", "One moment, please.", "Processing your request."]))

# Main loop
if __name__ == "__main__":
    speak(greet())
    while True:
        query = listen()
        if query:
            process_command(query)