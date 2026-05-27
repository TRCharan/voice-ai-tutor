import { useState, useRef } from 'react';
import axios from 'axios';
import { Mic, Square, Loader2, Bot } from 'lucide-react';

function App() {
  const [messages, setMessages] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  // Refs to manage the audio recording state without triggering re-renders
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        // 1. Dynamically get the exact audio format the browser used
        const mimeType = mediaRecorderRef.current.mimeType;
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        
        // 2. We name it .wav so Groq's API accepts the file header easily
        const audioFile = new File([audioBlob], 'recording.wav', { type: mimeType });
        
        stream.getTracks().forEach(track => track.stop());
        await sendAudioToBackend(audioFile);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Microphone access denied:", error);
      alert("Please allow microphone access to use the AI Tutor.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const sendAudioToBackend = async (audioFile) => {
    setIsLoading(true);
    try {
      // Create FormData to send the file AND the JSON string simultaneously
      const formData = new FormData();
      formData.append("file", audioFile);
      formData.append("messages_json", JSON.stringify(messages));

      // Make the API call to our FastAPI server
      const response = await axios.post("http://127.0.0.1:8000/api/chat-audio", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      // Update the chat history. We don't have the user's exact transcribed text 
      // in the response payload currently, so we'll just show the AI's reply for the MVP.
      setMessages((prev) => [
        ...prev, 
        { role: "user", content: response.data.user_text },
        { role: "assistant", content: response.data.reply }
      ]);
      
    } catch (error) {
      console.error("API Error:", error);
      alert("Failed to connect to the AI Tutor.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    // Background: A subtle modern gradient instead of flat gray
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex flex-col items-center justify-center p-4 sm:p-8 font-sans text-gray-800">
      
      {/* Main App Container: Glassmorphism effect */}
      <div className="w-full max-w-3xl bg-white/70 backdrop-blur-xl border border-white/40 rounded-3xl shadow-2xl overflow-hidden flex flex-col h-[85vh] sm:h-[80vh] relative">
        
        {/* Header: Clean and minimal */}
        <header className="p-6 border-b border-gray-100/50 flex justify-between items-center bg-white/30">
          <div className="flex items-center gap-3">
            <div className="bg-indigo-600 p-2 rounded-xl shadow-inner text-white">
              <Bot size={24} strokeWidth={2.5} />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-purple-600">
                AI Language Tutor
              </h1>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Voice Beta</p>
            </div>
          </div>
          <div className="flex gap-2">
             {/* Decorative status indicator */}
             <div className="flex items-center gap-2 text-xs font-semibold text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-full border border-indigo-100">
               <span className="relative flex h-2 w-2">
                 <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                 <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
               </span>
               Online
             </div>
          </div>
        </header>

        {/* Chat Interface */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-60">
              <div className="bg-indigo-100 p-4 rounded-full text-indigo-500 mb-2">
                <Mic size={32} />
              </div>
              <p className="text-lg font-medium text-gray-600">Tap the microphone to start speaking.</p>
              <p className="text-sm text-gray-400 max-w-xs">Try saying: "Hello, can you help me practice for my interview?"</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                
                {/* AI Avatar (Only show on AI messages) */}
                {msg.role === 'assistant' && (
                  <div className="flex-shrink-0 mr-3 self-end mb-1">
                    <div className="bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-full p-2 text-white shadow-md">
                      <Bot size={18} />
                    </div>
                  </div>
                )}

                {/* Message Bubble */}
                <div className={`max-w-[80%] sm:max-w-[70%] rounded-2xl px-5 py-4 shadow-sm relative text-sm sm:text-base leading-relaxed
                  ${msg.role === 'user' 
                    ? 'bg-gradient-to-br from-indigo-600 to-blue-600 text-white rounded-br-sm shadow-indigo-200' 
                    : 'bg-white text-gray-800 border border-gray-100 rounded-bl-sm'}`}
                >
                  <p>{msg.content}</p>
                </div>
              </div>
            ))
          )}

          {/* Loading / Thinking State */}
          {isLoading && (
            <div className="flex w-full justify-start items-center gap-3 mt-4 animate-pulse">
               <div className="bg-gray-200 rounded-full p-2 text-gray-500 shadow-sm">
                  <Bot size={18} />
                </div>
              <div className="bg-white border border-gray-100 rounded-2xl px-5 py-3 shadow-sm rounded-bl-sm flex items-center gap-2">
                <span className="text-sm font-medium text-indigo-500">Transcribing & Thinking</span>
                <Loader2 className="animate-spin text-indigo-400" size={16} />
              </div>
            </div>
          )}
          
          {/* Invisible div to pad the bottom so messages don't hide behind the floating mic */}
          <div className="h-24"></div>
        </div>

        {/* Floating Action Area (Bottom Center) */}
        <div className="absolute bottom-6 left-0 right-0 flex justify-center pointer-events-none">
          <div className="pointer-events-auto relative">
            
            {/* Visualizer rings when recording */}
            {isRecording && (
              <div className="absolute inset-0 bg-red-400 rounded-full animate-ping opacity-20 scale-150"></div>
            )}

            <button 
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isLoading}
              className={`flex items-center justify-center h-16 w-16 sm:h-20 sm:w-20 rounded-full shadow-2xl transition-all duration-300 transform 
                ${isRecording 
                  ? 'bg-red-500 hover:bg-red-600 scale-110 shadow-red-500/50' 
                  : 'bg-indigo-600 hover:bg-indigo-700 hover:scale-105 shadow-indigo-600/40'}
                ${isLoading ? 'opacity-50 cursor-not-allowed scale-95' : ''}`}
            >
              {isRecording ? (
                <Square className="text-white fill-white" size={24} />
              ) : (
                <Mic className="text-white" size={28} />
              )}
            </button>
          </div>
        </div>
        
      </div>
    </div>
  );
}

export default App;