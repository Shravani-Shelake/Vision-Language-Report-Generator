from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from config import settings
import uuid
from google import genai

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self.collection_name = settings.QDRANT_COLLECTION
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_size = 384  # all-MiniLM-L6-v2 embedding size
        
        # Create collection if not exists
        self._init_collection()
    
    def _init_collection(self):
        """Initialize Qdrant collection"""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
                )
                print(f"Created Qdrant collection: {self.collection_name}")
            else:
                print(f"Qdrant collection already exists: {self.collection_name}")
        except Exception as e:
            print(f"Warning: Could not initialize Qdrant collection: {e}")
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text"""
        embedding = self.encoder.encode(text)
        return embedding.tolist()
    
    def store_report_embedding(self, report_id: str, report_data: Dict[str, Any]):
        """Store report embeddings in Qdrant"""
        try:
            # Create text representation of report
            text_parts = []
            
            if isinstance(report_data.get('summary'), str):
                text_parts.append(f"Summary: {report_data['summary']}")
            
            if 'key_metrics' in report_data:
                metrics_text = ", ".join([
                    f"{m.get('name', '')}: {m.get('value', '')}" 
                    for m in report_data['key_metrics']
                ])
                text_parts.append(f"Metrics: {metrics_text}")
            
            if 'trends' in report_data:
                trends_text = ", ".join([
                    t.get('description', '') 
                    for t in report_data['trends']
                ])
                text_parts.append(f"Trends: {trends_text}")
            
            full_text = " | ".join(text_parts)
            
            # Generate embedding
            embedding = self.embed_text(full_text)
            
            # Store in Qdrant
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "report_id": report_id,
                    "summary": report_data.get('summary', ''),
                    "text": full_text[:1000]  # Store truncated text
                }
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            return True
        except Exception as e:
            print(f"Error storing embedding: {e}")
            return False
    
    def search_similar_reports(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar reports"""
        try:
            query_embedding = self.embed_text(query)
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit
            )
            
            return [
                {
                    "report_id": hit.payload.get("report_id"),
                    "summary": hit.payload.get("summary"),
                    "score": hit.score
                }
                for hit in results
            ]
        except Exception as e:
            print(f"Error searching: {e}")
            return []