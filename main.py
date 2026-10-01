import customtkinter as ctk
import tkinter as tk
import yt_dlp
import threading
import requests
from io import BytesIO
from PIL import Image
import os
import re

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Youtube Downloader v1.1.0")
        self.geometry("600x700")
        self.resizable(False, False)

        # Set window icon
        import sys
        try:
            if hasattr(sys, '_MEIPASS'):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(base_path, "icon.png")
            if os.path.exists(icon_path):
                icon_img = tk.PhotoImage(file=icon_path)
                self.iconphoto(False, icon_img)
        except Exception:
            pass

        # state variables
        self.video_info = None
        self.available_resolutions = []
        self.best_resolution = ""
        self.is_downloading = False

        self.setup_ui()
        self.after(100, self.check_and_download_ffmpeg)

    def check_and_download_ffmpeg(self):
        import shutil
        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            for path in ["/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"]:
                if os.path.exists(path):
                    ffmpeg_path = path
                    break
        
        app_dir = os.path.expanduser("~/.youtube_downloader_app")
        local_ffmpeg = os.path.join(app_dir, "ffmpeg")
        
        if not ffmpeg_path and os.path.exists(local_ffmpeg):
            ffmpeg_path = local_ffmpeg
            
        if ffmpeg_path:
            self.ffmpeg_path = ffmpeg_path
            self.status_label.configure(text="Ready", text_color="black")
            self.fetch_btn.configure(state="normal")
            return
            
        self.ffmpeg_path = None
        self.status_label.configure(text="Downloading ffmpeg (required)...", text_color="yellow")
        self.fetch_btn.configure(state="disabled")
        self.download_btn.configure(state="disabled")
        
        threading.Thread(target=self.download_ffmpeg_thread, args=(app_dir, local_ffmpeg), daemon=True).start()
        
    def download_ffmpeg_thread(self, app_dir, local_ffmpeg):
        try:
            os.makedirs(app_dir, exist_ok=True)
            import zipfile
            import urllib.request
            import ssl
            
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            url = "https://evermeet.cx/ffmpeg/getrelease/zip"
            zip_path = os.path.join(app_dir, "ffmpeg.zip")
            
            with urllib.request.urlopen(url, context=ctx) as response, open(zip_path, 'wb') as out_file:
                total_size = int(response.info().get('Content-Length', -1))
                block_size = 8192
                count = 0
                while True:
                    data = response.read(block_size)
                    if not data:
                        break
                    out_file.write(data)
                    count += 1
                    if total_size > 0:
                        percent = min((count * block_size * 100) / total_size, 100)
                        self.after(0, self.update_progress, percent / 100.0, f"Downloading ffmpeg: {int(percent)}%")
            
            self.after(0, self.update_progress, 1.0, "Extracting ffmpeg...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(app_dir)
                
            os.remove(zip_path)
            os.chmod(local_ffmpeg, 0o755)
            
            self.ffmpeg_path = local_ffmpeg
            self.after(0, self.ffmpeg_download_complete)
        except Exception as e:
            self.after(0, self.show_error, f"Failed to download ffmpeg: {str(e)}")

    def ffmpeg_download_complete(self):
        self.status_label.configure(text="Ready", text_color="black")
        self.fetch_btn.configure(state="normal")
        self.progress_bar.set(0)

    def setup_ui(self):
        # Title
        self.title_label = ctk.CTkLabel(self, text="YouTube Downloader v1.1.0", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)

        # URL Input
        self.url_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.url_frame.pack(padx=20, pady=10, fill="x")
        
        self.url_entry = ctk.CTkEntry(self.url_frame, placeholder_text="請貼上連結", height=40)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.url_entry.bind("<Return>", lambda e: self.on_fetch_clicked())
        
        self.fetch_btn = ctk.CTkButton(self.url_frame, text="Fetch Info", command=self.on_fetch_clicked, width=100, height=40)
        self.fetch_btn.pack(side="right")

        # Thumbnail
        self.thumbnail_label = ctk.CTkLabel(self, text="Thumbnail Preview", width=400, height=225, fg_color="gray30", corner_radius=8)
        self.thumbnail_label.pack(pady=10)
        
        self.video_title_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14), wraplength=500)
        self.video_title_label.pack(pady=(0, 10))

        # Options Frame
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(padx=20, pady=10, fill="x")

        # Download Type
        self.type_label = ctk.CTkLabel(self.options_frame, text="Download Type:", font=ctk.CTkFont(weight="bold"))
        self.type_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.download_type_var = ctk.StringVar(value="video")
        
        self.radio_video = ctk.CTkRadioButton(self.options_frame, text="Video (MP4)", variable=self.download_type_var, value="video", command=self.on_type_changed)
        self.radio_video.grid(row=0, column=1, padx=10, pady=10)
        
        self.radio_audio = ctk.CTkRadioButton(self.options_frame, text="Audio Only (WAV)", variable=self.download_type_var, value="audio", command=self.on_type_changed)
        self.radio_audio.grid(row=0, column=2, padx=10, pady=10)

        # Quality
        self.quality_label = ctk.CTkLabel(self.options_frame, text="Video Quality:", font=ctk.CTkFont(weight="bold"))
        self.quality_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        self.quality_var = ctk.StringVar(value="")
        self.quality_dropdown = ctk.CTkOptionMenu(self.options_frame, variable=self.quality_var, values=["---"])
        self.quality_dropdown.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="w")
        
        self.quality_dropdown.configure(state="disabled")
        
        # Download Button
        self.download_btn = ctk.CTkButton(self, text="Download", command=self.on_download_clicked, height=50, font=ctk.CTkFont(size=16, weight="bold"))
        self.download_btn.pack(padx=20, pady=20, fill="x")
        self.download_btn.configure(state="disabled")

        # Progress
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(padx=20, pady=5, fill="x")
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self, text="Ready", text_color="black")
        self.status_label.pack(pady=5)

        self.footer_label = ctk.CTkLabel(self, text="蘇廷融製作", font=ctk.CTkFont(size=12), text_color="gray")
        self.footer_label.pack(side="bottom", pady=(0, 10))

    def on_type_changed(self):
        if self.download_type_var.get() == "audio":
            self.quality_dropdown.configure(state="disabled")
        else:
            if self.video_info:
                self.quality_dropdown.configure(state="normal")

    def on_fetch_clicked(self):
        url = self.url_entry.get().strip()
        if not url:
            self.status_label.configure(text="Please enter a valid URL.", text_color="red")
            return
        
        self.fetch_btn.configure(state="disabled")
        self.download_btn.configure(state="disabled")
        self.status_label.configure(text="Fetching video info...", text_color="black")
        
        # Run in a thread to prevent freezing
        threading.Thread(target=self.fetch_video_info, args=(url,), daemon=True).start()

    def fetch_video_info(self, url):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'socket_timeout': 60
        }
        if os.path.exists('/opt/homebrew/bin/node'):
            ydl_opts['js_runtimes'] = {'node': {'path': '/opt/homebrew/bin/node'}}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
            self.video_info = info
            
            # Extract resolutions
            resolutions = set()
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('height'):
                    resolutions.add(f['height'])
            
            self.available_resolutions = sorted(list(resolutions), reverse=True)
            
            # Determine best resolution
            if self.available_resolutions:
                self.best_resolution = f"{self.available_resolutions[0]}p"
            else:
                self.best_resolution = "Best"

            # Fetch Thumbnail
            thumb_url = info.get('thumbnail')
            if thumb_url:
                response = requests.get(thumb_url)
                img_data = response.content
                img = Image.open(BytesIO(img_data))
                # Resize keeping aspect ratio
                img.thumbnail((400, 225))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                
                # Update UI in main thread
                self.after(0, self.update_thumbnail, ctk_img, info.get('title', 'Unknown Title'))
            
            self.after(0, self.update_quality_dropdown)
            
        except Exception as e:
            self.after(0, self.show_error, f"Failed to fetch info: {str(e)}")

    def update_thumbnail(self, img, title):
        self.thumbnail_label.configure(image=img, text="")
        self.video_title_label.configure(text=title)

    def update_quality_dropdown(self):
        res_strings = [f"{r}p" for r in self.available_resolutions]
        if not res_strings:
            res_strings = ["Best"]
        
        # Recommend the best resolution by default
        recommended = res_strings[0]
        self.quality_dropdown.configure(values=res_strings, state="normal")
        self.quality_var.set(f"{recommended} (Recommended)")
        
        self.status_label.configure(text="Video info loaded successfully.", text_color="green")
        self.fetch_btn.configure(state="normal")
        self.download_btn.configure(state="normal")
        self.on_type_changed()

    def show_error(self, message):
        self.status_label.configure(text=message, text_color="red")
        self.fetch_btn.configure(state="normal")

    def on_download_clicked(self):
        if self.is_downloading:
            return
            
        url = self.url_entry.get().strip()
        dtype = self.download_type_var.get()
        quality_str = self.quality_var.get().replace(" (Recommended)", "")
        
        # Save to Downloads folder
        download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        
        ffmpeg_path = getattr(self, "ffmpeg_path", None)

        
        ydl_opts = {
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.download_progress_hook],
            'noplaylist': True,
            'overwrites': True,
            'nocheckcertificate': True,
            'socket_timeout': 60,
        }
        
        if os.path.exists('/opt/homebrew/bin/node'):
            ydl_opts['js_runtimes'] = {'node': {'path': '/opt/homebrew/bin/node'}}
            
        if ffmpeg_path:
            ydl_opts['ffmpeg_location'] = ffmpeg_path
        
        if dtype == "audio":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }]
        else:
            if quality_str and quality_str != "Best":
                height = int(quality_str.replace("p", ""))
                # Strictly prefer mp4 (H.264/avc1) video and m4a (aac) audio for QuickTime compatibility
                ydl_opts['format'] = f'bestvideo[ext=mp4][vcodec^=avc1][height<={height}]+bestaudio[ext=m4a]/bestvideo[ext=mp4][vcodec^=avc1][height<={height}]+bestaudio/best[ext=mp4]/best'
            else:
                ydl_opts['format'] = 'bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/bestvideo[ext=mp4][vcodec^=avc1]+bestaudio/best[ext=mp4]/best'
                
            ydl_opts['merge_output_format'] = 'mp4'

        self.is_downloading = True
        self.download_btn.configure(state="disabled", text="Downloading...")
        self.status_label.configure(text="Starting download...", text_color="black")
        self.progress_bar.set(0)
        
        threading.Thread(target=self.start_download, args=(ydl_opts, url, dtype, ffmpeg_path), daemon=True).start()

    def start_download(self, ydl_opts, url, dtype, ffmpeg_path):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.after(0, self.download_finished)
        except Exception as e:
            self.after(0, self.show_error, f"Download failed: {str(e)}")
            self.after(0, self.reset_download_state)

    def download_progress_hook(self, d):
        if d['status'] == 'downloading':
            percent_str = d.get('_percent_str', '0%')
            # Clean ansi escape characters from yt-dlp output
            percent_str = re.sub(r'\x1b\[[0-9;]*m', '', percent_str)
            percent_str = percent_str.strip().replace('%', '')
            try:
                percent = float(percent_str) / 100.0
                self.after(0, self.update_progress, percent, f"Downloading: {percent_str}%")
            except:
                pass
        elif d['status'] == 'finished':
            self.after(0, self.update_progress, 1.0, "Processing file...")

    def update_progress(self, percent, text):
        self.progress_bar.set(percent)
        self.status_label.configure(text=text, text_color="black")

    def download_finished(self):
        self.status_label.configure(text="Download Complete! Saved to Downloads folder.", text_color="green")
        self.reset_download_state()

    def reset_download_state(self):
        self.is_downloading = False
        self.download_btn.configure(state="normal", text="Download")
        self.progress_bar.set(0)

if __name__ == "__main__":
    app = App()
    app.mainloop()
