# AI-Voice-Assistant
Aura is a next-generation, voice-enabled autonomous desktop AI assistant built specifically for Windows. Powered by Google’s Gemini multimodal models and an agentic ReAct loop, Aura acts not just as a conversational chatbot, but as an active operator of your operating system. (Under Development)

# ⚡ AURA // Autonomous Windows Voice AI Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/Python-3.10%20--%203.14%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/AI%20Brain-Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white" alt="Gemini AI">
  <img src="https://img.shields.io/badge/UI-CustomTkinter%20Dark-00e5ff?style=for-the-badge" alt="CustomTkinter">
  <img src="https://img.shields.io/badge/Voice%20TTS-Neural%20Edge--TTS-00E676?style=for-the-badge" alt="Edge TTS">
</p>

An intelligent, voice-first autonomous desktop assistant for Windows. **Aura** listens to your voice commands, reasons through complex multi-step instructions, executes tasks directly on your PC and the web, and speaks back responses in real-time.

---

## 🌟 Key Features

- 🎙️ **Voice Command & Audio Response**: Speak commands naturally and receive ultra-realistic neural voice answers.
- 🧠 **Autonomous Task Execution**: Powered by Gemini function calling with an agentic ReAct loop to decompose and execute complex workflows.
- 💻 **OS & System Automation**:
  - Launch applications (Chrome, VS Code, Spotify, Calculator, Notepad, etc.).
  - Execute PowerShell and Windows CMD commands.
  - Inspect hardware diagnostics (CPU, RAM, Disk, and Battery usage).
  - Capture desktop screenshots.
- 🌐 **Real-Time Web Research**: Perform live web searches and synthesize summaries from across the internet.
- 📁 **File Management**: Create, read, edit, search, and organize files and folders.
- ⚡ **Python Code Interpreter**: Write and execute Python scripts dynamically in a sandboxed subprocess.
- 🖥️ **Futuristic Desktop HUD**: Modern dark-themed GUI with an animated audio visualizer waveform and a live system action console.

---

## 🏗️ System Architecture

```mermaid
graph TD
    User([🎤 User Voice / Text]) --> UI[🖥️ Aura Windows Desktop HUD]
    UI --> STT[🗣️ Windows Speech Recognition]
    STT --> Agent[🧠 Autonomous ReAct Agent Loop]
    
    subgraph Autonomous Tool Suite
        Agent --> Shell[💻 PowerShell & System Control]
        Agent --> Apps[🚀 Desktop App Launcher]
        Agent --> Web[🌐 Live Web Search & Scraping]
        Agent --> Files[📁 File System Manager]
        Agent --> REPL[⚡ Dynamic Python Interpreter]
        Agent --> Screen[📸 Screenshot Capture]
    end
    
    Shell --> ToolResults[Action Results]
    Apps --> ToolResults
    Web --> ToolResults
    Files --> ToolResults
    REPL --> ToolResults
    Screen --> ToolResults
    
    ToolResults --> Agent
    Agent --> TTS[🔊 Neural Audio Synthesis]
    TTS --> Speaker([🔊 Windows Speaker Playback])
    Agent --> UIStream[Live Execution Feed]
    UIStream --> UI


voice_ai_assistant/
│
├── config.py                # Configuration, voice personas & system prompts
├── tools.py                 # Autonomous tool suite (Shell, Files, Web, Apps, REPL)
├── tts_engine.py            # Neural voice synthesizer (edge-tts + Windows MCI)
├── agent.py                 # Core ReAct reasoning & tool-calling engine
├── windows_app.py           # Native Windows Desktop GUI Application
├── requirements.txt         # Project dependencies
└── run_windows_app.bat      # 1-Click Windows launcher script
