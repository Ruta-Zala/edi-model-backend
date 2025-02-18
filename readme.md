# Technical Documentation: FastAPI PDF to HTML Extractor

## 1. Overview
This project is a **FastAPI-based service** that processes PDF documents and extracts their content into **fully structured HTML course pages**. It ensures **100% extraction** of text, images, tables, and formatting while maintaining the document's structure.

## 2. Features
- **Complete Content Extraction:**  
  Extracts **all** text, headings, and paragraphs from PDFs without summarizing or omitting any information.
  
- **Accurate Table Conversion:**  
  If a PDF contains tables, they are converted into proper HTML `<table>` elements that preserve headers, rows, and formatting exactly as they appear in the source document.
  
- **Preserved Structure & Formatting:**  
  Maintains the **exact order, structure, and formatting** of the original document to ensure that the resulting HTML mirrors the source PDF.
  
- **Structured Course Output:**  
  Generates a fully structured HTML document that serves as a course page. This includes predefined sections for lessons, assignments, and quizzes based on the extracted content.
  
- **Assignments and Quizzes Generation:**  
  Based on the extracted content, the system can also provide detailed assignments and quizzes to support learning, including multiple types of questions.

## 3. OpenAI Assistant & Threads Configuration
The system leverages OpenAI's Assistant API to process and extract content from PDFs. Here’s how it works:
- **OpenAI Assistants:**  
  An assistant is created using a set of strict instructions provided in the `assistant_instructions.txt` file. These instructions define rules for extracting text, tables, images, and other elements exactly as they appear in the PDF.
  
- **Using Threads:**  
  The assistant runs in a threaded environment (via OpenAI’s beta threads API) to manage the processing workflow:
  - **File Upload:** The PDF is first uploaded as a file to OpenAI.
  - **Message Creation:** A thread is created, and a message is sent to the assistant with the command to extract a fully structured HTML page.
  - **Run Management:** The assistant processes the file within the thread. The system continuously checks the status of this run until it is marked as "completed" or "failed".
  - **Response Extraction:** Once processing is complete, the extracted content is returned and cleaned to remove any extra content before `<html>` or after `</html>`.
  
---

## 4. Installation & Setup

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- OpenAI API Key

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-repo/pdf-to-html-extractor.git
cd pdf-to-html-extractor
```

### Step 2: Create a Virtual Environment
```bash
python -m venv venv
source venv/Scripts/activate  
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables
Create a `.env` file and add the following:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 5: Run the FastAPI Server
```bash
uvicorn main:app --reload
```

### Step 6: Access the API
Once the server is running, open:
```
http://127.0.0.1:8000/docs
```
This will open the **Swagger UI**, where you can test the API.

---

## 5. Running with Docker

### Step 1: Build the Docker Container
```bash

docker-compose build 
```
### Step 2:  Run the Docker Container
```bash

docker-compose up 
```

### Step 3: Stop the Container
```bash
docker-compose down
```

---

## 6. API Usage
### **Endpoint:** `/generate_course/`
- **Method:** `POST`
- **Description:** Uploads a PDF and returns a fully structured HTML course page.
- **Request Format:** Multipart Form
- **Required File Type:** PDF

#### **Example Request (Using cURL)**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/generate_course/' \
  -H 'accept: text/html' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@sample.pdf'
```

#### **Response Format (HTML Example)**
```html
<html>
<head><title>Extracted Course</title></head>
<body>
  <h1>Course Title</h1>
  <p>Full course content extracted...</p>
</body>
</html>
```








