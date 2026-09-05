# pyrefly: ignore [missing-import]
import speech_recognition as sr
import asyncio
from agent import VoiceAgent
from tts_engine import TTSEngine

async def main():
    agent = VoiceAgent()
    tts = TTSEngine()
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("\n=======================================================")
    print("      AURA // Autonomous Voice Assistant (CLI Mode)     ")
    print("=======================================================")
    print("Speak into your microphone or press Ctrl+C to exit.\n")

    tts.speak_locally("Aura is online and ready for your commands.")

    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1.0)

    while True:
        try:
            print("\n[🎤 Listening for voice command...]")
            with mic as source:
                audio = recognizer.listen(source, timeout=8, phrase_time_limit=15)

            print("[⏳ Transcribing voice...]")
            text = recognizer.recognize_google(audio)
            print(f"[🗣️ You said]: \"{text}\"")

            if text.lower() in ["exit", "quit", "stop", "shutdown"]:
                tts.speak_locally("Shutting down. Goodbye!")
                break

            print("[🧠 Reasoning and executing tasks...]")
            
            async def log_step(log_type, msg):
                print(f"  [{log_type.upper()}]: {msg}")

            response = await agent.run_agent_step(text, on_log_callback=log_step)
            print(f"\n[Aura]: {response}")
            
            # Speak response back
            tts.speak_locally(response)

        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            print("[❌ Could not understand audio, please speak again]")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"[Error]: {e}")

if __name__ == "__main__":
    asyncio.run(main())