import json
from fastapi import APIRouter, UploadFile, File, Form
from app.models.schemas import ChatRequest, ChatResponse, Message
from app.services.llm import generate_tutor_response
from app.services.audio import transcribe_audio

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    lesson_data = await generate_tutor_response(request.messages, "English", "C1 (Advanced)")
    return ChatResponse(
        user_text="[Text Input]",
        english_audio=lesson_data.get("english_audio", ""),
        target_audio=lesson_data.get("target_audio", ""),
        feedback=lesson_data.get("feedback", ""),
        score=lesson_data.get("score", 0),
        next_exercise=lesson_data.get("next_exercise", "")
    )

@router.post("/chat-audio", response_model=ChatResponse)
async def chat_audio_endpoint(
    file: UploadFile = File(...),
    messages_json: str = Form("[]"), 
    target_language: str = Form(...),  
    proficiency_level: str = Form(...)
):
    file_bytes = await file.read()
    
    # REVERTED: We are no longer passing target_language here
    user_text = await transcribe_audio(file_bytes, file.filename)
    
    if not user_text:
        return ChatResponse(
            user_text="", 
            english_audio="I couldn't hear that clearly. Could you try speaking a bit louder?",
            target_audio="",
            feedback="Microphone error. No audio detected.",
            score=0,
            next_exercise="Please try again."
        )

    try:
        history_dicts = json.loads(messages_json)
        messages = [Message(**msg) for msg in history_dicts]
    except Exception:
        messages = []
        
    messages.append(Message(role="user", content=user_text))
    
    lesson_data = await generate_tutor_response(messages, target_language, proficiency_level)
    
    return ChatResponse(
        user_text=user_text,
        english_audio=lesson_data.get("english_audio", ""),
        target_audio=lesson_data.get("target_audio", ""),
        feedback=lesson_data.get("feedback", ""),
        score=lesson_data.get("score", 0),
        next_exercise=lesson_data.get("next_exercise", "")
    )