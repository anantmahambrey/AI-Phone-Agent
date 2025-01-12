// transcriber/static/transcriber/js/recorder.js
let mediaRecorder;
let audioChunks = [];
let conversationHistory = [];

const startButton = document.getElementById('startRecording');
const stopButton = document.getElementById('stopRecording');
const statusElement = document.getElementById('recordingStatus');
const spinner = document.getElementById('loadingSpinner');
const chatHistory = document.getElementById('chatHistory');
const aiResponse = document.getElementById('aiResponse');
const aiResponseText = document.getElementById('aiResponseText');

startButton.addEventListener('click', startRecording);
stopButton.addEventListener('click', stopRecording);

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = sendAudioToServer;

        audioChunks = [];
        mediaRecorder.start();
        
        startButton.disabled = true;
        stopButton.disabled = false;
        statusElement.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="red" style="animation: pulse 1.5s infinite">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
            </svg>`;
        
    } catch (err) {
        console.error('Error accessing microphone:', err);
        statusElement.textContent = "Error accessing microphone. Please ensure you have given permission.";
    }
}

function stopRecording() {
    mediaRecorder.stop();
    startButton.disabled = false;
    stopButton.disabled = true;
    statusElement.textContent = "Just a min...";
    spinner.classList.remove('hidden');
}

async function sendAudioToServer() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/mp4' });
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.m4a');
    formData.append('history', JSON.stringify(conversationHistory));

    try {
        const response = await fetch('/transcribe/', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Server response:", data);
        
        if (data.error) {
            console.error("Server error:", data.error);
            addMessage('Error: ' + data.error, 'error');
            return;
        }

        // Add messages to chat
        addMessage(data.transcription, 'user');
        addMessage(data.ai_response, 'ai');
        
        // Try to play audio if available
        console.log(data.tts_status);
        if (data.audio_data && data.tts_status === 'success') {
            console.log("Attempting to play audio...");
            try {
                await playAudioResponse(data.audio_data);
            } catch (audioError) {
                console.error("Audio playback failed:", audioError);
            }
        } else {
            console.log("No audio data available or TTS failed");
        }
        
        conversationHistory = data.history;
        
    } catch (err) {
        console.error("Request failed:", err);
        addMessage('Error: ' + err.message, 'error');
    } finally {
        spinner.classList.add('hidden');
        statusElement.textContent = "";
    }
}

async function playAudioResponse(base64AudioData) {
    return new Promise((resolve, reject) => {
        try {
            const audioData = atob(base64AudioData);
            const arrayBuffer = new ArrayBuffer(audioData.length);
            const view = new Uint8Array(arrayBuffer);
            
            for (let i = 0; i < audioData.length; i++) {
                view[i] = audioData.charCodeAt(i);
            }
            
            const audioBlob = new Blob([arrayBuffer], { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);

            audio.onerror = (e) => {
                console.error("Audio error:", e);
                URL.revokeObjectURL(audioUrl);
                reject(new Error('Audio playback failed'));
            };

            audio.onended = () => {
                console.log("Audio playback completed");
                URL.revokeObjectURL(audioUrl);
                resolve();
            };

            audio.play()
                .then(() => console.log("Audio started playing"))
                .catch(err => {
                    console.error("Play failed:", err);
                    reject(err);
                });

        } catch (err) {
            console.error("Audio processing failed:", err);
            reject(err);
        }
    });
}

function addMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    messageDiv.textContent = text;
    
    if (type === 'ai') {
        // Add a small speaker icon to AI messages
        const speakerIcon = document.createElement('span');
        speakerIcon.innerHTML = '🔊';
        speakerIcon.className = 'speaker-icon';
        speakerIcon.style.marginLeft = '8px';
        speakerIcon.style.cursor = 'pointer';
        messageDiv.appendChild(speakerIcon);
    }
    
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}
