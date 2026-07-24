"""
Web UI Server for Voice AI Agent.
Serves interactive Web Dashboard UI and API endpoints.
"""

import re

def clean_markdown(text: str) -> str:
    """Strip all markdown formatting so responses are clean plain text."""
    # Bold+italic: ***text*** or **text** or *text*  (non-greedy, no newline crossing)
    text = re.sub(r'\*{3}([^\*\n]+?)\*{3}', r'\1', text)
    text = re.sub(r'\*{2}([^\*\n]+?)\*{2}', r'\1', text)
    text = re.sub(r'\*([^\*\n]+?)\*',        r'\1', text)
    # __bold__ and _italic_
    text = re.sub(r'_{2}([^_\n]+?)_{2}', r'\1', text)
    text = re.sub(r'_([^_\n]+?)_',       r'\1', text)
    # Headings: ## Title → Title
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Inline code: `code`
    text = re.sub(r'`+([^`]+)`+', r'\1', text)
    # Bullet points: lines starting with * - + (with optional leading spaces)
    text = re.sub(r'^\s*[\*\-\+]\s+', '', text, flags=re.MULTILINE)
    # Numbered lists: "1. " "2. " etc.
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    # Blockquotes: > text
    text = re.sub(r'^\s*>\s*', '', text, flags=re.MULTILINE)
    # Horizontal rules --- *** ___
    text = re.sub(r'^[\-\*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Collapse 3+ newlines to 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


import http.server
import socketserver
import json
import os
from pathlib import Path
from src.main import VoiceAIAgent


PORT = int(os.environ.get("PORT", 8000))
WEB_DIR = Path(__file__).parent.parent / "web"


# ── API Keys ──
# Groq is blocked by Cloudflare (error 1010) on this network/IP.
# Key is valid — uncomment below when using a VPN or different network:
# os.environ.setdefault("GROQ_API_KEY", "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")
os.environ.setdefault("GEMINI_API_KEY", "AQ.Ab8RN6IoolpxmonatIpH2hbIq2fxxaKI4bVa7FAb86qRhTGrag")




class VoiceAIHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    agent = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def log_message(self, format, *args):
        # Suppress noisy request logs; keep errors
        pass

    def do_POST(self):
        if self.path == "/api/process":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            query = data.get("query", "")
            if not self.__class__.agent:
                self.__class__.agent = VoiceAIAgent()
                self.__class__.agent.start()

            # Process voice/text turn → get response text
            response_text = self.__class__.agent.process_voice_turn(query.encode('utf-8'))

            # Strip markdown formatting (asterisks, hashes, bullets, etc.)
            response_text = clean_markdown(response_text)


            # Synthesize speech with gTTS → return MP3 as base64
            audio_b64 = ""
            try:
                from gtts import gTTS
                import io
                import base64
                tts = gTTS(text=response_text, lang="en")
                buf = io.BytesIO()
                tts.write_to_fp(buf)
                audio_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            except Exception as e:
                print(f"gTTS error: {e}")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "response": response_text,
                "audio_b64": audio_b64
            }).encode('utf-8'))

        elif self.path == "/api/settings":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            if data.get("groq_api_key"):
                os.environ["GROQ_API_KEY"] = data["groq_api_key"]
            if data.get("openai_api_key"):
                os.environ["OPENAI_API_KEY"] = data["openai_api_key"]
            if data.get("gemini_api_key"):
                os.environ["GEMINI_API_KEY"] = data["gemini_api_key"]
            if data.get("gtts_language"):
                os.environ["GTTS_LANGUAGE"] = data["gtts_language"]

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))

        else:
            self.send_error(404)


def start_web_ui(port: int = PORT):
    """Start local web server serving Voice AI UI."""
    os.chdir(WEB_DIR)
    with socketserver.TCPServer(("", port), VoiceAIHTTPRequestHandler) as httpd:
        print(f"Voice AI Agent UI available at: http://localhost:{port}")
        httpd.serve_forever()


if __name__ == '__main__':
    start_web_ui()
