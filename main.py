import tkinter as tk
from tkinter import ttk # For themed widgets
import threading # To run listening in a separate thread
import time # For delays

# Import your utility modules
from voice_output import speak
from voice_input import listen_command
from dateTime_utils import get_date, get_time
from personal_data_handler import PersonalDataHandler

class NURAGUI:
    def __init__(self, master):
        self.master = master
        master.title("NURA Personal Assistant")
        master.geometry("500x350") # Larger window for better UI
        master.resizable(False, False) # Keep window fixed size

        self.personal_data_manager = PersonalDataHandler()
        self.is_active = False # State to track if assistant is active/listening for commands

        self.WAKE_WORDS = ["nura", "hey nura", "ok nura"]

        # --- UI Elements ---
        self.status_label = ttk.Label(master, text="NURA: Waiting for activation...", font=("Arial", 16))
        self.status_label.pack(pady=20)

        self.mic_icon_label = ttk.Label(master, text="🎤", font=("Arial", 72)) # Larger mic icon
        self.mic_icon_label.pack(pady=10)
        self.mic_icon_label.config(foreground="grey") # Grey when inactive

        self.user_display_label = ttk.Label(master, text="", font=("Arial", 12), wraplength=450)
        self.user_display_label.pack(pady=(0, 10))

        self.response_display_label = ttk.Label(master, text="", font=("Arial", 12, "italic"), wraplength=450)
        self.response_display_label.pack(pady=(0, 10))

        # --- Start Activation Listener ---
        # Run activation listening in a separate thread to not block the UI
        self.activation_thread = threading.Thread(target=self._listen_for_activation, daemon=True)
        self.activation_thread.start()
        print("NURAGUI: Activation listener thread started.")
        
        # Bind the window close event to cleanup
        master.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        """Handle window closing event to ensure database connection is closed."""
        print("NURAGUI: Closing application.")
        self.personal_data_manager.close()
        self.master.destroy()

    def _update_ui_status(self, text, color="black", mic_color="grey"):
        """Helper to update UI elements from any thread."""
        self.master.after(0, lambda: self.status_label.config(text=text, foreground=color))
        self.master.after(0, lambda: self.mic_icon_label.config(foreground=mic_color))
        self.master.after(0, lambda: self.user_display_label.config(text=""))
        self.master.after(0, lambda: self.response_display_label.config(text=""))


    def _display_conversation(self, user_text="", navion_response=""):
        """Helper to display user input and NURA's response."""
        self.master.after(0, lambda: self.user_display_label.config(text=f"You: {user_text}"))
        self.master.after(0, lambda: self.response_display_label.config(text=f"NURA: {navion_response}"))


    def _listen_for_activation(self):
        """Continuously listens for the activation command."""
        self._update_ui_status("NURA: Waiting for activation...", "black", "grey")
        speak("Hello, I am NURA, your neural personal assistant. To activate me, say 'NURA' or 'Hey NURA'.")

        while True:
            print("NURAGUI: Listening for wake word...")
            self._update_ui_status("NURA: Say 'NURA' to activate...", "blue", "grey")
            trigger = listen_command()
            print(f"NURAGUI: Detected trigger: '{trigger}'")

            if self._contains_wake_word(trigger):
                self._activate_assistant()
                break # Exit activation loop, now ready for commands
            elif trigger:
                self._update_ui_status("NURA: Didn't hear the wake word. Trying again...", "orange", "grey")
                speak("I didn't hear the wake word. Please try again.")
                time.sleep(1) # Small delay before retrying


    def _activate_assistant(self):
        self.is_active = True
        self._update_ui_status("NURA: Active. Listening for commands...", "green", "red")
        speak("I'm listening. What do you want me to do?")
        print("NURAGUI: Assistant activated. Starting command listener.")
        
        # Start command listener in a new thread
        self.command_thread = threading.Thread(target=self._listen_for_commands, daemon=True)
        self.command_thread.start()


    def _deactivate_assistant(self):
        self.is_active = False
        self._update_ui_status("NURA: Deactivated. Waiting for activation...", "black", "grey")
        speak("Goodbye! Have a great day!")
        print("NURAGUI: Assistant deactivated.")
        # Restart the activation listener
        self.activation_thread = threading.Thread(target=self._listen_for_activation, daemon=True)
        self.activation_thread.start()


    def _contains_wake_word(self, text):
        if not text:
            return False
        return any(wake_word in text.lower() for wake_word in self.WAKE_WORDS)

    def _listen_for_commands(self):
        """Continuously listens for user commands when active."""
        while self.is_active:
            self._update_ui_status("NURA: Listening for commands...", "green", "red")
            user_input = listen_command()
            
            self._display_conversation(user_text=user_input)

            if not user_input:
                response = "I didn't catch that. Please try again."
                self._update_ui_status("NURA: Undefined command...", "orange", "red")
                speak(response)
                self._display_conversation(user_text="", navion_response=response)
                time.sleep(2) # Give user time to see the message
                continue

            # Check for deactivation command first
            if "exit" in user_input.lower() or "quit" in user_input.lower() or \
               "goodbye" in user_input.lower() or "bye bye" in user_input.lower():
                self.master.after(0, self._deactivate_assistant) # Call on main thread
                break # Exit this command listening loop

            response = self._process_query(user_input)
            self._display_conversation(user_text=user_input, navion_response=response)
            speak(response)
            time.sleep(3) # Display response for a few seconds before going back to listening state
            self._update_ui_status("NURA: Listening for commands...", "green", "red")


    def _process_query(self, query):
        query = query.lower()

        # --- Logic to store personal data ---
        if "my name is" in query:
            parts = query.split("my name is", 1)
            if len(parts) > 1:
                value = parts[1].strip()
                if value:
                    self.personal_data_manager.store_data("my name", value)
                    return f"Okay, I will remember that your name is {value}."
                else:
                    return "I didn't understand your name. Could you please state it clearly?"
            return "Could you please tell me your name after 'my name is'?"

        elif "my favorite color is" in query:
            parts = query.split("my favorite color is", 1)
            if len(parts) > 1:
                value = parts[1].strip()
                if value:
                    self.personal_data_manager.store_data("my favorite color", value)
                    return f"Alright, your favorite color is {value}. I'll remember that."
                else:
                    return "I didn't understand your favorite color."
            return "Could you please tell me your favorite color after 'my favorite color is'?"

        elif "remember that my name is" in query:
            parts = query.split("remember that my name is", 1)
            if len(parts) > 1:
                value = parts[1].strip()
                if value:
                    self.personal_data_manager.store_data("my name", value)
                    return f"Okay, I've noted that your name is {value}."
                else:
                    return "I didn't catch the name to remember."
            return "Please tell me the name to remember after 'remember that my name is'."

        elif "remember that my favorite color is" in query:
            parts = query.split("remember that my favorite color is", 1)
            if len(parts) > 1:
                value = parts[1].strip()
                if value:
                    self.personal_data_manager.store_data("my favorite color", value)
                    return f"Got it, I'll remember your favorite color is {value}."
                else:
                    return "I didn't catch the color to remember."
            return "Please tell me the color to remember after 'remember that my favorite color is'."

        # --- Logic to retrieve personal data ---
        elif "what is my name" in query:
            name = self.personal_data_manager.get_data("my name")
            if name:
                return f"Your name is {name}."
            else:
                return "I don't remember your name. Would you like to tell me?"
        
        elif "what is my favorite color" in query:
            color = self.personal_data_manager.get_data("my favorite color")
            if color:
                return f"Your favorite color is {color}."
            else:
                return "I don't remember your favorite color. Would you like to tell me?"

        # --- General commands ---
        elif "what is the date" in query or "today's date" in query:
            current_date = get_date()
            return f"Today's date is {current_date}."
        elif "what is the time" in query or "current time" in query:
            current_time = get_time()
            return f"The current time is {current_time}."
        elif "what is the weather" in query or "tell me about the weather" in query:
            # You can integrate a real weather API here later
            return "The weather in Kolkata is pleasant today, with a temperature of 28 degrees Celsius."
        elif "who is elon musk" in query:
            return "Elon Musk is an entrepreneur and investor. He is the founder, CEO, and chief designer of SpaceX, Tesla, Neuralink, and The Boring Company."
        elif "who is donald trump" in query:
            return "Donald Trump was the 45th President of the United States."
        else:
            return f"I can help you with date, time, weather, and remember your name or favorite color. You said: '{query}'."


if __name__ == "__main__":
    root = tk.Tk()
    app = NURAGUI(root)
    root.mainloop()
    # The _on_closing method should handle database closing