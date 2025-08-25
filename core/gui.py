import tkinter as tk
from tkinter import ttk
import threading

class ChatGUI:
    def __init__(self, bot_core, speech_manager):
        self.bot = bot_core
        self.speech = speech_manager
        
        self.root = tk.Tk()
        self.root.title("Chat Bot")
        self.root.geometry("800x800")
        
        try:
            icon = tk.PhotoImage(file="Avatarka.png")
            self.root.iconphoto(False, icon)
        except:
            pass
        
        self.setup_gui()
        self.bind_events()
    
    def setup_gui(self):
        self.chat_frame = tk.Text(self.root, height=30, width=85, state='disabled')
        self.chat_frame.place(x=10, y=40)
        
        label = tk.Label(self.root, text="Chat Bot AI")
        label.pack()
        
        history = self.bot.get_chat_history()
        self.chat_frame.config(state='normal')
        for entry in history:
            self.chat_frame.insert(tk.END, f"{entry['sender']}: {entry['message']}\n")
        self.chat_frame.config(state='disabled')
        
        self.closeWindowButton = ttk.Button(self.root, text="Close window", 
                                          command=self.destroy_window)
        self.closeWindowButton.place(x=700, y=10)
        
        self.inputFieldText = tk.Text(self.root, height=5, width=85)
        self.inputFieldText.place(x=10, y=700)
        
        self.sendMessageButton = ttk.Button(self.root, text="Send", 
                                          command=self.send_message, width=15)
        self.sendMessageButton.place(x=700, y=710)
        
        self.recordMessageButton = ttk.Button(self.root, text="Record", 
                                            command=self.record_voice, width=15)
        self.recordMessageButton.place(x=700, y=750)
        
        self.inputFieldText.focus_set()
    
    def bind_events(self):
        self.root.bind('<Control-Return>', self.send_message)
        self.root.bind('<Control-KP_Enter>', self.send_message)
        self.inputFieldText.bind('<Tab>', self.record_voice)
        self.root.bind('<Escape>', lambda event: self.destroy_window())
        self.inputFieldText.bind('<Return>', self.handle_enter)
    
    def handle_enter(self, event):
        if event.state & 0x1:
            return self.send_message(event)
        return None
    
    def send_message(self, event=None):
        message = self.inputFieldText.get("1.0", tk.END).strip()
        
        if message:
            self.chat_frame.config(state='normal')
            self.chat_frame.insert(tk.END, f"You: {message}\n")
            self.chat_frame.config(state='disabled')
            self.inputFieldText.delete("1.0", tk.END)
            
            threading.Thread(target=self.process_bot_response, args=(message,), daemon=True).start()
        
        return "break"
    
    def process_bot_response(self, message):
        response = self.bot.process_message(message)
        
        self.root.after(0, lambda: self.display_bot_response(response))
    
    def display_bot_response(self, response):
        if response:
            self.chat_frame.config(state='normal')
            self.chat_frame.insert(tk.END, f"Bot: {response}\n")
            self.chat_frame.config(state='disabled')
            
            self.speech.speak(response)
    
    def record_voice(self, event=None):
        def recording_thread():
            self.recordMessageButton.config(text="Record...", state='disabled')
            try:
                recorded_text = self.speech.record_audio()
                if recorded_text:
                    self.root.after(0, lambda: self.inputFieldText.insert("1.0", recorded_text))
            except Exception as e:
                error_message = f"Ошибка: {str(e)}"
                self.root.after(0, lambda: self.inputFieldText.insert("1.0", error_message))
            finally:
                self.root.after(0, lambda: self.recordMessageButton.config(text="Record", state='normal'))
        
        threading.Thread(target=recording_thread, daemon=True).start()
        return "break"
    
    def destroy_window(self):
        self.speech.cleanup()
        self.root.destroy()
        print("Window is destroyed")
    
    def run(self):
        self.root.mainloop()