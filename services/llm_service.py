from openai import OpenAI
from typing import Dict, Any
from config import settings
import json        
from google import genai
import os
from dotenv import load_dotenv
load_dotenv()
class OpenAILLMService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        
    def generate_insights(self, csv_summary: str, vision_insights: str, user_description: str) -> Dict[str, Any]:
        prompt = f"""You are a business analytics AI. Analyze the following data and generate a comprehensive report.

USER REQUEST: {user_description}

CSV DATA ANALYSIS:
{csv_summary}

VISUAL INSIGHTS FROM IMAGES:
{vision_insights}

Generate a JSON response with the following structure:
{{
    "summary": "2-3 paragraph executive summary of key findings",
    "key_metrics": [
        {{"name": "metric name", "value": "value", "unit": "optional unit"}},
        ...
    ],
    "trends": [
        {{"description": "trend description", "direction": "up/down/stable", "impact": "positive/negative/neutral"}},
        ...
    ],
    "correlations": [
        "correlation insight 1",
        "correlation insight 2",
        ...
    ],
    "recommendations": [
        {{"priority": "high/medium/low", "action": "recommended action", "rationale": "why this matters"}},
        ...
    ],
    "visual_insights": [
        "insight from image 1",
        "insight from image 2",
        ...
    ]
}}

Provide actionable, specific insights based on the data. Be concise but comprehensive."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert business analyst. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {
                "summary": f"Error generating insights: {str(e)}",
                "key_metrics": [],
                "trends": [],
                "correlations": [],
                "recommendations": [],
                "visual_insights": []
            }
    
    def generate_text_completion(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
        


class GeminiLLMService:
    def __init__(self):
        # genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        print(f"Gemini API Key: {settings.GEMINI_API_KEY}")
        self.model = "gemini-2.5-flash"  # or "gemini-2.5-flash"
        
    def generate_insights(self, csv_summary: str, vision_insights: str, user_description: str) -> Dict[str, Any]:
        prompt = f"""You are a business analytics AI. Analyze the following data and generate a comprehensive report.

USER REQUEST: {user_description}

CSV DATA ANALYSIS:
{csv_summary}

VISUAL INSIGHTS FROM IMAGES:
{vision_insights}

Generate a JSON response with the following structure:
{{
    "summary": "2-3 paragraph executive summary of key findings",
    "key_metrics": [
        {{"name": "metric name", "value": "value", "unit": "optional unit"}},
        ...
    ],
    "trends": [
        {{"description": "trend description", "direction": "up/down/stable", "impact": "positive/negative/neutral"}},
        ...
    ],
    "correlations": [
        "correlation insight 1",
        "correlation insight 2",
        ...
    ],
    "recommendations": [
        {{"priority": "high/medium/low", "action": "recommended action", "rationale": "why this matters"}},
        ...
    ],
    "visual_insights": [
        "insight from image 1",
        "insight from image 2",
        ...
    ]
}}

Provide actionable, specific insights based on the data. Be concise but comprehensive.
IMPORTANT: Respond with ONLY valid JSON. Do not include any markdown formatting, backticks, or explanatory text."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "temperature": 0.7,
                    "response_mime_type": "application/json"
                }
            )
            
            # Clean the response text and parse JSON
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            result = json.loads(response_text.strip())
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {response.text[:500]}")
            return {
                "summary": "Error parsing response. Please try again.",
                "key_metrics": [],
                "trends": [],
                "correlations": [],
                "recommendations": [],
                "visual_insights": []
            }
        except Exception as e:
            return {
                "summary": f"Error generating insights: {str(e)}",
                "key_metrics": [],
                "trends": [],
                "correlations": [],
                "recommendations": [],
                "visual_insights": []
            }
    
    def generate_text_completion(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "temperature": 0.7
                }
            )
            return response.text.strip()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def create_chat_session(self):
        return self.client.chats.create(model=self.model)
    
    def chat_with_history(self, chat_session, message: str) -> str:
        try:
            response = chat_session.send_message(message)
            return response.text.strip()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_chat_history(self, chat_session) -> list:
        try:
            history = []
            for message in chat_session.get_history():
                history.append({
                    "role": message.role,
                    "content": message.parts[0].text
                })
            return history
        except Exception as e:
            return []
