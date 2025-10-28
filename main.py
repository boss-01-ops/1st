from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkImage, CTkScrollableFrame, set_appearance_mode
from tkinter import filedialog, messagebox
import os
from PIL import Image
from threading import Thread
from LIBS.transcriber import Transcriber

set_appearance_mode('light')

class SummarizeAi:

    ICON_PATH = os.path.join(os.getcwd(), 'assets', 'icons')
    ELEMENT_PATH = os.path.join(os.getcwd(), 'assets', 'image')

    def save_file(self):
        try:
            
            transcription_file = os.path.join(os.getcwd(), 'transcription.txt')
            summary_file = os.path.join(os.getcwd(), 'summary.txt')

            # Read contents
            with open(transcription_file, "r", encoding="utf-8") as f:
                transcription = f.read()

            with open(summary_file, "r", encoding="utf-8") as f:
                summary = f.read()

            # Merge content
            combined_content = f"--- TRANSCRIPTION ---\n\n{transcription}\n\n--- SUMMARY ---\n\n{summary}"

            # Open save file dialog
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])

            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(combined_content)
                messagebox.showinfo("Saved", "File saved successfully!")
            else:
                messagebox.showwarning("Cancelled", "File save cancelled.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

    def th_video_to_text(self):
        th = Thread(target=self.video_to_text)
        th.start()

    def video_to_text(self):
        print(f"Video file path: {self.file_path}")

        #self.transcribe_label.configure(text="",justify="center", font=(" ", 14), wraplength=700)
        Transcriber(video_file_path=self.file_path,
            audio_file_path='audio.wav',
            default_image_frame=self.default_img_label,
            indicator=self.indication_label,
            transcribe_label=self.transcribe_label,
            summary_label=self.summary_label,).video_to_text()

    def audio_to_text(self):
        Transcriber(video_file_path=self.file_path,
            audio_file_path='audio.wav',
            default_image_frame=self.default_img_label,
            indicator=self.indication_label,
            transcribe_label=self.transcribe_label,
            summary_label=self.summary_label).audio_to_text()

    def th_audio_to_text(self):
        th = Thread(target=self.audio_to_text)
        th.start()

    def textfile_to_summary(self):


        Transcriber(video_file_path=self.file_path,
            audio_file_path='audio.wav',
            default_image_frame=self.default_img_label,
            indicator=self.indication_label,
            transcribe_label=self.transcribe_label,
            summary_label=self.summary_label).textfile_to_summary()

    def th_textfile_to_summary(self):
        th = Thread(target=self.textfile_to_summary)
        th.start()
   
    def __init__(self, window):
        self.window = window

    def update_summary_field(self, text=None):
        for i in range(30):
            CTkLabel(master=self.summary_frame, text=f"Summary Line {i+1}", font=(" ", 14)).pack(pady=5, anchor='w', padx=10)

    def gui(self):
        width, height = 1190, 720
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        self.window.title("Summarize AI")

        # Input and Output Frame
        self.input_frame = CTkFrame(master=self.window, corner_radius=0, fg_color='#F2F2FC')
        self.input_frame.place(relx=0, rely=0, relwidth=0.37, relheight=1.0)

        self.output_frame = CTkFrame(master=self.window, corner_radius=0, fg_color='#F2F2FC')
        self.output_frame.place(relx=0.37, rely=0, relwidth=0.63, relheight=1.0)
        
        # File Input Frame
        self.file_input_frame = CTkFrame(master=self.input_frame, corner_radius=25, fg_color='white')
        self.file_input_frame.place(relx=0.5, rely=0.2, anchor="center", relwidth=0.9, relheight=0.25)

        save_image_path = os.path.join(self.ICON_PATH, 'save.png')
        save_image = Image.open(save_image_path)
        save_image = CTkImage(light_image=save_image, dark_image=save_image, size=(30, 30))
        save_btn = CTkButton(master=self.file_input_frame, text="", image=save_image, font=(" ", 14),fg_color='white',hover_color='#F2F2FC',command=self.save_file)
        save_btn.place(relx=0.65, rely=0.09, relwidth=0.2, relheight=0.25)



        CTkLabel(master=self.file_input_frame, text="Select your file here", font=(" ", 19, 'bold'),
                 fg_color='white', bg_color='white').place(relx=0.3, rely=0.2, anchor="center")

        btn_fram = CTkFrame(master=self.file_input_frame, fg_color='#EEF0FB', corner_radius=25)
        btn_fram.place(relx=0.5, rely=0.59, relwidth=0.87, relheight=0.35, anchor="center")

        file_btn = CTkButton(master=btn_fram, text="File", font=(" ", 14),
                             corner_radius=85, hover_color='#36719F',
                             fg_color='#523CAD', command=self.select_file)
        file_btn.place(relx=0.08, rely=0.1, relwidth=0.3, relheight=0.78)

        self.file_indicator = CTkLabel(master=btn_fram, text="Select a file", font=(" ", 14),
                                       fg_color='#EEF0FB', bg_color='#EEF0FB')
        self.file_indicator.place(relx=0.65, rely=0.5, anchor="center")

        # Indication Frame
        self.indication_frame = CTkFrame(master=self.input_frame, corner_radius=25, fg_color='white')
        self.indication_frame.place(relx=0.5, rely=0.65, anchor="center", relwidth=0.9, relheight=0.57)

        # Load default image
        default_img_path = os.path.join(self.ELEMENT_PATH, 'file_.jpg')
        default_img = Image.open(default_img_path)
        default_img = default_img.resize((200, 200))
        default_img = CTkImage(light_image=default_img, dark_image=default_img, size=(200, 200))

        self.default_img_label = CTkLabel(master=self.indication_frame, text="", image=default_img, fg_color='white')
        self.default_img_label.place(relx=0.5, rely=0.5, anchor="center")

        # Indicator label
        self.indication_label = CTkLabel(master=self.indication_frame, text="................", font=(" ", 14))
        self.indication_label.place(relx=0.5, rely=0.9, anchor="center")

        # Scrollable Transcribe Frame
        self.transcribe_scroll_frame = CTkScrollableFrame(master=self.output_frame, fg_color='white', corner_radius=25)
        self.transcribe_scroll_frame.place(relx=0.05, rely=0.04, relwidth=0.9, relheight=0.45)

        self.transcribe_label = CTkLabel(
            master=self.transcribe_scroll_frame,
            text="Select your video or audio file to automatically generate and\n view the transcription here.",
            font=("Arial", 20, 'bold'),
            text_color="#4B4B4B",
            wraplength=700,
            justify="center"
        )
        self.transcribe_label.pack(pady=90, padx=20)

        # Summary Frame (Static for now)
        self.summary_frame = CTkScrollableFrame(master=self.output_frame, fg_color='white', corner_radius=25)
        self.summary_frame.place(relx=0.05, rely=0.5, relwidth=0.9, relheight=0.45)

        self.summary_label = CTkLabel(
            master=self.summary_frame,
            text="Summary is not available yet.\n",
            font=("Arial", 20, 'bold'),
            text_color="#4B4B4B",
            wraplength=700,
            justify="center"
        )
        self.summary_label.pack(pady=110, padx=20, anchor="center")

    def select_file(self):
        filetypes = [
            ("All supported files", "*.mp4 *.mp3 *.wav *.txt"),
            ("Video files", "*.mp4"),
            ("Audio files", "*.mp3 *.wav"),
            ("Text files", "*.txt")
        ]

        filepath = filedialog.askopenfilename(title="Select a file", filetypes=filetypes)
        self.file_path = filepath  # Store the file path for later use
        if filepath:
            ext = os.path.splitext(filepath)[-1].lower()

            if ext in ['.mp4']:
                file_type = "Video"
                self.th_video_to_text()
            elif ext in ['.mp3', '.wav']:
                file_type = "Audio"
                self.th_audio_to_text()
            elif ext == '.txt':
                file_type = "Text"
                self.th_textfile_to_summary()
            else:
                file_type = "Unknown"

            print(f"Selected file: {filepath}")
            print(f"File type: {file_type}")
            self.indication_label.configure(text="Initializing...")
            self.file_indicator.configure(text=f"File Selected")
        else:
            print("No file selected.")
            self.file_indicator.configure(text="No file selected")
            messagebox.showwarning("File not found", "No file selected. Please select a valid file.")

# Run App
window = CTk()
app = SummarizeAi(window)
app.gui()
window.mainloop()
