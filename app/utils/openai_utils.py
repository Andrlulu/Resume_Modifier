from openai import OpenAI
import os
import json


def analyze_text_with_openai(extracted_text, job_description):
    # Initialize the client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    messages = [
        {"role": "system",
         "content": "You analyze resumes against job descriptions and return a structured JSON response."},
        {"role": "user", "content": f"Job Description:\n{job_description}\n\nResume Text:\n{extracted_text}"}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Changed from gpt-4 to gpt-4o-mini
            messages=messages,
            max_tokens=1500,
            temperature=0.7,
        )

        ai_text = response.choices[0].message.content.strip()

        try:
            structured_data = json.loads(ai_text)
        except json.JSONDecodeError:
            structured_data = {"parsed_text": extracted_text, "analysis": ai_text}

        return structured_data

    except Exception as e:
        return {"error": f"OpenAI API error: {str(e)}"}
