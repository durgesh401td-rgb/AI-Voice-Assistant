import os
import sys
import threading
import asyncio
import math
import time
import tempfile
import subprocess
import customtkinter as ctk

# pyrefly: ignore [missing-import]
from agent import VoiceAgent
from tts_engine import TTSEngine
from config import GEMINI_API_KEY, DEFAULT_VOICE

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class WindowsVoiceAssistantUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AURA // Windows Voice AI Assistant")
        self.geometry("900x720")
        self.minsize(800, 600)
        self.configure(fg_color="#0b0f19")

        self.agent = VoiceAgent()
        self.tts = TTSEngine(voice=DEFAULT_VOICE)
        self.is_recording = False
        self.is_speaking = False

        self.create_widgets()

        self.visualizer_phase = 0
        self.animate_visualizer()

        threading.Thread(target=self.startup_greeting, daemon=True).start()

    def create_widgets(self):
        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="#121826", corner_radius=12, height=60)
        self.header_frame.pack(fill="x", padx=16, pady=(16, 8))

        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="⚡ AURA // AUTONOMOUS AI", 
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#00e5ff"
        )
        self.title_label.pack(side="left", padx=16, pady=12)

        self.api_key_entry = ctk.CTkEntry(
            self.header_frame, 
            placeholder_text="Enter Gemini API Key...", 
            width=240, 
            show="*",
            fg_color="#080c14",
            border_color="#1e293b"
        )
        if GEMINI_API_KEY:
            self.api_key_entry.insert(0, GEMINI_API_KEY)
        self.api_key_entry.pack(side="right", padx=(8, 16), pady=12)

        self.save_key_btn = ctk.CTkButton(
            self.header_frame, 
            text="Save Key", 
            width=80, 
            fg_color="#00e5ff", 
            text_color="#000",
            hover_color="#00b4d8",
            command=self.save_api_key
        )
        self.save_key_btn.pack(side="right", padx=4, pady=12)

        # Visualizer & Transcript Area
        self.vis_frame = ctk.CTkFrame(self, fg_color="#121826", corner_radius=16)
        self.vis_frame.pack(fill="both", expand=True, padx=16, pady=8)

        self.canvas = ctk.CTkCanvas(self.vis_frame, width=700, height=180, bg="#121826", highlightthickness=0)
        self.canvas.pack(pady=(20, 10))

        self.transcript_label = ctk.CTkLabel(
            self.vis_frame,
            text="Click 'Voice Command' or type any task below...",
            font=ctk.CTkFont(family="Segoe UI", size=15),
            text_color="#e0e6ed",
            wraplength=750
        )
        self.transcript_label.pack(pady=(0, 16), padx=20)

        # Control Bar
        self.controls_frame = ctk.CTkFrame(self.vis_frame, fg_color="transparent")
        self.controls_frame.pack(fill="x", padx=20, pady=(0, 16))

        self.mic_btn = ctk.CTkButton(
            self.controls_frame,
            text="🎤 Voice Command",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=46,
            width=160,
            fg_color="#00e5ff",
            text_color="#000",
            hover_color="#ff0055",
            command=self.trigger_voice_input
        )
        self.mic_btn.pack(side="left", padx=(0, 10))

        self.text_entry = ctk.CTkEntry(
            self.controls_frame,
            placeholder_text="Type any task (e.g. 'Open Chrome and search NASA', 'Check CPU usage', 'Create notes.txt')...",
            height=46,
            fg_color="#080c14",
            border_color="#1e293b",
            font=ctk.CTkFont(size=13)
        )
        self.text_entry.pack(side="left", fill="x", expand=True, padx=6)
        self.text_entry.bind("<Return>", lambda e: self.send_text_command())

        self.send_btn = ctk.CTkButton(
            self.controls_frame,
            text="Execute",
            width=90,
            height=46,
            fg_color="#7c4dff",
            hover_color="#651fff",
            command=self.send_text_command
        )
        self.send_btn.pack(side="right", padx=(6, 0))

        # Log Console
        self.log_frame = ctk.CTkFrame(self, fg_color="#080c14", corner_radius=12, height=180)
        self.log_frame.pack(fill="x", padx=16, pady=(4, 16))

        self.log_header = ctk.CTkLabel(
            self.log_frame,
            text="SYSTEM EXECUTION FEED // LIVE ACTIONS",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#8892b0"
        )
        self.log_header.pack(anchor="w", padx=12, pady=(8, 2))

        self.log_textbox = ctk.CTkTextbox(
            self.log_frame,
            fg_color="#080c14",
            text_color="#b9f6ca",
            font=ctk.CTkFont(family="Consolas", size=12),
            height=130
        )
        self.log_textbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.log_textbox.insert("end", "[SYSTEM] Aura Windows Assistant ready.\n")

    def log_message(self, message_type: str, text: str):
        def _update():
            timestamp = time.strftime("%H:%M:%S")
            self.log_textbox.insert("end", f"[{timestamp}] [{message_type.upper()}] {text}\n")
            self.log_textbox.see("end")
        self.after(0, _update)

    def set_transcript(self, text: str):
        self.after(0, lambda: self.transcript_label.configure(text=text))

    def save_api_key(self):
        key = self.api_key_entry.get().strip()
        if key:
            self.agent.set_api_key(key)
            self.log_message("SYSTEM", "Gemini API key updated.")

    def animate_visualizer(self):
        self.canvas.delete("all")
        width, height = 700, 180
        center_y = height // 2
        # pyrefly: ignore [bad-assignment]
        self.visualizer_phase += 0.08
        points = []

        if self.is_recording:
            amplitude, color = 45, "#ff0055"
        elif self.is_speaking:
            amplitude, color = 35 + 15 * math.sin(self.visualizer_phase * 2), "#00e5ff"
        else:
            amplitude, color = 10, "#7c4dff"

        for x in range(0, width, 6):
            y = center_y + amplitude * math.sin((x * 0.03) + self.visualizer_phase) * math.cos((x * 0.01) + self.visualizer_phase)
            points.append((x, y))

        for i in range(len(points) - 1):
            self.canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill=color, width=3, smooth=True)

        orb_r = 18 + (10 if (self.is_recording or self.is_speaking) else 0)
        self.canvas.create_oval(width//2 - orb_r, center_y - orb_r, width//2 + orb_r, center_y + orb_r, fill=color, outline="")

        self.after(30, self.animate_visualizer)

    def trigger_voice_input(self):
        """Native Windows Speech Recognition fallback using Windows PowerShell Speech API."""
        def _listen():
            self.is_recording = True
            self.mic_btn.configure(fg_color="#ff0055", text="🔴 Listening...")
            self.set_transcript("Listening via Windows Speech...")

            # PowerShell command that triggers Windows Speech Recognizer
            ps_script = """
            Add-Type -AssemblyName System.Speech;
            $rec = New-Object System.Speech.Recognition.SpeechRecognitionEngine;
            $rec.SetInputToDefaultAudioDevice();
            $grammar = New-Object System.Speech.Recognition.DictationGrammar;
            $rec.LoadGrammar($grammar);
            $result = $rec.Recognize([TimeSpan]::FromSeconds(8));
            if ($result) { $result.Text }
            """
            try:
                proc = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True, timeout=12)
                user_text = proc.stdout.strip()
                if user_text:
                    self.set_transcript(f"\"{user_text}\"")
                    self.log_message("USER_VOICE", user_text)
                    self.process_command(user_text)
                else:
                    self.set_transcript("No speech detected. You can also type commands.")
            except Exception as e:
                self.log_message("ERROR", f"Voice capture: {e}")
                self.set_transcript("Voice capture timed out. Type in command bar.")
            finally:
                self.is_recording = False
                self.mic_btn.configure(fg_color="#00e5ff", text="🎤 Voice Command")

        threading.Thread(target=_listen, daemon=True).start()

    def send_text_command(self):
        text = self.text_entry.get().strip()
        if text:
            self.text_entry.delete(0, "end")
            self.set_transcript(f"\"{text}\"")
            self.log_message("USER_TEXT", text)
            threading.Thread(target=self.process_command, args=(text,), daemon=True).start()

    def process_command(self, command: str):
        try:
            async def log_cb(log_type, msg):
                self.log_message(log_type, msg)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(self.agent.run_agent_step(command, on_log_callback=log_cb))

            self.set_transcript(response)
            self.log_message("RESPONSE", response)

            # Speak response back using native Windows audio
            self.is_speaking = True
            audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
            loop.run_until_complete(self.tts.generate_audio_file(response, audio_file))
            loop.close()

            if os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
                # pyrefly: ignore [missing-attribute]
                self.tts.play_audio_file(audio_file)
                try:
                    os.remove(audio_file)
                except:
                    pass

        except Exception as e:
            self.log_message("ERROR", str(e))
        finally:
            self.is_speaking = False

    def startup_greeting(self):
        time.sleep(0.5)
        self.tts.speak_locally("Aura Windows Assistant is ready.")

if __name__ == "__main__":
    app = WindowsVoiceAssistantUI()
    app.mainloop()
