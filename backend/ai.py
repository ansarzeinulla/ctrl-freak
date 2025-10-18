import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from the .env file
load_dotenv()

def generate_ai_response(api_key, vacancy_details, resume_details, history):
  """
  Generates a response from the AI based on vacancy, resume, and conversation history.
  """
  genai.configure(api_key=api_key)
  
  model = genai.GenerativeModel('gemini-flash-latest') 
  
  # Construct a detailed prompt for the AI
  prompt = f"""
You are an expert HR assistant. Your task is to evaluate a candidate's resume against a job vacancy.

**INSTRUCTIONS:**
1.  **Analyze:** Review the provided "JOB VACANCY" and "CANDIDATE RESUME".
2.  **Identify Gaps:** Determine if the resume provides enough information to assess suitability.
3.  **Ask or Conclude:**
    *   **If information is missing:** Ask a SINGLE, concise question to the candidate to clarify their experience or skills relevant to the vacancy. Do NOT be conversational, just ask the question.
    *   **If you have enough information (from the resume and conversation history):** Conclude your analysis. Provide a final suitability score as a percentage from 0 to 100. Your response MUST be a JSON object with two keys: "final_score" (an integer) and "summary" (a brief explanation for the score). Example: {{"final_score": 85, "summary": "The candidate is a strong fit..."}}

**IMPORTANT:**
-   When you decide to conclude, the JSON output is the ONLY thing you should return.
-   The "CONVERSATION HISTORY" shows the questions you've already asked and the candidate's answers. Use it to inform your next step. Avoid repeating questions.

**DETAIlS TO PAY ATTENTION TO:**
- Look at languages
- Look at city, if other city, ask about relocation
- Look at skills and experience requirements
- Look at education requirements
- Ask about will they are ready to learn fast new skills if needed
- Ask when they will finish their education
---
**JOB VACANCY:**
{vacancy_details}

---
**CANDIDATE RESUME:**
{resume_details}

---
**CONVERSATION HISTORY:**
{"No history yet." if not history else history}
---

Your response:
"""
  
  response = model.generate_content(prompt)
  return response.text