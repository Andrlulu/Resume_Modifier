# Resume Modifier

## Setup
1. Clone the repository
2. Get your OpenAI API key from: https://platform.openai.com/account/api-keys

## Running Locally
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Add your OpenAI API key to `.env`
3. Run the server:
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
   docker run -p 5000:5000 -e OPENAI_API_KEY=your_actual_api_key resume-modifier
   ```

Note: Replace `your_actual_api_key` with your OpenAI API key. 