# from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
# from fastapi.responses import StreamingResponse
# from sqlalchemy.orm import Session
# from typing import List
# import uuid
# from datetime import datetime

# from config import settings
# from database import get_db, init_db, UploadedFile, Report
# from models import (
#     FileUploadResponse, GenerateReportRequest, 
#     GenerateReportResponse, ReportResponse, ReportData
# )
# from services.storage_service import StorageService
# from services.report_service import ReportService
# from services.pdf_service import PDFService

# # Initialize FastAPI
# app = FastAPI(
#     title=settings.APP_NAME,
#     version=settings.APP_VERSION,
#     description="AI-powered business report generator using vision and language models"
# )

# # Initialize services
# storage_service = StorageService()
# report_service = ReportService()

# # Initialize database on startup
# @app.on_event("startup")
# async def startup_event():
#     init_db()
#     print("Database initialized")

# @app.get("/")
# async def root():
#     """Health check endpoint"""
#     return {
#         "message": "Vision-Language Report Generator API",
#         "version": settings.APP_VERSION,
#         "status": "running"
#     }

# @app.post("/upload/csv", response_model=FileUploadResponse)
# async def upload_csv(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db)
# ):
#     """Upload a CSV file"""
#     # Validate file extension
#     if not any(file.filename.lower().endswith(ext) for ext in settings.ALLOWED_CSV_EXTENSIONS):
#         raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files allowed.")
    
#     # Upload file
#     file_id, storage_path = await storage_service.upload_file(file, "csv")
    
#     # Save metadata to database
#     db_file = UploadedFile(
#         file_id=file_id,
#         file_name=file.filename,
#         file_type="csv",
#         storage_path=storage_path
#     )
#     db.add(db_file)
#     db.commit()
    
#     return FileUploadResponse(
#         file_id=file_id,
#         file_name=file.filename,
#         file_type="csv",
#         message="CSV file uploaded successfully"
#     )

# @app.post("/upload/image", response_model=FileUploadResponse)
# async def upload_image(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db)
# ):
#     """Upload an image file"""
#     # Validate file extension
#     if not any(file.filename.lower().endswith(ext) for ext in settings.ALLOWED_IMAGE_EXTENSIONS):
#         raise HTTPException(status_code=400, detail="Invalid file type. Only image files allowed.")
    
#     # Upload file
#     file_id, storage_path = await storage_service.upload_file(file, "image")
    
#     # Save metadata to database
#     db_file = UploadedFile(
#         file_id=file_id,
#         file_name=file.filename,
#         file_type="image",
#         storage_path=storage_path
#     )
#     db.add(db_file)
#     db.commit()
    
#     return FileUploadResponse(
#         file_id=file_id,
#         file_name=file.filename,
#         file_type="image",
#         message="Image file uploaded successfully"
#     )

# def process_report_generation(
#     report_id: str,
#     csv_paths: List[str],
#     image_paths: List[str],
#     description: str,
#     db: Session
# ):
#     """Background task to generate report"""
#     try:
#         # Update status to processing
#         report = db.query(Report).filter(Report.report_id == report_id).first()
#         report.status = "processing"
#         db.commit()
        
#         # Generate report
#         result = report_service.generate_report(csv_paths, image_paths, description)
        
#         if result["success"]:
#             # Store embedding
#             report_service.store_report_embedding(report_id, result["data"])
            
#             # Update database
#             report.status = "completed"
#             report.result = result["data"]
#             report.updated_at = datetime.utcnow()
#             db.commit()
#         else:
#             report.status = "failed"
#             report.error_message = result.get("error", "Unknown error")
#             db.commit()
    
#     except Exception as e:
#         report = db.query(Report).filter(Report.report_id == report_id).first()
#         report.status = "failed"
#         report.error_message = str(e)
#         db.commit()

# @app.post("/generate-report", response_model=GenerateReportResponse)
# async def generate_report(
#     request: GenerateReportRequest,
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(get_db)
# ):
#     """Generate a business report from uploaded files"""
#     # Validate file IDs exist
#     csv_files = db.query(UploadedFile).filter(
#         UploadedFile.file_id.in_(request.csv_file_ids)
#     ).all()
    
#     image_files = db.query(UploadedFile).filter(
#         UploadedFile.file_id.in_(request.image_file_ids)
#     ).all()
    
#     if len(csv_files) != len(request.csv_file_ids):
#         raise HTTPException(status_code=404, detail="Some CSV files not found")
    
#     if len(image_files) != len(request.image_file_ids):
#         raise HTTPException(status_code=404, detail="Some image files not found")
    
#     # Create report record
#     report_id = str(uuid.uuid4())
#     report = Report(
#         report_id=report_id,
#         status="pending"
#     )
#     db.add(report)
#     db.commit()
    
#     # Get file paths
#     csv_paths = [storage_service.get_file_path(f.storage_path) for f in csv_files]
#     image_paths = [storage_service.get_file_path(f.storage_path) for f in image_files]
    
#     # Add background task
#     background_tasks.add_task(
#         process_report_generation,
#         report_id,
#         csv_paths,
#         image_paths,
#         request.description,
#         db
#     )
    
#     return GenerateReportResponse(
#         report_id=report_id,
#         message="Report generation started",
#         status="pending"
#     )

# @app.get("/report/{report_id}", response_model=ReportResponse)
# async def get_report(report_id: str, db: Session = Depends(get_db)):
#     """Get report by ID"""
#     report = db.query(Report).filter(Report.report_id == report_id).first()
    
#     if not report:
#         raise HTTPException(status_code=404, detail="Report not found")
    
#     # Convert result to ReportData if completed
#     data = None
#     if report.status == "completed" and report.result:
#         data = ReportData(**report.result)
    
