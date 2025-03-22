# from fastapi import FastAPI, UploadFile, File, Form
# from fastapi.middleware.cors import CORSMiddleware
# import os
# import google.generativeai as genai
# from groq import Groq
# from gtts import gTTS
# import wave
# from dotenv import load_dotenv
# from fastapi.staticfiles import StaticFiles
# import logging
# from pydantic import BaseModel
# from typing import List, Optional
# import json

# # Enable logging
# logging.basicConfig(level=logging.INFO)
# # Load API keys
# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# genai.configure(api_key=GEMINI_API_KEY)
# client = Groq(api_key=GROQ_API_KEY)

# app = FastAPI()
# # Serve the static folder for audio files
# app.mount("/static", StaticFiles(directory="static"), name="static")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Change this to specific origins in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class QuestionRequest(BaseModel):
#     skills: Optional[str] = None

# class FinalAnalysisRequest(BaseModel):
#     responses: List[dict]
#     skills: Optional[str] = None

# @app.post("/generate_question")
# async def generate_question(request: QuestionRequest):
#     skills = request.skills if request.skills else "general"
#     logging.info(f"Generating question for skills: {skills}")
    
#     model = genai.GenerativeModel("gemini-1.5-flash")
    
#     # Craft a prompt that uses the user's skills
#     prompt = f"""
#     Generate a professional interview question that specifically tests a candidate's knowledge and experience in {skills}.
#     The question should:
#     1. Be challenging but appropriate for a job interview
#     2. Require detailed knowledge of {skills}
#     3. Allow the candidate to demonstrate both technical knowledge and practical experience
#     4. Be open-ended enough to allow for a 1-2 minute response
#     5. Return ONLY the question without any explanation, introduction, or commentary
#     """
    
#     try:
#         response = model.generate_content(prompt)
#         question = response.text.strip()
#         logging.info(f"Generated question: {question}")
#         return {"question": question}
#     except Exception as e:
#         logging.error(f"Error generating question: {e}")
#         return {"question": f"Tell me about your experience with {skills}."}

# @app.post("/upload_audio/")
# async def upload_audio(
#     file: UploadFile = File(...),
#     skills: str = Form(None),
#     question: str = Form(None)
# ):
#     filename = "response.wav"
#     with open(filename, "wb") as buffer:
#         buffer.write(file.file.read())

#     logging.info(f"Received audio for skills: {skills}")
#     logging.info(f"Question was: {question}")

#     # Transcribe audio
#     try:
#         transcription = client.audio.transcriptions.create(
#             file=(filename, open(filename, "rb").read()),
#             model="whisper-large-v3-turbo",
#             language="en",
#             response_format="json"
#         )
#         text = transcription.text.strip()
#     except Exception as e:
#         logging.error(f"Error transcribing audio: {e}")
#         text = "Could not transcribe the audio"

#     # Generate feedback based on skills and question context
#     feedback = analyze_response(text, skills, question)

#     # Automatically generate `feedback.mp3`
#     speak_feedback(feedback)

#     return {"transcription": text, "feedback": feedback, "audio_file": "feedback.mp3"}

# @app.post("/final_analysis")
# async def final_analysis(request: FinalAnalysisRequest):
#     responses = request.responses
#     skills = request.skills if request.skills else "general skills"
    
#     logging.info(f"Generating final analysis for skills: {skills}")
#     logging.info(f"Number of responses: {len(responses)}")
    
#     if not responses:
#         return {"analysis": "No responses to analyze."}
    
#     model = genai.GenerativeModel("gemini-1.5-flash")
    
#     # Format the responses for the prompt
#     formatted_responses = ""
#     for i, resp in enumerate(responses):
#         formatted_responses += f"Q{i+1}: {resp.get('question', 'Unknown question')}\n"
#         formatted_responses += f"A{i+1}: {resp.get('response', 'No response')}\n\n"
    
