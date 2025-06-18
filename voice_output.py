import pyttsx3

def speak(text):
    print(f"Voice output: Attempting to speak: '{text}'") # Debug print

    try:
        NURA = pyttsx3.init()
        print("Voice output: pyttsx3 engine initialized.") # Debug print

        # Set voice properties for English output
        voices = NURA.getProperty('voices')
        english_voice_found = False
        selected_voice_name = "Default"
        for voice in voices:
            # Prioritize a common English voice like 'Zira' or 'David' (Microsoft voices) or 'en-us'
            if "zira" in voice.name.lower() or "david" in voice.name.lower() or "en-us" in voice.id.lower():
                NURA.setProperty('voice', voice.id)
                selected_voice_name = voice.name
                english_voice_found = True
                print(f"Voice output: Selected voice: {selected_voice_name}") # Debug print
                break
        if not english_voice_found:
            print("Voice output: Specific English voice not found. Trying other English voices.")
            for voice in voices:
                if "en" in voice.lang.lower(): # Check for any English language voice
                    NURA.setProperty('voice', voice.id)
                    selected_voice_name = voice.name
                    print(f"Voice output: Falling back to voice: {selected_voice_name}") # Debug print
                    break
            if not english_voice_found and not selected_voice_name: # If no English voice was set
                 print("Voice output: No English voice found. Using system default.")

        NURA.setProperty('rate', 170)
        NURA.setProperty('volume', 0.9)
        
        NURA.say(text)
        print(f"Voice output: 'say' method called for text: '{text}'") # Debug print
        NURA.runAndWait()
        print("Voice output: 'runAndWait' completed.") # Debug print

    except Exception as e:
        print(f"Voice output: CRITICAL ERROR - Could not speak. Details: {e}")
        # This is where errors related to pyttsx3 or underlying TTS engine will show up.