#     return ReportResponse(
#         report_id=report.report_id,
#         status=report.status,
#         data=data,
#         error_message=report.error_message,
#         created_at=report.created_at,
#         updated_at=report.updated_at
#     )

# @app.get("/report/{report_id}/pdf")
# async def get_report_pdf(report_id: str, db: Session = Depends(get_db)):
#     """Generate and download PDF report"""
#     report = db.query(Report).filter(Report.report_id == report_id).first()
    
#     if not report:
#         raise HTTPException(status_code=404, detail="Report not found")
    
#     if report.status != "completed":
#         raise HTTPException(status_code=400, detail="Report not ready yet")
    
#     # Generate PDF
#     pdf_buffer = PDFService.generate_report_pdf(report.result, report_id)
    
#     return StreamingResponse(
#         pdf_buffer,
#         media_type="application/pdf",
#         headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"}
#     )

# @app.get("/reports/search")
# async def search_reports(query: str, limit: int = 5):
#     """Search for similar reports using vector similarity"""
#     results = report_service.search_similar_reports(query, limit)
#     return {"query": query, "results": results}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List, Optional
import tempfile
import os
from pathlib import Path

from config import settings
from models import ReportData
from services.report_service import ReportService
from services.pdf_service import PDFService

# Initialize FastAPI
app = FastAPI(
    title="Vision-Language Report Generator (Simple)",
    version="2.0.0",
    description="Upload CSV and images, get instant report!"
)

# Initialize services
report_service = ReportService()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Vision-Language Report Generator API (Simplified)",
        "version": "2.0.0",
        "status": "running",
        "usage": "POST /generate-report with CSV and image files"
    }

@app.post("/generate-report")
async def generate_report_simple(
    csv_files: List[UploadFile] = File(..., description="Upload one or more CSV files"),
    image_files: Optional[List[UploadFile]] = File(None, description="Upload one or more image files (optional)"),
    description: str = Form(..., description="Describe what kind of report you want")
):
    """
    Upload files and get report directly in response
    
    - **csv_files**: Upload CSV files (required)
    - **image_files**: Upload images (optional)
    - **description**: What analysis you want
    
    Returns: Complete JSON report with metrics, trends, recommendations
    """
    
    temp_csv_paths = []
    temp_image_paths = []
    
    try:
        # Save CSV files temporarily
        for csv_file in csv_files:
            if not csv_file.filename.endswith('.csv'):
                raise HTTPException(status_code=400, detail=f"Invalid file: {csv_file.filename}. Only CSV files allowed.")
            
            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False)
            content = await csv_file.read()
            temp_file.write(content)
            temp_file.close()
            temp_csv_paths.append(temp_file.name)
        
        # Save image files temporarily (if provided)
        if image_files:
            for image_file in image_files:
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
                if not any(image_file.filename.lower().endswith(ext) for ext in allowed_extensions):
                    raise HTTPException(status_code=400, detail=f"Invalid file: {image_file.filename}. Only images allowed.")
                
                # Create temp file
                suffix = Path(image_file.filename).suffix
                temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix=suffix, delete=False)
                content = await image_file.read()
                temp_file.write(content)
                temp_file.close()
                temp_image_paths.append(temp_file.name)
        
        # Generate report
        result = report_service.generate_report(
            csv_file_paths=temp_csv_paths,
            image_file_paths=temp_image_paths,
            description=description
        )
        
        print(result)
        
        if result["success"]:
            return JSONResponse(content={
                "status": "success",
                "message": "Report generated successfully",
                "data": result["data"]
            })
        else:
            raise HTTPException(status_code=500, detail=f"Report generation failed: {result.get('error')}")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
    
    finally:
        # Cleanup temp files
        for path in temp_csv_paths:
            try:
                os.unlink(path)
            except:
                pass
        for path in temp_image_paths:
            try:
                os.unlink(path)
            except:
                pass

@app.post("/generate-report-pdf")
async def generate_report_with_pdf(
    csv_files: List[UploadFile] = File(..., description="Upload one or more CSV files"),
    image_files: Optional[List[UploadFile]] = File(None, description="Upload one or more image files (optional)"),
    description: str = Form(..., description="Describe what kind of report you want")
):
    """
    Upload files and get PDF report directly
    
    Returns: PDF file download
    """
    
    temp_csv_paths = []
    temp_image_paths = []
    
    try:
        # Save CSV files temporarily
        for csv_file in csv_files:
            if not csv_file.filename.endswith('.csv'):
                raise HTTPException(status_code=400, detail=f"Invalid file: {csv_file.filename}. Only CSV files allowed.")
            
            temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False)
            content = await csv_file.read()
            temp_file.write(content)
            temp_file.close()
            temp_csv_paths.append(temp_file.name)
        
        # Save image files temporarily (if provided)
        if image_files:
            for image_file in image_files:
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
                if not any(image_file.filename.lower().endswith(ext) for ext in allowed_extensions):
                    raise HTTPException(status_code=400, detail=f"Invalid file: {image_file.filename}. Only images allowed.")
                
                suffix = Path(image_file.filename).suffix
                temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix=suffix, delete=False)
                content = await image_file.read()
                temp_file.write(content)
                temp_file.close()
                temp_image_paths.append(temp_file.name)
        
        # Generate report
        result = report_service.generate_report(
            csv_file_paths=temp_csv_paths,
            image_file_paths=temp_image_paths,
            description=description
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Report generation failed: {result.get('error')}")
        
        # Generate PDF
        pdf_buffer = PDFService.generate_report_pdf(result["data"], "instant-report")
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=business_report.pdf"}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
    
    finally:
        # Cleanup temp files
        for path in temp_csv_paths:
            try:
                os.unlink(path)
            except:
                pass
        for path in temp_image_paths:
            try:
                os.unlink(path)
            except:
                pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)