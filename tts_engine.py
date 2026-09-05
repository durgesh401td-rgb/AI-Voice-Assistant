import os
import asyncio
import edge_tts
import tempfile
import ctypes
import subprocess
from typing import Optional
from config import DEFAULT_VOICE, DEFAULT_VOICE_RATE, DEFAULT_VOICE_PITCH

class TTSEngine:
    def __init__(self, voice: str = DEFAULT_VOICE):
        self.voice = voice

    async def generate_audio_file(self, text: str, output_path: Optional[str] = None) -> str:
        """Generates realistic neural audio using edge-tts."""
        if not output_path:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            output_path = tmp.name
            tmp.close()

        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.voice,
                rate=DEFAULT_VOICE_RATE,
                pitch=DEFAULT_VOICE_PITCH
            )
            await communicate.save(output_path)
            return output_path
        except Exception as e:
            print(f"[TTS Error]: {e}")
            return ""

    def play_audio_file(self, file_path: str):
        """Plays MP3 audio using Windows native Multimedia DLL (Zero extra libraries needed)."""
        try:
            mci = ctypes.windll.winmm.mciSendStringW
            mci('close all', None, 0, None)
            mci(f'open "{file_path}" type mpegvideo alias mp3sound', None, 0, None)
            mci('play mp3sound wait', None, 0, None)
            mci('close mp3sound', None, 0, None)
        except Exception as e:
            # Fallback to Windows Media Player PowerShell command
            cmd = f'powershell -c "(New-Object Media.SoundPlayer \'{file_path}\').PlaySync()"'
            subprocess.run(cmd, shell=True)

    def speak_locally(self, text: str):
        """Speaks text immediately using Windows SAPI / edge-tts."""
        try:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tmp_path = tmp.name
            tmp.close()

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.generate_audio_file(text, tmp_path))
            loop.close()

            if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
                self.play_audio_file(tmp_path)
                try:
                    os.remove(tmp_path)
                except:
                    pass
        except Exception as e:
            # Windows native built-in SAPI fallback
            clean_text = text.replace('"', '').replace("'", "")
            subprocess.run(f'powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{clean_text}\')"', shell=True)