#     prompt = f"""
#     You are an expert interviewer and career coach specializing in {skills}. 
#     Analyze the following interview responses and provide comprehensive feedback:

#     {formatted_responses}

#     Please provide:
#     1. An overall assessment of the candidate's communication skills
#     2. Specific strengths demonstrated in their responses
#     3. Areas for improvement
#     4. How well they demonstrated knowledge of {skills}
#     5. Advice for future interviews
    
#     Format your analysis in clear paragraphs that are easy to read and understand.
#     """
    
#     try:
#         response = model.generate_content(prompt)
#         analysis = response.text.strip()
#         return {"analysis": analysis}
#     except Exception as e:
#         logging.error(f"Error generating final analysis: {e}")
#         return {"analysis": "Unable to generate analysis. Please try again."}

# @app.get("/speak_feedback/")
# def speak_feedback(text: str):
#     if not text:
#         logging.error("No text received for speech synthesis!")
#         return {"error": "No feedback text provided"}

#     logging.info(f"Generating speech for: {text}")

#     filename = "static/feedback.mp3"  # Save in static directory
#     try:
#         tts = gTTS(text)
#         tts.save(filename)
#         logging.info("Feedback audio saved as feedback.mp3")
#         return {"audio_file": "/static/feedback.mp3"}
#     except Exception as e:
#         logging.error(f"Error generating speech: {e}")
#         return {"error": "Failed to generate speech"}

# def analyze_response(text, skills=None, question=None):
#     model = genai.GenerativeModel("gemini-1.5-flash")
    
#     skills_context = f"for the skill areas of {skills}" if skills else ""
#     question_context = f"in response to the question: '{question}'" if question else ""
    
#     prompt = f"""
#     Analyze this interview response {skills_context} {question_context}. 
    
#     Response: "{text}"
    
#     Provide constructive feedback on:
#     1. Content quality and relevance
#     2. Confidence, clarity, and delivery
#     3. Technical accuracy {skills_context}
#     4. Structure and organization
#     5. Specific improvements for next time
    
#     Format your feedback in 3-4 natural sentences suitable for text-to-speech. Be constructive but encouraging.
#     """
    
#     try:
#         response = model.generate_content(prompt)
#         feedback = response.text.strip()
#         if not feedback:
#             return f"I couldn't analyze your response properly. Try speaking more clearly about your experience with {skills}."
#         return feedback
#     except Exception as e:
#         logging.error(f"Error analyzing response: {e}")
#         return "I had trouble analyzing your response. Please try again with more details about your experience."

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import logging
import json
import wave

# AI and Speech imports
import google.generativeai as genai
from groq import Groq
from gtts import gTTS
from dotenv import load_dotenv

# ===== CONFIG AND SETUP =====

# Enable logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Configure AI clients
genai.configure(api_key=GEMINI_API_KEY)
client = Groq(api_key=GROQ_API_KEY)

# ===== FASTAPI APP SETUP =====

app = FastAPI()

# Serve static files for audio
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== DATA MODELS =====

class QuestionRequest(BaseModel):
    skills: Optional[str] = None

class FinalAnalysisRequest(BaseModel):
    responses: List[dict]
    skills: Optional[str] = None

# ===== UTILITY FUNCTIONS =====

