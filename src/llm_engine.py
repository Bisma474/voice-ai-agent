"""
Language Model Engine component for Voice AI Agent.
Integrates with llama.cpp or fallback engine for local LLM inference.
"""

import json
from typing import List, Dict, Any, Optional
from src.exceptions import LLMEngineError



class LLMEngine:
    """Manages text generation using llama.cpp or fallback engine."""

    def __init__(self, model_path: Optional[str] = None, context_length: int = 2048):
        """Initialize LLM engine with model.

        Args:
            model_path: Path to GGUF model file
            context_length: Context window size in tokens
        """
        self._model_path = model_path
        self._context_length = context_length
        self._is_loaded = True if model_path else False
        self._tools: Dict[str, Any] = {}

        # Generation parameters
        self.temperature: float = 0.7
        self.top_p: float = 0.9
        self.max_tokens: int = 300
        self.repeat_penalty: float = 1.1
        self.system_prompt: str = (
            "You are a helpful Voice AI Assistant. "
            "Give short, complete answers in 2 to 4 sentences maximum. "
            "Never leave an answer unfinished. "
            "IMPORTANT: Never use markdown formatting. No asterisks, no bold, no bullet points, "
            "no headers, no backticks. Write in plain natural sentences only."
        )


    def generate(self, prompt: str, context: Optional[List[Dict[str, Any]]] = None) -> str:
        """Generate text response from prompt and optional conversation history context.

        Args:
            prompt: User query or prompt string
            context: List of message dicts (e.g. [{'role': 'user', 'content': 'hi'}])

        Returns:
            Generated response string
        """
        if not self._is_loaded and self._model_path:
            raise LLMEngineError("LLM model is unloaded. Load model before generation.")

        prompt_lower = (prompt or "").lower()
        import datetime



        import os
        import urllib.request
        import re
        import datetime

        groq_key   = os.environ.get("GROQ_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")
        gemini_key = os.environ.get("GEMINI_API_KEY")

        # ── 1. Groq (primary) ─ llama-3.3-70b-versatile, fast & generous free tier ──
        if groq_key:
            try:
                payload = json.dumps({
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user",   "content": prompt}
                    ],
                    "temperature": self.temperature,
                    "max_tokens":  self.max_tokens
                }).encode('utf-8')
                req = urllib.request.Request(
                    "https://api.groq.com/openai/v1/chat/completions",
                    data=payload,
                    headers={
                        "Authorization": f"Bearer {groq_key}",
                        "Content-Type":  "application/json",
                        "User-Agent":    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                    }
                )
                with urllib.request.urlopen(req, timeout=10.0) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    return data['choices'][0]['message']['content'].strip()
            except Exception as e:
                print(f"[Groq] error: {e} — trying Gemini fallback")

        # ── 2. Gemini 2.0-flash (fallback) ──────────────────────────────────────────
        if gemini_key:
            try:
                payload = json.dumps({
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": self.temperature,
                        "maxOutputTokens": self.max_tokens
                    },
                    "systemInstruction": {
                        "parts": [{"text": self.system_prompt}]
                    }
                }).encode('utf-8')
                url = (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"gemini-2.5-flash:generateContent?key={gemini_key}"
                )
                req = urllib.request.Request(
                    url, data=payload,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=10.0) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    return data['candidates'][0]['content']['parts'][0]['text'].strip()
            except Exception as e:
                print(f"[Gemini] error: {e} — using local fallback")

        # ── 3. OpenAI (optional third fallback) ────────────────────────────────────
        if openai_key:
            try:
                payload = json.dumps({
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}]
                }).encode('utf-8')
                req = urllib.request.Request(
                    "https://api.openai.com/v1/chat/completions",
                    data=payload,
                    headers={
                        "Authorization": f"Bearer {openai_key}",
                        "Content-Type":  "application/json"
                    }
                )
                with urllib.request.urlopen(req, timeout=10.0) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    return data['choices'][0]['message']['content'].strip()
            except Exception:
                pass

        # ── 4. Tool intent matching (offline only) ──────────────────────────────────
        for tool_name, tool in self._tools.items():
            if tool_name.lower() in prompt_lower or getattr(tool, 'description', '').lower() in prompt_lower:
                return f"[TOOL_CALL:{tool_name}]"

        # ── 5. Fast local shortcuts (offline safety net) ───────────────────────────
        if "weather" in prompt_lower or "forecast" in prompt_lower:
            return "I don't have any weather info right now."
        if "time" in prompt_lower or "clock" in prompt_lower:
            return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."
        if "date" in prompt_lower or "what day" in prompt_lower:
            return f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}."
        if any(w in prompt_lower.split() for w in ["hello", "hi", "hey"]):
            return "Hello! How can I assist you today?"
        math_match = re.search(r'(\d+\s*[\+\-\*\/\^]\s*\d+)', prompt)
        if math_match:
            try:
                expr = math_match.group(1).replace('^', '**')
                return f"The result of {math_match.group(1)} is {eval(expr)}."
            except Exception:
                pass

        return "I'm having trouble reaching the AI service right now. Please check your internet connection."






    def set_parameters(self, **kwargs) -> None:
        """Set generation parameters (temperature, top_p, max_tokens, repeat_penalty, system_prompt).

        Args:
            **kwargs: Generation parameter key-value pairs
        """
        if 'temperature' in kwargs:
            self.temperature = float(kwargs['temperature'])
        if 'top_p' in kwargs:
            self.top_p = float(kwargs['top_p'])
        if 'max_tokens' in kwargs:
            self.max_tokens = int(kwargs['max_tokens'])
        if 'repeat_penalty' in kwargs:
            self.repeat_penalty = float(kwargs['repeat_penalty'])
        if 'system_prompt' in kwargs:
            self.system_prompt = str(kwargs['system_prompt'])

    def load_model(self, model_path: str) -> bool:
        """Load language model from file path.

        Args:
            model_path: Path to GGUF model file

        Returns:
            True if loaded successfully
        """
        if not model_path:
            raise ValueError("Model path cannot be empty")
        self._model_path = model_path
        self._is_loaded = True
        return True

    def unload_model(self) -> None:
        """Unload model to free memory."""
        self._is_loaded = False

    def get_token_count(self, text: str) -> int:
        """Get approximate token count for text.

        Args:
            text: Input string

        Returns:
            Estimated number of tokens
        """
        if not text:
            return 0
        # Simple word/subword approximation: ~4 chars per token
        return max(1, len(text) // 4)

    def register_tool(self, tool: Any) -> None:
        """Register a tool for intent detection.

        Args:
            tool: BaseTool instance
        """
        tool_name = getattr(tool, 'name', str(tool))
        self._tools[tool_name] = tool
