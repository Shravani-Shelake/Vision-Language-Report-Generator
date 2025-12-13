from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
from typing import List, Dict
from config import settings
from google import genai
from google.genai import types

class BlipVisionService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading vision model on {self.device}...")
        self.processor = BlipProcessor.from_pretrained(settings.VISION_MODEL)
        self.model = BlipForConditionalGeneration.from_pretrained(settings.VISION_MODEL).to(self.device)
        print("Vision model loaded successfully")
    
    def analyze_image(self, image_path: str) -> Dict[str, str]:
        try:
            image = Image.open(image_path).convert('RGB')
            
            # Generate caption
            inputs = self.processor(image, return_tensors="pt").to(self.device)
            out = self.model.generate(**inputs, max_length=100)
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            
            # Generate detailed description with conditional prompt
            prompt = "describe this business chart or infographic in detail:"
            inputs = self.processor(image, prompt, return_tensors="pt").to(self.device)
            out = self.model.generate(**inputs, max_length=150)
            description = self.processor.decode(out[0], skip_special_tokens=True)
            
            return {
                "caption": caption,
                "description": description,
                "status": "success"
            }
        except Exception as e:
            return {
                "caption": "",
                "description": f"Error analyzing image: {str(e)}",
                "status": "error"
            }
    
    def analyze_multiple_images(self, image_paths: List[str]) -> List[Dict[str, str]]:
        results = []
        for idx, path in enumerate(image_paths):
            result = self.analyze_image(path)
            result["image_index"] = idx
            result["image_path"] = path
            results.append(result)
        return results


class VisionService:
    def __init__(self):
        print("Initializing Gemini vision service...")
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = "gemini-2.0-flash-exp"  # or "gemini-2.5-flash" based on your needs
        print("Gemini vision service initialized successfully")
    
    def _get_mime_type(self, image_path: str) -> str:
        mime_type, _ = mimetypes.guess_type(image_path)
        return mime_type or 'image/jpeg'
    
    def analyze_image(self, image_path: str) -> Dict[str, str]:
        try:
            # Read image as bytes
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            mime_type = self._get_mime_type(image_path)
            
            # Generate caption
            caption_response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=mime_type,
                    ),
                    'Provide a brief caption for this image in one sentence.'
                ]
            )
            caption = caption_response.text.strip()
            
            # Generate detailed description
            description_response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=mime_type,
                    ),
                    'Describe this business chart or infographic in detail. Include all key data points, trends, labels, and insights visible in the image.'
                ]
            )
            description = description_response.text.strip()
            
            return {
                "caption": caption,
                "description": description,
                "status": "success"
            }
        except Exception as e:
            return {
                "caption": "",
                "description": f"Error analyzing image: {str(e)}",
                "status": "error"
            }
    
    def analyze_multiple_images(self, image_paths: List[str]) -> List[Dict[str, str]]:
        results = []
        for idx, path in enumerate(image_paths):
            result = self.analyze_image(path)
            result["image_index"] = idx
            result["image_path"] = path
            results.append(result)
        return results
    
    def compare_images(self, image_paths: List[str], prompt: str = None) -> str:
        try:
            if not image_paths:
                return "No images provided"
            
            contents = []
            
            # Add prompt
            if prompt is None:
                prompt = "Analyze and compare these images. Describe what you see in each and highlight key differences or patterns."
            contents.append(prompt)
            
            # Add all images
            for image_path in image_paths:
                with open(image_path, 'rb') as f:
                    image_bytes = f.read()
                
                mime_type = self._get_mime_type(image_path)
                contents.append(
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=mime_type
                    )
                )
            
            # Generate comparison
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents
            )
            
            return response.text.strip()
            
        except Exception as e:
            return f"Error comparing images: {str(e)}"
