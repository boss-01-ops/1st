import os
import subprocess
import sys
import requests
from PIL import Image
from customtkinter import CTkImage
from pydub import AudioSegment
import concurrent.futures
import speech_recognition as sr

class Transcriber:

    def __init__(self,video_file_path=None,audio_file_path=None, default_image_frame=None,indicator=None, transcribe_label=None,summary_label=None):

        self.video_file_path = video_file_path
        self.audio_file_path = audio_file_path
        self.default_image_frame = default_image_frame
        self.indicator_label = indicator
        self.transcribe_label = transcribe_label
        self.summary_label = summary_label



        self.ELEMENTS_IMAGE_PATH = os.path.join(os.getcwd(), 'assets', 'image')
        AudioSegment.ffmpeg = r"./ffmpeg.exe"  # Update if needed

        self.startupinfo = None
        if sys.platform == "win32":
            self.startupinfo = subprocess.STARTUPINFO()
            self.startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        self.r = sr.Recognizer()
        
    def load_image(self,image_path, size):
        image = Image.open(image_path)
        return CTkImage(image, size=size)

    def transcribe_audio_chunk(self,chunk_path):
        with sr.AudioFile(chunk_path) as source:
            audio = self.r.record(source)
            return self.r.recognize_google(audio)

    def transcribe_audio_google_parallel(self):
        # Indicate processing
        self.indicator_label.configure(text='Initializing transcriber...')
        sound = AudioSegment.from_file(self.audio_file_path)
        chunk_length_ms = 40000  # 30 seconds
        chunks = []
        start = 0
        while start < len(sound):
            end = min(start + chunk_length_ms, len(sound))
            chunk = sound[start:end]
            chunks.append(chunk)
            start = end

        folder_name = "audio-chunks"
        os.makedirs(folder_name, exist_ok=True)

        chunk_paths = []
        for i, chunk in enumerate(chunks):
            path = os.path.join(folder_name, f"chunk{i}.wav")
            chunk.export(path, format="wav")
            chunk_paths.append((i, path))

        # Update image while writing
        img = Image.open(os.path.join(self.ELEMENTS_IMAGE_PATH, 'writting.jpg'))
        resized_img = img.resize((300, 250))
        ct_img = CTkImage(resized_img, size=(300, 250))
        self.default_image_frame.configure(image=ct_img)
        self.default_image_frame.image = ct_img

        results = [None] * len(chunk_paths)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(self.transcribe_audio_chunk, path[1]): path[0] for path in chunk_paths}
            total = len(chunk_paths)
            for idx, future in enumerate(concurrent.futures.as_completed(futures)):
                index = futures[future]
                try:
                    results[index] = future.result()
                except:
                    results[index] = ""
                progress = (idx + 1) / total * 100
                self.indicator_label.configure(text=f"Progress: {progress:.2f}%")

        for i in chunk_paths:
            os.remove(i[1])

        return "\n".join(results)

    def summarize_text(self):
        API_KEY = "YOUR API KEY HERE"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
        data = {
            "contents": [{
                "parts": [{
                    "text": f"Summarize the following content step-by-step and top 5 keyword from the following text:\n\n{self.transcribed_text}"
                }]
            }]
        }
        response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        if response.ok:
            response_json = response.json()
            return response_json["candidates"][0]["content"]["parts"][0]["text"]
        
        else:
            return f"Error: {response.status_code} {response.text}"

    def video_to_text(self):
        images = {
            'listing': self.load_image(os.path.join(self.ELEMENTS_IMAGE_PATH, '9251270.png'), (200, 200)),
            'writing': self.load_image(os.path.join(self.ELEMENTS_IMAGE_PATH, 'writting.jpg'), (200, 200)),
            'ai_writing': self.load_image(os.path.join(self.ELEMENTS_IMAGE_PATH, 'ai_writting.jpg'), (200, 200)),
            'done': self.load_image(os.path.join(self.ELEMENTS_IMAGE_PATH, 'done.png'), (200, 200))
        }

        self.default_image_frame.configure(image=images['listing'], text="")
        self.indicator_label.configure(text="Audio extracting...")

        try:
            subprocess.run(["module/ffmpeg", "-y", "-i", self.video_file_path, "-vn", "-ar", "16000", "-ac", "1", "-sample_fmt", "s16", self.audio_file_path],
                        check=True, startupinfo=self.startupinfo)
            self.indicator_label.configure(text="Audio extracted successfully")
        except subprocess.CalledProcessError as e:
            self.indicator_label.configure(text=f"Error extracting audio: {e}")
            return

        self.indicator_label.configure(text="Transcribing using Google Speech API...")
        self.transcribed_text = self.transcribe_audio_google_parallel()

        self.transcribe_label.configure(text=self.transcribed_text, font=(" ", 14), wraplength=500, anchor='w', justify="left")
        with open("transcription.txt", "w", encoding="utf-8") as f:
            f.write(self.transcribed_text)

        self.indicator_label.configure(text="Generating summary...")
        self.default_image_frame.configure(image=images['ai_writing'], text="")

        summary = self.summarize_text()

        self.summary_label.configure(text=summary, font=(" ", 14), wraplength=500, anchor='w', justify="left")

        with open("summary.txt", "w", encoding="utf-8") as f:
            f.write(summary)

        self.indicator_label.configure(text="Summary generated!")
        self.default_image_frame.configure(image=images['done'], text="")

    def audio_to_text(self):
        images = {
            'writing': self.load_image(os.path.join(self.ELEMENTS_IMAGE_PATH, 'writting.jpg'), (200, 200)),
            'ai_writing': self.load_image(os.path.join(self.ELEMENTS_IMAGE_PATH, 'ai_writting.jpg'), (200, 200)),
            'done': self.load_image(os.path.join(self.ELEMENTS_IMAGE_PATH, 'done.png'), (200, 200))
        }

        self.indicator_label.configure(text="Transcribing audio using Google Speech API...")
        self.default_image_frame.configure(image=images['writing'], text="")

        self.transcribed_text = self.transcribe_audio_google_parallel()

        self.transcribe_label.configure(text=self.transcribed_text, font=(" ", 14), wraplength=500, anchor='w', justify="left")

        with open("transcription.txt", "w", encoding="utf-8") as f:
            f.write(self.transcribed_text)

        self.indicator_label.configure(text="Generating summary...")
        self.default_image_frame.configure(image=images['ai_writing'], text="")

        summary = self.summarize_text()

        self.summary_label.configure(text=summary, font=(" ", 14), wraplength=500, anchor='w', justify="left")

        with open("summary.txt", "w", encoding="utf-8") as f:
            f.write(summary)

        self.indicator_label.configure(text="Summary generated!")
        self.default_image_frame.configure(image=images['done'], text="")

    def textfile_to_summary(self):
        images = {
            'ai_writing': self.load_image(os.path.join(self.ELEMENTS_IMAGE_PATH, 'ai_writting.jpg'), (200, 200)),
            'done': self.load_image(os.path.join(self.ELEMENTS_IMAGE_PATH, 'done.png'), (200, 200))
        }

        self.indicator_label.configure(text="Reading text file...")
        
        try:
            with open(self.video_file_path, "r", encoding="utf-8") as f:
                self.transcribed_text = f.read()
        except Exception as e:
            self.indicator_label.configure(text=f"Error reading file: {e}")
            return

        self.transcribe_label.configure(text=self.transcribed_text, font=(" ", 14), wraplength=500, anchor='w', justify="left")

        self.indicator_label.configure(text="Generating summary from text file...")
        self.default_image_frame.configure(image=images['ai_writing'], text="")

        summary = self.summarize_text()

        self.summary_label.configure(text=summary, font=(" ", 14), wraplength=500, anchor='w', justify="left")

        with open("summary_from_textfile.txt", "w", encoding="utf-8") as f:
            f.write(summary)

        self.indicator_label.configure(text="Summary generated from text!")
        self.default_image_frame.configure(image=images['done'], text="")
