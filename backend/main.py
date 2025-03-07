from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import google.generativeai as genai
from groq import Groq
from gtts import gTTS
import wave
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
import logging
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity

# Enable logging
logging.basicConfig(level=logging.INFO)

# Load API keys
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
client = Groq(api_key=GROQ_API_KEY)

app = FastAPI()
# Serve the static folder for audio files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to "*" temporarily for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the ArcFace model
face_analyzer = FaceAnalysis(name="buffalo_l")
face_analyzer.prepare(ctx_id=-1)  # Use CPU (-1) or GPU (0, 1, ...)

def get_embedding(image_data):
    """Extracts face embedding from an image."""
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    faces = face_analyzer.get(image)
    return faces[0].embedding if faces else None

@app.post("/compare_faces/")
async def compare_faces(image1: UploadFile = File(...), image2: UploadFile = File(...), threshold: float = 0.7):
    try:
        image1_data = np.frombuffer(await image1.read(), np.uint8)
        image2_data = np.frombuffer(await image2.read(), np.uint8)

        emb1, emb2 = get_embedding(image1_data), get_embedding(image2_data)

        if emb1 is None or emb2 is None:
            raise HTTPException(status_code=400, detail="Face not detected in one or both images.")

        similarity = cosine_similarity([emb1], [emb2])[0][0]
        is_match = similarity > threshold

        return {"match": bool(is_match), "similarity_score": round(float(similarity), 2)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/generate_question")
def generate_question(topic: str = "general"):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"Generate a random interview-style question on Python, javascript, web dev, machine learning. And it should be readable for a person within 10 seconds"
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

    filename = "static/feedback.mp3"  # Save in static directory
    try:
        tts = gTTS(text)
        tts.save(filename)
        logging.info("Feedback audio saved as feedback.mp3")
        return {"audio_file": "/static/feedback.mp3"}
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
