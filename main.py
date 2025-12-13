from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks, Form
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
import tempfile
import os
from pathlib import Path

from config import settings
from database import get_db, init_db, UploadedFile, Report
from models import (
    FileUploadResponse, GenerateReportRequest, 
    GenerateReportResponse, ReportResponse, ReportData
)
from services.storage_service import StorageService
from services.report_service import ReportService
from services.pdf_service import PDFService

# Initialize FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered business report generator using Google Gemini (vision + language)"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
storage_service = StorageService()
report_service = ReportService()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("=" * 60)
    print(" Vision-Language Report Generator")
    print(" Powered by Google Gemini (FREE & Fast!)")
    print("=" * 60)
    print("Database initialized")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Vision-Language Report Generator API",
        "version": settings.APP_VERSION,
        "status": "running",
        "ai_model": "Google Gemini",
        "features": [
            "Multi-step workflow (upload → generate → retrieve)",
            "Direct workflow (upload files → instant report)",
            "Background processing",
            "Database storage",
            "Vector search",
            "PDF generation"
        ]
    }

@app.post("/upload/csv", response_model=FileUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate file extension
    if not any(file.filename.lower().endswith(ext) for ext in settings.ALLOWED_CSV_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files allowed.")
    
    # Upload file
    file_id, storage_path = await storage_service.upload_file(file, "csv")
    
    # Save metadata to database
    db_file = UploadedFile(
        file_id=file_id,
        file_name=file.filename,
        file_type="csv",
        storage_path=storage_path
    )
    db.add(db_file)
    db.commit()
    
    return FileUploadResponse(
        file_id=file_id,
        file_name=file.filename,
        file_type="csv",
        message="CSV file uploaded successfully"
    )

@app.post("/upload/image", response_model=FileUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Validate file extension
    if not any(file.filename.lower().endswith(ext) for ext in settings.ALLOWED_IMAGE_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Invalid file type. Only image files allowed.")
    
    # Upload file
    file_id, storage_path = await storage_service.upload_file(file, "image")
    
    # Save metadata to database
    db_file = UploadedFile(
        file_id=file_id,
        file_name=file.filename,
        file_type="image",
        storage_path=storage_path
    )
    db.add(db_file)
    db.commit()
    
    return FileUploadResponse(
        file_id=file_id,
        file_name=file.filename,
        file_type="image",
        message="Image file uploaded successfully"
    )

def process_report_generation(
    report_id: str,
    csv_paths: List[str],
    image_paths: List[str],
    description: str,
    db: Session
):

    try:
        print(f"\n Processing report: {report_id}")
        
        # Update status to processing
        report = db.query(Report).filter(Report.report_id == report_id).first()
        report.status = "processing"
        db.commit()
        
        # Generate report using Gemini
        print("→ Generating report with Gemini AI...")
        result = report_service.generate_report(csv_paths, image_paths, description)
        
        if result["success"]:
            print("✓ Report generated successfully!")
            
            # Store embedding in Qdrant
            print("→ Storing embeddings in Qdrant...")
            report_service.store_report_embedding(report_id, result["data"])
            
            # Update database
            report.status = "completed"
            report.result = result["data"]
            report.updated_at = datetime.utcnow()
            db.commit()
            print(f"✓ Report {report_id} completed and stored")
        else:
            print(f"✗ Report generation failed: {result.get('error')}")
            report.status = "failed"
            report.error_message = result.get("error", "Unknown error")
            db.commit()
    
    except Exception as e:
        print(f"✗ Error processing report: {str(e)}")
        report = db.query(Report).filter(Report.report_id == report_id).first()
        report.status = "failed"
        report.error_message = str(e)
        db.commit()

@app.post("/generate-report", response_model=GenerateReportResponse)
async def generate_report(
    request: GenerateReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    # Validate file IDs exist
    csv_files = db.query(UploadedFile).filter(
        UploadedFile.file_id.in_(request.csv_file_ids)
    ).all()
    
    image_files = db.query(UploadedFile).filter(
        UploadedFile.file_id.in_(request.image_file_ids)
    ).all()
    
    if len(csv_files) != len(request.csv_file_ids):
        raise HTTPException(status_code=404, detail="Some CSV files not found")
    
    # if len(image_files) != len(request.image_file_ids):
    #     raise HTTPException(status_code=404, detail="Some image files not found")
    
    # Create report record
    report_id = str(uuid.uuid4())
    report = Report(
        report_id=report_id,
        status="pending"
    )
    db.add(report)
    db.commit()
    
    # Get file paths
    csv_paths = [storage_service.get_file_path(f.storage_path) for f in csv_files]
    image_paths = [storage_service.get_file_path(f.storage_path) for f in image_files]
    
    # Add background task
    background_tasks.add_task(
        process_report_generation,
        report_id,
        csv_paths,
        image_paths,
        request.description,
        db
    )
    
    return GenerateReportResponse(
        report_id=report_id,
        message="Report generation started. Use GET /report/{report_id} to check status.",
        status="pending"
    )

@app.get("/report/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.report_id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Convert result to ReportData if completed
    data = None
    if report.status == "completed" and report.result:
        data = ReportData(**report.result)
    
    return ReportResponse(
        report_id=report.report_id,
        status=report.status,
        data=data,
        error_message=report.error_message,
        created_at=report.created_at,
        updated_at=report.updated_at
    )

@app.get("/report/{report_id}/pdf")
async def get_report_pdf(report_id: str, db: Session = Depends(get_db)):

    report = db.query(Report).filter(Report.report_id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report.status != "completed":
        raise HTTPException(status_code=400, detail=f"Report not ready yet. Status: {report.status}")
    
    # Generate PDF
    pdf_buffer = PDFService.generate_report_pdf(report.result, report_id)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"}
    )

@app.get("/reports/search")
async def search_reports(query: str, limit: int = 5):

    results = report_service.search_similar_reports(query, limit)
    return {"query": query, "results": results, "count": len(results)}

@app.post("/generate-report-instant")
async def generate_report_instant(
    csv_files: List[UploadFile] = File(..., description="Upload one or more CSV files"),
    image_files: List[UploadFile] = File(None, description="Upload images (optional)"),
    description: str = Form(..., description="Describe what analysis you want")
):

    temp_csv_paths = []
    temp_image_paths = []
    
    try:
        print(f"\n📥 Instant report request: {len(csv_files)} CSV(s), {len(image_files or [])} image(s)")
        
        # Save CSV files temporarily
        for csv_file in csv_files:
            if not csv_file.filename.endswith('.csv'):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid file: {csv_file.filename}. Only .csv files allowed."
                )
            
            temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False)
            content = await csv_file.read()
            temp_file.write(content)
            temp_file.close()
            temp_csv_paths.append(temp_file.name)
            print(f"  ✓ Saved: {csv_file.filename}")
        
        # Save image files temporarily (if provided)
        if image_files:
            for image_file in image_files:
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
                if not any(image_file.filename.lower().endswith(ext) for ext in allowed_extensions):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid file: {image_file.filename}. Allowed: JPG, PNG, WEBP"
                    )
                
                suffix = Path(image_file.filename).suffix
                temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix=suffix, delete=False)
                content = await image_file.read()
                temp_file.write(content)
                temp_file.close()
                temp_image_paths.append(temp_file.name)
                print(f"  ✓ Saved: {image_file.filename}")
        
        # Generate report using Gemini
        print("🤖 Processing with Gemini AI...")
        result = report_service.generate_report(
            csv_file_paths=temp_csv_paths,
            image_file_paths=temp_image_paths,
            description=description
        )
        
        if result["success"]:
            print("✓ Report generated successfully!")
            return JSONResponse(content={
                "status": "success",
                "message": "Report generated successfully",
                "data": result["data"],
                "ai_model": "Google Gemini"
            })
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Report generation failed: {result.get('error')}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    finally:
        # Cleanup temp files
        for path in temp_csv_paths + temp_image_paths:
            try:
                os.unlink(path)
            except:
                pass

@app.post("/generate-report-instant-pdf")
async def generate_report_instant_pdf(
    csv_files: List[UploadFile] = File(..., description="Upload one or more CSV files"),
    image_files: List[UploadFile] = File(None, description="Upload images (optional)"),
    description: str = Form(..., description="Describe what analysis you want")
):

    temp_csv_paths = []
    temp_image_paths = []
    
    try:
        # Save CSV files temporarily
        for csv_file in csv_files:
            if not csv_file.filename.endswith('.csv'):
                raise HTTPException(status_code=400, detail=f"Invalid file: {csv_file.filename}")
            
            temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False)
            content = await csv_file.read()
            temp_file.write(content)
            temp_file.close()
            temp_csv_paths.append(temp_file.name)
        
        # Save image files temporarily
        if image_files:
            for image_file in image_files:
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
                if not any(image_file.filename.lower().endswith(ext) for ext in allowed_extensions):
                    raise HTTPException(status_code=400, detail=f"Invalid image: {image_file.filename}")
                
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
            raise HTTPException(status_code=500, detail=result.get('error'))
        
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
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup
        for path in temp_csv_paths + temp_image_paths:
            try:
                os.unlink(path)
            except:
                pass

# ==================== LIST & MANAGEMENT ENDPOINTS ====================

@app.get("/files/list")
async def list_files(
    file_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):

    query = db.query(UploadedFile)
    
    if file_type:
        query = query.filter(UploadedFile.file_type == file_type)
    
    files = query.order_by(UploadedFile.created_at.desc()).limit(limit).all()
    
    return {
        "files": [
            {
                "file_id": f.file_id,
                "file_name": f.file_name,
                "file_type": f.file_type,
                "created_at": f.created_at
            }
            for f in files
        ],
        "count": len(files)
    }

@app.get("/reports/list")
async def list_reports(
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Report)
    
    if status:
        query = query.filter(Report.status == status)
    
    reports = query.order_by(Report.created_at.desc()).limit(limit).all()
    
    return {
        "reports": [
            {
                "report_id": r.report_id,
                "status": r.status,
                "created_at": r.created_at,
                "updated_at": r.updated_at
            }
            for r in reports
        ],
        "count": len(reports)
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


