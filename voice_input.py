import speech_recognition as sr

recognizer = sr.Recognizer()

def listen_command():
    with sr.Microphone() as source:
        print("NURA is listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            print("Recognizing...")
            # Changed language to English (US)
            text = recognizer.recognize_google(audio, language='en-US') # Use 'en-IN' for Indian English accent
            print(f"Recognized: {text}")
            return text
        except sr.UnknownValueError:
            print("I didn't understand, please repeat.")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return ""
        except Exception as e:
            print(f"An error occurred: {e}")
            return ""