def analyze_response(text, skills=None, question=None):
    """Analyze an interview response using Gemini AI."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    skills_context = f"for the skill areas of {skills}" if skills else ""
    question_context = f"in response to the question: '{question}'" if question else ""
    
    prompt = f"""
    Analyze this interview response {skills_context} {question_context}. 
    
    Response: "{text}"
    
    Provide constructive feedback on:
    1. Content quality and relevance
    2. Confidence, clarity, and delivery
    3. Technical accuracy {skills_context}
    4. Structure and organization
    5. Specific improvements for next time
    
    Format your feedback in 3-4 natural sentences suitable for text-to-speech. Be constructive but encouraging.
    """
    
    try:
        response = model.generate_content(prompt)
        feedback = response.text.strip()
        if not feedback:
            return f"I couldn't analyze your response properly. Try speaking more clearly about your experience with {skills}."
        return feedback
    except Exception as e:
        logging.error(f"Error analyzing response: {e}")
        return "I had trouble analyzing your response. Please try again with more details about your experience."

# ===== API ENDPOINTS =====

@app.post("/generate_question")
async def generate_question(request: QuestionRequest):
    """Generate a tailored interview question based on specified skills."""
    skills = request.skills if request.skills else "general"
    logging.info(f"Generating question for skills: {skills}")
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    Generate a professional interview question that specifically tests a candidate's knowledge and experience in {skills}.
    The question should:
    1. Be challenging but appropriate for a job interview
    2. Require detailed knowledge of {skills}
    3. Allow the candidate to demonstrate both technical knowledge and practical experience
    4. Be open-ended enough to allow for a 1-2 minute response
    5. Return ONLY the question without any explanation, introduction, or commentary
    """
    
    try:
        response = model.generate_content(prompt)
        question = response.text.strip()
        logging.info(f"Generated question: {question}")
        return {"question": question}
    except Exception as e:
        logging.error(f"Error generating question: {e}")
        return {"question": f"Tell me about your experience with {skills}."}

@app.post("/upload_audio/")
async def upload_audio(
    file: UploadFile = File(...),
    skills: str = Form(None),
    question: str = Form(None)
):
    """Process uploaded audio interview response and provide feedback."""
    filename = "response.wav"
    with open(filename, "wb") as buffer:
        buffer.write(file.file.read())

    logging.info(f"Received audio for skills: {skills}")
    logging.info(f"Question was: {question}")

    # Transcribe audio
    try:
        transcription = client.audio.transcriptions.create(
            file=(filename, open(filename, "rb").read()),
            model="whisper-large-v3-turbo",
            language="en",
            response_format="json"
        )
        text = transcription.text.strip()
    except Exception as e:
        logging.error(f"Error transcribing audio: {e}")
        text = "Could not transcribe the audio"

    # Generate feedback based on skills and question context
    feedback = analyze_response(text, skills, question)

    # Automatically generate `feedback.mp3`
    speak_feedback(feedback)

    return {"transcription": text, "feedback": feedback, "audio_file": "feedback.mp3"}

@app.post("/final_analysis")
async def final_analysis(request: FinalAnalysisRequest):
    """Generate a comprehensive analysis of all interview responses."""
    responses = request.responses
    skills = request.skills if request.skills else "general skills"
    
    logging.info(f"Generating final analysis for skills: {skills}")
    logging.info(f"Number of responses: {len(responses)}")
    
    if not responses:
        return {"analysis": "No responses to analyze."}
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Format the responses for the prompt
    formatted_responses = ""
    for i, resp in enumerate(responses):
        formatted_responses += f"Q{i+1}: {resp.get('question', 'Unknown question')}\n"
        formatted_responses += f"A{i+1}: {resp.get('response', 'No response')}\n\n"
    
    prompt = f"""
    You are an expert interviewer and career coach specializing in {skills}. 
    Analyze the following interview responses and provide comprehensive feedback:

    {formatted_responses}

    Please provide:
    1. An overall assessment of the candidate's communication skills
    2. Specific strengths demonstrated in their responses
    3. Areas for improvement
    4. How well they demonstrated knowledge of {skills}
    5. Advice for future interviews
    
    Format your analysis in clear paragraphs that are easy to read and understand.
    """
    
    try:
        response = model.generate_content(prompt)
        analysis = response.text.strip()
        return {"analysis": analysis}
    except Exception as e:
        logging.error(f"Error generating final analysis: {e}")
        return {"analysis": "Unable to generate analysis. Please try again."}

@app.get("/speak_feedback/")
def speak_feedback(text: str):
    """Convert feedback text to speech and save as MP3."""
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