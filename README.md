# Resume Modifier

## Setup
1. Clone the repository
2. Get your OpenAI API key from: https://platform.openai.com/account/api-keys

## Environment Setup
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Add your OpenAI API key to `.env`:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Running Locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the server:
   ```bash
   python -m app.server
   ```

## Running with Docker
1. Build the image:
   ```bash
   docker build -t resume-modifier .
   ```
2. Run the container:
   ```bash
   docker run -p 5000:5000 --env-file .env resume-modifier
   ```

## API Endpoints
- `POST /api/pdfupload` - Upload and parse resume PDF
- `POST /api/job_description_upload` - Analyze resume against job description
- `PUT /api/feedback` - Process feedback for resume sections

## Testing
```bash
pytest app/tests/
```

Note: Make sure you have a valid OpenAI API key in your `.env` file before running. 