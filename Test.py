from tkinter import *
from tkinter import ttk
import speech_recognition as speech_r
import pyaudio
import wave
import threading
import pyttsx3
import queue
import json
import os

root = Tk() 
root.title("Chat Bot")
icon = PhotoImage(file="Avatarka.png")
root.iconphoto(False, icon)
root.geometry("800x800")

CHUNK = 1024
FRT = pyaudio.paInt16
CHAN = 1
RT = 44100
REC_SEC = 5
FILENAME = "output.wav"
HISTORY_FILE = "chat_history.json"

tts_queue = queue.Queue()
tts_busy = False

# Инициализация синтезатора речи в отдельном потоке
def init_tts():
    tts = pyttsx3.init()
    rate = tts.getProperty('rate')
    tts.setProperty('rate', rate-40)

    volume = tts.getProperty('volume')
    tts.setProperty('volume', volume+0.9)

    voices = tts.getProperty('voices')
    for voice in voices:
        if voice.name == 'Anna':
            tts.setProperty('voice', voice.id)
    
    return tts

# Функция для обработки очереди синтеза речи
def process_tts_queue():
    global tts_busy
    if not tts_queue.empty() and not tts_busy:
        tts_busy = True
        text = tts_queue.get()
        
        def speak():
            try:
                tts = init_tts()
                tts.say(text)
                tts.runAndWait()
            except Exception as e:
                print(f"Ошибка синтеза речи: {e}")
            finally:
                global tts_busy
                tts_busy = False
                root.after(100, process_tts_queue)
        
        threading.Thread(target=speak, daemon=True).start()

# Функция для загрузки истории из JSON
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Ошибка загрузки истории: {e}")
            return []
    return []

# Функция для сохранения истории в JSON
def save_history(history):
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as file:
            json.dump(history, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения истории: {e}")

# Инициализация окна чата и загрузка истории
p = pyaudio.PyAudio()
r = speech_r.Recognizer()

chat_frame = Text(root, height=30, width=85, state='disabled')
chat_frame.place(x=10, y=40)

label = Label(text="Chat Bot AI")
label.pack()

# Загрузка истории при запуске
history = load_history()
chat_frame.config(state='normal')
for entry in history:
    chat_frame.insert(END, f"{entry['sender']}: {entry['message']}\n")
chat_frame.config(state='disabled')

def destroy_window():
    root.destroy()
    p.terminate()
    print("Window is destroyed")

closeWindowButton = ttk.Button(text="Close window", command=destroy_window)
closeWindowButton.place(x=700, y=10)

inputFieldText = Text(height=5, width=85)
inputFieldText.place(x=10, y=700)

def response_bot(message):
    text = 'Остроумный ответ'
    
    if text:
        chat_frame.config(state='normal')
        chat_frame.insert(END, f"Bot: {text}\n")
        chat_frame.config(state='disabled')
        
        # Сохранение ответа бота в историю
        history.append({"sender": "Bot", "message": text})
        save_history(history)
    
    # Добавляем текст в очередь для синтеза речи
    tts_queue.put(text)
    process_tts_queue()

def send_message(event=None):
    message = inputFieldText.get("1.0", END).strip()
    
    if message:
        chat_frame.config(state='normal')
        chat_frame.insert(END, f"You: {message}\n")
        chat_frame.config(state='disabled')
        inputFieldText.delete("1.0", END)
        
        history.append({"sender": "You", "message": message})
        save_history(history)
        
        response_bot(message)
    
    return "break"

sendMessageButton = ttk.Button(text="Send", command=send_message, width=15)
sendMessageButton.place(x=700, y=710)

def record_voice(event=None):
    def recording_thread():
        try:
            stream = p.open(format=FRT, channels=CHAN, rate=RT, input=True, frames_per_buffer=CHUNK)
            
            recordMessageButton.config(text="Record...", state='disabled')
            
            frames = []
            for i in range(0, int(RT / CHUNK * REC_SEC)):
                data = stream.read(CHUNK)
                frames.append(data)

            stream.stop_stream()
            stream.close()

            w = wave.open(FILENAME, 'wb')
            w.setnchannels(CHAN)
            w.setsampwidth(p.get_sample_size(FRT))
            w.setframerate(RT)
            w.writeframes(b''.join(frames))
            w.close()
            
            sample = speech_r.WavFile(FILENAME)

            with sample as audio:
                r.adjust_for_ambient_noise(audio)
                content = r.record(audio)

            recordText = r.recognize_google(content, language="ru-RU")
            
            root.after(0, lambda: inputFieldText.insert("1.0", recordText))
            
        except Exception as e:
            error_message = f"Ошибка: {str(e)}" 
            root.after(0, lambda: inputFieldText.insert("1.0", error_message))
        finally:
            root.after(0, lambda: recordMessageButton.config(text="Record", state='normal'))
    
    threading.Thread(target=recording_thread, daemon=True).start()
    return "break"

recordMessageButton = ttk.Button(text="Record", command=record_voice, width=15)
recordMessageButton.place(x=700, y=750)

root.bind('<Control-Return>', send_message)
root.bind('<Control-KP_Enter>', send_message)

inputFieldText.bind('<Tab>', record_voice)

root.bind('<Escape>', lambda event: destroy_window())

def handle_enter(event):
    if event.state & 0x1:
        return send_message(event)
    else:
        return None

inputFieldText.bind('<Return>', handle_enter)

inputFieldText.focus_set()

root.mainloop()