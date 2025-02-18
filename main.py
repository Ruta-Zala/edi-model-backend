import openai
import os
import time
import re
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return HTMLResponse(
        content="<html><body><h1>Too Many Requests: Rate limit exceeded. Try again later.</h1></body></html>",
        status_code=429
    )

ASSISTANT_ID = ""

def read_instructions_from_file(filename="assistant_instructions.txt"):
    """Reads assistant instructions from a file."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

def validate_instructions(instructions):
    """Validate the completeness and relevance of the instructions."""
    required_keywords = ["extract", "image", "table", "html", "structure"]
    return all(keyword in instructions.lower() for keyword in required_keywords)

def create_new_assistant():
    """Creates a new assistant with refined instructions from an external file."""
    instructions = read_instructions_from_file()
    if not instructions or not validate_instructions(instructions):
        return None

    try:
        assistant = openai.beta.assistants.create(
            name="Structured Course HTML Generator",
            description="Processes PDFs and extracts detailed structured educational content into a fully formatted HTML course page.",
            model="gpt-4o",
            instructions=instructions,
            tools=[{"type": "file_search"}]
        )
        return assistant.id
    except Exception:
        return None

def get_or_create_assistant():
    """Returns the existing Assistant ID or creates a new one."""
    global ASSISTANT_ID
    if ASSISTANT_ID:
        return ASSISTANT_ID
    
    ASSISTANT_ID = create_new_assistant()
    return ASSISTANT_ID

def clean_html_response(raw_response: str) -> str:
    """Cleans up AI response to remove extra content before <html> and after </html>."""
    match = re.search(r"(<html>.*?</html>)", raw_response, re.DOTALL)
    if match:
        return match.group(1)
    return "<html><body><h1>Error: Invalid HTML response</h1></body></html>"

async def process_pdf_with_assistant(pdf_bytes: bytes):
    """Uploads PDF, processes it with OpenAI Assistant, and returns a cleaned HTML response."""
    try:
        file_response = openai.files.create(
            file=("course.pdf", pdf_bytes, "application/pdf"),
            purpose="assistants"
        )
        file_id = file_response.id

        assistant_id = get_or_create_assistant()
        if not assistant_id:
            raise Exception("Assistant creation failed.")

        thread = openai.beta.threads.create()
        thread_id = thread.id

        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content="Extract a fully structured HTML course page from this PDF.",
            attachments=[{"file_id": file_id, "tools": [{"type": "file_search"}]}]
        )

        run = openai.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
        run_id = run.id

        while True:
            run_status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                raise Exception("Assistant failed to process PDF.")
            time.sleep(2)

        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        if not messages.data:
            raise Exception("No messages returned from OpenAI.")

        raw_response = messages.data[0].content[0].text.value.strip()

        cleaned_html = clean_html_response(raw_response)

        openai.files.delete(file_id)

        return cleaned_html

    except Exception:
        return "<html><body><h1>Error: Failed to generate course.</h1></body></html>"

@app.post("/generate_course/", response_class=HTMLResponse)
@limiter.limit("2/minute")
async def generate_course_html(request: Request, file: UploadFile = File(...)):
    """Processes PDF and extracts structured course data, returning cleaned HTML"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    pdf_bytes = await file.read()
    course_html = await process_pdf_with_assistant(pdf_bytes)

    if not course_html or "<html>" not in course_html:
        raise HTTPException(status_code=500, detail="Failed to generate course.")

    return HTMLResponse(content=course_html)
