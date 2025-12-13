from typing import List, Dict, Any
from datetime import datetime
from .csv_service import CSVService
from .vision_service import VisionService
from .llm_service import GeminiLLMService
from .qdrant_service import QdrantService
from .storage_service import StorageService
import json

class ReportService:
    def __init__(self):
        self.storage_service = StorageService()
        self.csv_service = CSVService()
        self.vision_service = VisionService()
        self.llm_service = GeminiLLMService()
        self.qdrant_service = QdrantService()
    
    def generate_report(
        self,
        csv_file_paths: List[str],
        image_file_paths: List[str],
        description: str
    ) -> Dict[str, Any]:
        try:
            # 1. Analyze CSV files
            csv_analyses = self.csv_service.analyze_multiple_csvs(csv_file_paths)
            csv_summary = self.csv_service.generate_data_summary(csv_analyses)
            print(f"CSV Summary: {csv_summary}")
            
            # 2. Analyze images
            vision_results = self.vision_service.analyze_multiple_images(image_file_paths)
            vision_summary = self._format_vision_insights(vision_results)
            
            # 3. Generate insights using LLM
            insights = self.llm_service.generate_insights(
                csv_summary=csv_summary,
                vision_insights=vision_summary,
                user_description=description
            )
            
            # 4. Format final report
            report_data = {
                "summary": insights.get("summary", "No summary available"),
                "key_metrics": insights.get("key_metrics", []),
                "trends": insights.get("trends", []),
                "correlations": insights.get("correlations", []),
                "recommendations": insights.get("recommendations", []),
                "visual_insights": insights.get("visual_insights", []),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "data": report_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _format_vision_insights(self, vision_results: List[Dict[str, str]]) -> str:
        insights = []
        for idx, result in enumerate(vision_results):
            if result.get("status") == "success":
                insight = f"\nImage {idx + 1}:\n"
                insight += f"  Caption: {result.get('caption', 'N/A')}\n"
                insight += f"  Description: {result.get('description', 'N/A')}\n"
                insights.append(insight)
        
        return "\n".join(insights) if insights else "No visual insights available"
    
    def store_report_embedding(self, report_id: str, report_data: Dict[str, Any]):
        return self.qdrant_service.store_report_embedding(report_id, report_data)
    
    def search_similar_reports(self, query: str, limit: int = 5):
        return self.qdrant_service.search_similar_reports(query, limit)
