# 🎙️ Real-Time Voice AI Agent

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-47%20Passed-brightgreen.svg)](tests/)
[![AI Brain](https://img.shields.io/badge/LLM-Gemini%202.5--flash-orange.svg)](https://aistudio.google.com/)
[![TTS](https://img.shields.io/badge/TTS-Google%20gTTS-red.svg)](https://pypi.org/project/gTTS/)

A full-stack, real-time Voice AI Agent that listens to user speech via microphone, understands intent through Large Language Models, and responds back in natural spoken voice with an interactive Web Dashboard.

---

## 📸 Overview & Features

- **🎙️ Real-Time Speech Recognition (STT)**: Uses browser Web Speech API for low-latency streaming transcription without setup overhead.
- **🧠 Intelligent LLM Routing**: 
  - **Primary**: Google `gemini-2.5-flash` for fast, rich, plain-text conversational answers.
  - **Fallback**: Groq `llama-3.3-70b-versatile` for high-throughput LPU inference.
  - **Offline Safety Net**: Built-in deterministic handlers for date, time, math, and identity.
- **🔊 Multi-Language Text-to-Speech (TTS)**: Powered by Google gTTS (free, unlimited) supporting 8+ output languages including English, Urdu, Arabic, French, German, Spanish, Chinese, and Hindi.
- **💻 Modern Web Dashboard**: Responsive dark-mode dashboard with interactive voice orb, audio meter, live state machine indicators, and manual text fallback.
- **🧪 Comprehensive Test Coverage**: 47 automated tests covering unit, integration, performance benchmarks, and security validation.

---

## 🏗️ System Architecture

```
                               ┌────────────────────────┐
                               │   Browser Web UI       │
                               │ (HTML5/CSS3/JS Web Speech)│
                               └───────────┬────────────┘
                                           │
                              POST /api/process (JSON)
                                           │
                                           ▼
                               ┌────────────────────────┐
                               │  Python HTTP Backend   │
                               │    (src/web_ui.py)     │
                               └───────────┬────────────┘
                                           │
                                           ▼
                               ┌────────────────────────┐
                               │   Voice AI Machine     │
                               │     (src/main.py)      │
                               └───────────┬────────────┘
                                           │
                  ┌────────────────────────┼────────────────────────┐
                  ▼                        ▼                        ▼
       ┌────────────────────┐   ┌────────────────────┐   ┌────────────────────┐
       │   STT Engine       │   │    LLM Engine      │   │    TTS Engine      │
       │ (Browser / UTF-8)  │   │  (Gemini / Groq)   │   │   (Google gTTS)    │
       └────────────────────┘   └────────────────────┘   └────────────────────┘
```

---

## 🔁 Multi-Layer Fallback Strategy

To guarantee maximum uptime and reliability, the agent employs automatic fallback chains at every layer:

```
[ User Input ]
      │
      ▼
┌──────────────┐     Fail     ┌──────────────┐     Fail     ┌──────────────┐
│  Gemini 2.5  │ ───────────► │  Groq Llama  │ ───────────► │ Local Rule   │
│    Flash     │              │    3.3 70B   │              │   Engine     │
└──────────────┘              └──────────────┘              └──────────────┘

┌──────────────┐     Fail     ┌──────────────┐
│  Google gTTS │ ───────────► │ Browser Web  │
│   MP3 Audio  │              │ SpeechSynthesis│
└──────────────┘              └──────────────┘
```

---

## 📁 Repository Structure

```
voice_ai_agent/
├── src/
│   ├── main.py                 # Core VoiceAIAgent controller & state machine
│   ├── llm_engine.py           # LLM router (Gemini 2.5-flash / Groq Llama 3.3 / Local)
│   ├── tts_engine.py           # Text-to-Speech manager using gTTS
│   ├── stt_engine.py           # Speech-to-Text engine abstraction
│   ├── web_ui.py               # Lightweight HTTP server & REST endpoints
│   ├── audio_pipeline.py       # Audio stream management & hardware config
│   ├── wake_word_detector.py   # Wake word detection logic
│   ├── tool_manager.py         # Extensible tool integration framework
│   ├── event_system.py         # Internal pub/sub event bus
│   ├── config.py               # Configuration schema & validation
│   ├── constants.py            # Global constants & default parameters
│   ├── exceptions.py           # Custom exception hierarchy
│   ├── logging_config.py       # Structured logging setup
│   └── utils.py                # Text normalization & helper utilities
├── web/
│   ├── index.html              # Modern Web Dashboard UI
│   ├── style.css               # Vanilla CSS design system
│   └── app.js                  # Frontend logic & Web Speech API integration
├── tests/                      # Full unit & integration test suite (47 tests)
├── requirements.txt            # Project dependencies
├── run_tests.py                # Automated test runner
├── LICENSE                     # MIT License
└── README.md                   # Project documentation
```

---

## ⚙️ Quick Start Guide

### Prerequisites
- Python 3.10 or higher
- Modern web browser (Google Chrome or Microsoft Edge recommended for voice input)
- A free Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/voice-ai-agent.git
cd voice-ai-agent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your_gemini_api_key_here"

# Linux / macOS
export GEMINI_API_KEY="your_gemini_api_key_here"
```

### 4. Run the Server
```bash
python -m src.web_ui
```

### 5. Access the Web Dashboard
Open your browser and navigate to:
```
http://localhost:8000
```

---

## 🎙️ How to Interact

1. **Voice Input**: Click the **Push To Talk** button or click the central voice orb, then speak clearly into your microphone.
2. **Text Input**: Type your question in the text bar and press **Send** or `Enter`.
3. **Voice Output**: The agent will display the answer in plain text and read it aloud using Google gTTS.
4. **Change Spoken Language**: Navigate to **Settings** → **Voice Output Language** to choose between English, Urdu, Arabic, French, German, Spanish, Chinese, or Hindi.

---

## 🔌 REST API Endpoints

### `POST /api/process`
Sends a query to the agent pipeline and receives plain text and audio.

**Request:**
```json
{
  "query": "What is machine learning?"
}
```

**Response:**
```json
{
  "response": "Machine learning is a subset of artificial intelligence that allows systems to learn from data.",
  "audio_b64": "//uQxA..."
}
```

### `POST /api/settings`
Updates runtime settings such as TTS language.

**Request:**
```json
{
  "gtts_language": "ur"
}
```

---

## 🧪 Testing & Quality Assurance

Run all 47 unit and integration tests:

```bash
python run_tests.py
```

Tests cover:
- Text normalization & chunking
- LLM response generation & system prompt compliance
- gTTS audio synthesis & byte buffer handling
- Pipeline latency performance (< 500ms benchmark)
- Security input validation & error recovery

---

## 🛠️ Tech Stack & Dependencies

| Layer | Component | Technology |
|-------|-----------|------------|
| **Frontend** | UI Dashboard | Vanilla HTML5 / CSS3 / JavaScript |
| **STT** | Speech-to-Text | Web Speech API (Chrome / Edge) |
| **LLM (Primary)** | Brain | Google Gemini 2.5-flash |
| **LLM (Fallback)** | Brain | Groq Llama 3.3 70B |
| **TTS** | Speech Synthesis | Google gTTS (`gtts>=2.5.0`) |
| **Backend** | Server | Python `http.server` & `socketserver` |
| **Testing** | QA | Python `unittest` |

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.