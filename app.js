let ws;
let recognition;
let isRecording = false;

const orb = document.getElementById("orb");
const transcriptDisplay = document.getElementById("transcript");
const micBtn = document.getElementById("micBtn");
const textInput = document.getElementById("textInput");
const sendBtn = document.getElementById("sendBtn");
const consoleBody = document.getElementById("consoleBody");
const audioPlayer = document.getElementById("audioPlayer");
const apiKeyInput = document.getElementById("apiKeyInput");
const voiceSelect = document.getElementById("voiceSelect");
const saveConfigBtn = document.getElementById("saveConfigBtn");

// Connect WebSocket
function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleServerMessage(data);
    };

    ws.onclose = () => {
        addLog("system", "WebSocket disconnected. Reconnecting in 2 seconds...");
        setTimeout(connectWebSocket, 2000);
    };
}

// Add logs to console
function addLog(type, content) {
    const logEl = document.createElement("div");
    logEl.className = `log-item ${type}`;
    logEl.textContent = `[${new Date().toLocaleTimeString()}] ${content}`;
    consoleBody.appendChild(logEl);
    consoleBody.scrollTop = consoleBody.scrollHeight;
}

// Handle messages from the AI backend
function handleServerMessage(data) {
    if (data.type === "status") {
        transcriptDisplay.textContent = data.content;
    } else if (data.type === "thought" || data.type === "tool_call" || data.type === "tool_result" || data.type === "response" || data.type === "error") {
        addLog(data.type, data.content);
    } else if (data.type === "audio_response") {
        transcriptDisplay.textContent = data.text;
        addLog("response", `Aura: ${data.text}`);

        // Play voice audio
        if (data.audio_url) {
            audioPlayer.src = data.audio_url;
            orb.classList.remove("listening");
            orb.classList.add("speaking");
            audioPlayer.play();
        }
    }
}

audioPlayer.onended = () => {
    orb.classList.remove("speaking");
};

// Speech Recognition setup (Web Speech API)
function setupSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        addLog("error", "Web Speech API is not supported in this browser. Please use Chrome/Edge or type your commands.");
        return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
        isRecording = true;
        micBtn.classList.add("active");
        orb.classList.add("listening");
        transcriptDisplay.textContent = "Listening to your voice...";
    };

    recognition.onresult = (event) => {
        let currentTranscript = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
            currentTranscript += event.results[i][0].transcript;
        }
        transcriptDisplay.textContent = currentTranscript;

        if (event.results[0].isFinal) {
            sendCommand(currentTranscript);
        }
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        stopRecording();
    };

    recognition.onend = () => {
        stopRecording();
    };
}

function startRecording() {
    if (recognition && !isRecording) {
        audioPlayer.pause();
        recognition.start();
    }
}

function stopRecording() {
    isRecording = false;
    micBtn.classList.remove("active");
    orb.classList.remove("listening");
}

function sendCommand(text) {
    if (!text || !text.trim()) return;
    addLog("system", `User Voice Command: "${text}"`);
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ text: text }));
    }
}

// Event Listeners
micBtn.addEventListener("click", () => {
    if (isRecording) {
        recognition.stop();
    } else {
        startRecording();
    }
});

sendBtn.addEventListener("click", () => {
    const val = textInput.value.trim();
    if (val) {
        transcriptDisplay.textContent = val;
        sendCommand(val);
        textInput.value = "";
    }
});

textInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        sendBtn.click();
    }
});

// Spacebar push-to-talk
window.addEventListener("keydown", (e) => {
    if (e.code === "Space" && document.activeElement !== textInput && document.activeElement !== apiKeyInput) {
        e.preventDefault();
        if (!isRecording) startRecording();
    }
});

saveConfigBtn.addEventListener("click", async () => {
    const key = apiKeyInput.value.trim();
    const voice = voiceSelect.value;
    await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: key, voice: voice })
    });
    addLog("system", `Configuration saved (Voice: ${voice}).`);
});

document.getElementById("clearLogsBtn").addEventListener("click", () => {
    consoleBody.innerHTML = "";
});

// Init
setupSpeechRecognition();
connectWebSocket();