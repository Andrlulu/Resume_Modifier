# Resume Modifier

## Project Description
Resume Modifier is a web service that helps users optimize their resumes for specific job descriptions using AI. The service:
- Parses and analyzes PDF resumes
- Compares resume content against job descriptions
- Provides AI-powered suggestions for improvement
- Manages multiple resumes and job applications
- Secures user data with JWT authentication
- Stores data in a persistent PostgreSQL database

## API Documentation
Detailed API documentation is available [here](https://docs.google.com/document/d/1y-apfWolpNhmUbpuSNJat0SojwjjA9y4M3c6vH9FCoo/edit?usp=sharing)

## Setup
1. Clone the repository
2. Get your OpenAI API key from: https://platform.openai.com/account/api-keys
3. Get or generate a JWT secret key for authentication

## Environment Setup
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Add your environment variables to `.env`:
   ```
   OPENAI_API_KEY=your_api_key_here
   JWT_SECRET=your_jwt_secret_here
   ```

## Running with Docker Compose (Recommended)
1. Start the application:
   ```bash
   docker compose up --build
   ```
2. The application will be available at:
   - API: http://localhost:5001
   - Database: localhost:5432

3. To stop and remove containers:
   ```bash
   docker compose down
   ```

4. To stop and remove containers including database volume:
   ```bash
   docker compose down -v
   ```

## Running Locally (Development)
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Make sure PostgreSQL is running locally with:
   - Database name: resume_app
   - Username: postgres
   - Password: postgres

3. Run the server:
   ```bash
   python -m app.server
   ```

## API Endpoints
- `POST /api/register` - Register new user
- `POST /api/login` - Login user and get JWT token
- `POST /api/pdfupload` - Upload and parse resume PDF (requires authentication)
- `POST /api/job_description_upload` - Analyze resume against job description (requires authentication)
- `PUT /api/feedback` - Process feedback for resume sections (requires authentication)

## Testing
```bash
pytest app/tests/
```

## Database Management
- View Docker volumes:
  ```bash
  docker volume ls
  ```
- Backup database:
  ```bash
  docker compose exec db pg_dump -U postgres resume_app > backup.sql
  ```
- Restore database:
  ```bash
  docker compose exec -T db psql -U postgres resume_app < backup.sql
  ```

Note: 
- Make sure you have Docker and Docker Compose installed
- All authenticated endpoints require a JWT token in the Authorization header: `Bearer <token>`
- Database data persists in Docker volume between restarts
- See the [API Documentation](https://docs.google.com/document/d/1y-apfWolpNhmUbpuSNJat0SojwjjA9y4M3c6vH9FCoo/edit?usp=sharing) for detailed request/response formats and examples 