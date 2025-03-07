from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import google.generativeai as genai
from groq import Groq
from gtts import gTTS
import wave
from dotenv import load_dotenv

import logging

# Enable logging
logging.basicConfig(level=logging.INFO)
# Load API keys
load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
client = Groq(api_key=GROQ_API_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to "*" temporarily for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/generate_question")
def generate_question(topic: str = "general"):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"Generate a random interview-style question on {topic}."
    response = model.generate_content(prompt)
    return {"question": response.text.strip()}

@app.post("/upload_audio/")
def upload_audio(file: UploadFile = File(...)):
    filename = "response.wav"
    with open(filename, "wb") as buffer:
        buffer.write(file.file.read())

    # Transcribe audio
    transcription = client.audio.transcriptions.create(
        file=(filename, open(filename, "rb").read()),
        model="whisper-large-v3-turbo",
        language="en",
        response_format="json"
    )

    text = transcription.text.strip()
    feedback = analyze_confidence(text)

    # Automatically generate `feedback.mp3`
    speak_feedback(feedback)

    return {"transcription": text, "feedback": feedback, "audio_file": "feedback.mp3"}


@app.get("/speak_feedback/")
def speak_feedback(text: str):
    if not text:
        logging.error("No text received for speech synthesis!")
        return {"error": "No feedback text provided"}

    logging.info(f"Generating speech for: {text}")

    filename = "feedback.mp3"
    try:
        tts = gTTS(text)
        tts.save(filename)
        logging.info("Feedback audio saved as feedback.mp3")
        return {"audio_file": filename}
    except Exception as e:
        logging.error(f"Error generating speech: {e}")
        return {"error": "Failed to generate speech"}


def analyze_confidence(text):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = (
        "Analyze this response for confidence, nervousness, hesitation, and emotional tone. "
        "Give a confidence score from 0 to 100 and provide detailed feedback. "
        "Ensure the response is at least 10 words long. "
        "Use clear, natural sentences suitable for text-to-speech conversion.\n\n"
        f"Response: {text}"
    )
    
    try:
        response = model.generate_content(prompt)
        feedback = response.text.strip()
        if not feedback:
            return "I could not analyze the confidence of your response. Please try again."
        return feedback
    except Exception as e:
        logging.error(f"Error analyzing confidence: {e}")
        return "Error in confidence analysis."
