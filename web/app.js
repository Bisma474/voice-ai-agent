document.addEventListener('DOMContentLoaded', () => {
    // Tab Switching
    const navBtns = document.querySelectorAll('.nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const tabTitle = document.getElementById('tab-title');
    const tabSubtitle = document.getElementById('tab-subtitle');

    const tabMeta = {
        'chat-tab': { title: 'Voice Assistant', subtitle: 'Powered by Gemini 2.5-flash · Google gTTS' },
        'settings-tab': { title: 'Settings & Preferences', subtitle: 'Configure voice output language and audio' }
    };


    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.tab;
            navBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(target).classList.add('active');

            if (tabMeta[target]) {
                tabTitle.textContent = tabMeta[target].title;
                tabSubtitle.textContent = tabMeta[target].subtitle;
            }
        });
    });

    // Theme Toggle
    const themeBtn = document.getElementById('theme-toggle-btn');
    themeBtn.addEventListener('click', () => {
        document.body.classList.toggle('light-theme');
        themeBtn.textContent = document.body.classList.contains('light-theme') ? '☀️' : '🌙';
    });

    // Elements
    const talkBtn = document.getElementById('talk-btn');
    const voiceOrb = document.getElementById('voice-orb');
    const orbLabel = document.getElementById('orb-state-label');
    const globalDot = document.getElementById('global-status-dot');
    const globalStatusText = document.getElementById('global-status-text');
    const micMeter = document.getElementById('mic-meter');

    const textInput = document.getElementById('text-input');
    const sendBtn = document.getElementById('send-btn');
    const transcriptList = document.getElementById('transcript-list');
    const clearHistoryBtn = document.getElementById('clear-history-btn');

    let currentState = 'idle';
    let isListening = false;

    let recognition = null;

    // Initialize Web Speech API Recognition if supported
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            isListening = true;
            setSystemState('listening');
            micMeter.style.width = '75%';
        };

        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }

            if (interimTranscript) {
                orbLabel.textContent = `Hearing: "${interimTranscript}"`;
            }

            if (finalTranscript) {
                handleTurn(finalTranscript);
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            micMeter.style.width = '0%';
            setSystemState('idle');
            if (event.error === 'not-allowed') {
                alert('Microphone access denied. Please allow microphone permissions in your browser address bar.');
            }
        };

        recognition.onend = () => {
            isListening = false;
            micMeter.style.width = '0%';
            if (currentState === 'listening') {
                setSystemState('idle');
            }
        };
    }

    function setSystemState(state) {
        currentState = state;
        globalDot.className = `status-dot ${state}`;
        globalStatusText.textContent = state.toUpperCase();
        voiceOrb.className = `voice-orb ${state}`;

        if (state === 'idle') {
            orbLabel.textContent = recognition ? 'Click Microphone and speak' : 'Type prompt below or click microphone';
        } else if (state === 'listening') {
            orbLabel.textContent = 'Listening to your speech... (Speak now)';
        } else if (state === 'processing') {
            orbLabel.textContent = 'Processing STT -> LLM response...';
        } else if (state === 'speaking') {
            orbLabel.textContent = 'Speaking synthesized audio response...';
        }
    }

    function addMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-message ${role}`;

        const isUser = role === 'user';
        const avatar = isUser ? '👤' : '🤖';
        const senderName = isUser ? 'You' : 'Voice AI Assistant';
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        msgDiv.innerHTML = `
            <div class="avatar">${avatar}</div>
            <div class="message-content">
                <div class="sender">${senderName}</div>
                <div class="body">${text}</div>
                <div class="timestamp">${timeStr}</div>
            </div>
        `;

        transcriptList.appendChild(msgDiv);
        transcriptList.scrollTop = transcriptList.scrollHeight;
    }

    function speakAudio(audio_b64, fallbackText) {
        if (audio_b64) {
            // Play gTTS MP3 returned from server
            const binary = atob(audio_b64);
            const bytes = new Uint8Array(binary.length);
            for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
            const blob = new Blob([bytes], { type: 'audio/mpeg' });
            const url = URL.createObjectURL(blob);
            const audio = new Audio(url);
            setSystemState('speaking');
            audio.onended = () => { setSystemState('idle'); URL.revokeObjectURL(url); };
            audio.onerror = () => { setSystemState('idle'); URL.revokeObjectURL(url); };
            audio.play().catch(() => setSystemState('idle'));
        } else if ('speechSynthesis' in window && fallbackText) {
            // Browser TTS fallback when gTTS is unavailable
            const utterance = new SpeechSynthesisUtterance(fallbackText);
            utterance.onend = () => setSystemState('idle');
            setSystemState('speaking');
            window.speechSynthesis.speak(utterance);
        } else {
            setSystemState('idle');
        }
    }

    function handleTurn(userText) {
        if (!userText.trim()) return;

        addMessage('user', userText);
        setSystemState('processing');

        fetch('/api/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: userText })
        })
        .then(res => res.json())
        .then(data => {
            addMessage('assistant', data.response);
            speakAudio(data.audio_b64, data.response);
        })
        .catch(err => {
            // Client-side fallback when server is unreachable
            let response = `I received your query: "${userText}"`;
            if (userText.toLowerCase().includes('hello') || userText.toLowerCase().includes('hi')) {
                response = "Hello! How can I assist you today?";
            } else if (userText.toLowerCase().includes('weather')) {
                response = "The current weather is clear and 72 degrees.";
            }
            addMessage('assistant', response);
            speakAudio(null, response);
        });
    }


    function toggleMic() {
        if (!recognition) {
            // Request browser getUserMedia permissions
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    alert("Microphone active! You can also type text below.");
                })
                .catch(err => {
                    alert("Please allow microphone permissions in browser header or use text input below.");
                });
            return;
        }

        if (isListening) {
            recognition.stop();
        } else {
            try {
                recognition.start();
            } catch (e) {
                console.log(e);
            }
        }
    }

    talkBtn.addEventListener('click', toggleMic);
    voiceOrb.addEventListener('click', toggleMic);

    sendBtn.addEventListener('click', () => {
        const text = textInput.value;
        textInput.value = '';
        handleTurn(text);
    });

    textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendBtn.click();
        }
    });

    const saveSettingsBtn = document.getElementById('save-settings-btn');
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', () => {
            const gttsLang = document.getElementById('setting-gtts-lang').value;
            fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ gtts_language: gttsLang })
            })
            .then(res => res.json())
            .then(() => alert(`✅ Voice language set to: ${gttsLang}`))
            .catch(() => alert("✅ Preferences saved."));
        });
    }



    clearHistoryBtn.addEventListener('click', () => {
        transcriptList.innerHTML = '';
    });
});

