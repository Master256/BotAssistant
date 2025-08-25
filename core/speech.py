import speech_recognition as speech_r
import pyaudio
import wave
import threading
import pyttsx3
import queue

class SpeechManager:
    def __init__(self):
        self.CHUNK = 1024
        self.FRT = pyaudio.paInt16
        self.CHAN = 1
        self.RT = 44100
        self.REC_SEC = 5
        self.FILENAME = "output.wav"
        
        self.tts_queue = queue.Queue()
        self.tts_busy = False
        self.p = pyaudio.PyAudio()
        self.r = speech_r.Recognizer()
        
        self.init_tts_engine()
    
    def init_tts_engine(self):
        """Инициализация синтезатора речи"""
        self.tts = pyttsx3.init()
        rate = self.tts.getProperty('rate')
        self.tts.setProperty('rate', rate-40)
        
        volume = self.tts.getProperty('volume')
        self.tts.setProperty('volume', volume+0.9)
        
        voices = self.tts.getProperty('voices')
        for voice in voices:
            if voice.name == 'Anna':
                self.tts.setProperty('voice', voice.id)
                break
    
    def speak(self, text):
        """Добавляет текст в очередь для синтеза речи"""
        self.tts_queue.put(text)
        self.process_tts_queue()
    
    def process_tts_queue(self):
        """Обрабатывает очередь синтеза речи"""
        if not self.tts_queue.empty() and not self.tts_busy:
            self.tts_busy = True
            text = self.tts_queue.get()
            
            def speak_thread():
                try:
                    self.tts.say(text)
                    self.tts.runAndWait()
                except Exception as e:
                    print(f"Ошибка синтеза речи: {e}")
                finally:
                    self.tts_busy = False
            
            threading.Thread(target=speak_thread, daemon=True).start()
    
    def record_audio(self):
        """Записывает аудио и преобразует в текст"""
        try:
            stream = self.p.open(format=self.FRT, channels=self.CHAN, 
                               rate=self.RT, input=True, 
                               frames_per_buffer=self.CHUNK)
            
            frames = []
            for i in range(0, int(self.RT / self.CHUNK * self.REC_SEC)):
                data = stream.read(self.CHUNK)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            w = wave.open(self.FILENAME, 'wb')
            w.setnchannels(self.CHAN)
            w.setsampwidth(self.p.get_sample_size(self.FRT))
            w.setframerate(self.RT)
            w.writeframes(b''.join(frames))
            w.close()
            
            with speech_r.WavFile(self.FILENAME) as audio:
                self.r.adjust_for_ambient_noise(audio)
                content = self.r.record(audio)
            
            return self.r.recognize_google(content, language="ru-RU")
            
        except Exception as e:
            raise Exception(f"Ошибка записи аудио: {str(e)}")
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.p.terminate()