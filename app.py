from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
from pathlib import Path

from pydantic import BaseModel

# Backend API URL for Ollama
OLLAMA_API_URL = "http://localhost:11434/api/chat"  # Replace with your actual Ollama API endpoint if different

# FastAPI instance
app = FastAPI()

# Static files (for serving images, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 template renderer
templates = Jinja2Templates(directory="templates")

# Pydantic model for request body
class UserInput(BaseModel):
    user_input: str
# Function to send user query to Ollama and get response
def get_response_from_ollama(user_input):
    payload = {
        "model": "llama3.2",  # Specify the model you're using
        "messages": [{"role": "user", "content": user_input.user_input}],
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        #response.raise_for_status()
        # Extract the assistant's message from the response
        print(response.json())
        return response.json().get("message", {}).get("content", "Sorry, I couldn't understand that. Please try again.")
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

@app.get("/", response_class=HTMLResponse)
async def get_chat_ui(request: Request):
    # Render the chat UI using Jinja2 template
    return templates.TemplateResponse("chat_ui.html", {"request": request})

@app.post("/chat")
async def chat(user_input: UserInput):
    # Get response from Ollama based on user input
    response = get_response_from_ollama(user_input)
    return {"response": response}
