# Vision-Language Report Generator

AI-powered backend system that generates structured business reports from CSV data and images using Google Gemini.

**Two Workflows Available:**
1. **Multi-Step Workflow** - Upload files → Get IDs → Generate report → Poll status (with database storage)
2. **Direct Workflow** - Upload files → Get instant report (no database required)

---

## 📋 Project Overview

This system analyzes CSV files and images (charts, infographics) to generate comprehensive business reports with:
- Executive summaries
- Key performance metrics
- Trend analysis
- Data correlations
- Actionable recommendations
- Visual insights

**Built with:** FastAPI, Google Gemini AI, PostgreSQL, Qdrant, LangChain

---

## 🎯 Features

### Core Features
- ✅ Multi-file CSV upload and analysis
- ✅ Image analysis (charts, infographics, documents)
- ✅ AI-powered insights using Google Gemini (vision + text)
- ✅ Structured JSON report generation
- ✅ PDF report export with professional formatting
- ✅ Vector similarity search across reports (Qdrant)
- ✅ RESTful API with Swagger documentation
- ✅ Database storage with file tracking (PostgreSQL)
- ✅ Background task processing
- ✅ Two workflow options (database or instant)

### Tech Stack
- **Backend:** FastAPI
- **AI Models:** Google Gemini 2.0 Flash (multimodal - vision + text)
- **Orchestration:** LangChain
- **Database:** PostgreSQL
- **Vector Store:** Qdrant
- **Storage:** AWS S3 / Local filesystem
- **PDF Generation:** ReportLab

---

## 📁 Project Structure

```
vision-language-report-generator/
│
├── main.py                      # FastAPI application (10 endpoints)
├── config.py                    # Configuration settings
├── database.py                  # Database models
├── models.py                    # Pydantic schemas
├── requirements.txt             # Dependencies
├── .env.example                # Environment template
│
├── services/
│   ├── gemini_service.py       # Gemini AI (vision + text)
│   ├── csv_service.py          # CSV analysis
│   ├── report_service.py       # Report generation
│   ├── pdf_service.py          # PDF creation
│   ├── qdrant_service.py       # Vector search
│   ├── storage_service.py      # File storage (S3/Local)
│   └── langchain_agent.py      # LangChain orchestration
│
├── storage/                     # Local file storage
├── Dockerfile                   # Docker configuration
└── docker-compose.yml          # Multi-container setup
```

---

## ⚙️ Setup Instructions

### Prerequisites

- **Python:** 3.9 or higher
- **PostgreSQL:** 13 or higher
- **Qdrant:** Latest version
- **Google Gemini API Key** (free from Google AI Studio)

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd vision-language-report-generator
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Setup PostgreSQL Database

```bash
# Create database
createdb reportdb

# Or using psql:
psql -U postgres
CREATE DATABASE reportdb;
CREATE USER reportuser WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE reportdb TO reportuser;
\q
```

### Step 5: Setup Qdrant Vector Database

**Option A: Using Docker (Recommended)**
```bash
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant
```

**Option B: Install Standalone**
```bash
# Follow instructions at: https://qdrant.tech/documentation/install/
```

### Step 6: Get Google Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Click **"Create API Key"**
3. Copy your API key (starts with `AIza...`)

**Note:** Gemini offers a generous free tier (1,500 requests/day)

### Step 7: Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env file with your settings
nano .env
```

**Required Environment Variables:**

```bash
# Google Gemini API Key (Required)
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# Database Configuration
DATABASE_URL=postgresql://reportuser:your_password@localhost:5432/reportdb

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=reports_collection

# Storage Configuration
USE_LOCAL_STORAGE=true
LOCAL_STORAGE_PATH=./storage

# AWS S3 (Optional - for production)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# App Settings
DEBUG=true
```

### Step 8: Initialize Database Tables

The application will automatically create tables on first run.

### Step 9: Start the Application

```bash
python main.py
```

**Application will be running at:**
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🐳 Docker Setup (Alternative)

### Using Docker Compose

```bash
# Create .env file first
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

This will start:
- FastAPI application (port 8000)
- PostgreSQL database (port 5432)
- Qdrant vector store (port 6333)

---

## 📖 Usage Instructions

### 🔄 Workflow 1: Multi-Step (With Database Storage)

**Use this when you need:**
- File history and tracking
- Background processing
- Report versioning
- Vector similarity search
- Multiple users

#### Step-by-Step Process:

**1. Upload CSV File**
```bash
curl -X POST "http://localhost:8000/upload/csv" \
  -F "file=@sales_data.csv"

# Response:
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "file_name": "sales_data.csv",
  "file_type": "csv",
  "message": "CSV file uploaded successfully"
}
# Save this file_id!
```

**2. Upload Image (Optional)**
```bash
curl -X POST "http://localhost:8000/upload/image" \
  -F "file=@revenue_chart.png"

# Response:
{
  "file_id": "660e8400-e29b-41d4-a716-446655440001",
  "file_name": "revenue_chart.png",
  "file_type": "image",
  "message": "Image file uploaded successfully"
}
# Save this file_id!
```

**3. Generate Report**
```bash
curl -X POST "http://localhost:8000/generate-report" \
  -H "Content-Type: application/json" \
  -d '{
    "csv_file_ids": ["550e8400-e29b-41d4-a716-446655440000"],
    "image_file_ids": ["660e8400-e29b-41d4-a716-446655440001"],
    "description": "Analyze Q4 sales performance and identify growth opportunities"
  }'

# Response:
{
  "report_id": "770e8400-e29b-41d4-a716-446655440002",
  "message": "Report generation started. Use GET /report/{report_id} to check status.",
  "status": "pending"
}
# Save this report_id!
```

**4. Check Report Status**
```bash
curl -X GET "http://localhost:8000/report/770e8400-e29b-41d4-a716-446655440002"

# While processing:
{
  "report_id": "770e8400-e29b-41d4-a716-446655440002",
  "status": "processing",
  "data": null,
  ...
}

# When completed:
{
  "report_id": "770e8400-e29b-41d4-a716-446655440002",
  "status": "completed",
  "data": {
    "summary": "...",
    "key_metrics": [...],
    "trends": [...],
    ...
  }
}
```

**5. Download PDF**
```bash
curl -X GET "http://localhost:8000/report/770e8400-e29b-41d4-a716-446655440002/pdf" \
  --output report.pdf
```

**6. Search Similar Reports**
```bash
curl -X GET "http://localhost:8000/reports/search?query=sales+trends&limit=5"
```

#### Python Example (Multi-Step):

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Upload CSV
with open('sales_data.csv', 'rb') as f:
    response = requests.post(f"{BASE_URL}/upload/csv", files={'file': f})
    csv_file_id = response.json()['file_id']
    print(f"CSV uploaded: {csv_file_id}")

# 2. Upload image
with open('chart.png', 'rb') as f:
    response = requests.post(f"{BASE_URL}/upload/image", files={'file': f})
    image_file_id = response.json()['file_id']
    print(f"Image uploaded: {image_file_id}")

# 3. Generate report
response = requests.post(
    f"{BASE_URL}/generate-report",
    json={
        'csv_file_ids': [csv_file_id],
        'image_file_ids': [image_file_id],
        'description': 'Analyze Q4 sales performance'
    }
)
report_id = response.json()['report_id']
print(f"Report generating: {report_id}")

# 4. Poll for completion
while True:
    response = requests.get(f"{BASE_URL}/report/{report_id}")
    data = response.json()
    
    if data['status'] == 'completed':
        print("\n✓ Report completed!")
        print(f"Summary: {data['data']['summary'][:200]}...")
        break
    elif data['status'] == 'failed':
        print(f"✗ Failed: {data['error_message']}")
        break
    
    print("Processing...")
    time.sleep(3)

# 5. Download PDF
response = requests.get(f"{BASE_URL}/report/{report_id}/pdf")
with open('report.pdf', 'wb') as f:
    f.write(response.content)
print("PDF saved: report.pdf")
```

---

### ⚡ Workflow 2: Direct (Instant Reports)

**Use this when you need:**
- Quick one-time analysis
- No file history needed
- Instant results
- Simpler workflow

#### One-Step Process:

**Get JSON Report Instantly:**
```bash
curl -X POST "http://localhost:8000/generate-report-instant" \
  -F "csv_files=@sales_data.csv" \
  -F "image_files=@chart.png" \
  -F "description=Analyze Q4 sales performance"

# Instant Response with full report!
{
  "status": "success",
  "message": "Report generated successfully",
  "data": {
    "summary": "...",
    "key_metrics": [...],
    "trends": [...],
    ...
  }
}
```

**Get PDF Report Instantly:**
```bash
curl -X POST "http://localhost:8000/generate-report-instant-pdf" \
  -F "csv_files=@sales_data.csv" \
  -F "description=Generate executive summary" \
  -o report.pdf
```

#### Python Example (Direct):

```python
import requests

# One call - instant report!
with open('sales_data.csv', 'rb') as csv_file:
    files = {'csv_files': csv_file}
    data = {'description': 'Analyze sales trends'}
    
    response = requests.post(
        'http://localhost:8000/generate-report-instant',
        files=files,
        data=data
    )
    
    if response.status_code == 200:
        report = response.json()
        print(f"Summary: {report['data']['summary']}")
        print(f"Metrics: {report['data']['key_metrics']}")
```

---

## 📊 API Endpoints Reference

### Multi-Step Workflow Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload/csv` | POST | Upload CSV file → Get `file_id` |
| `/upload/image` | POST | Upload image → Get `file_id` |
| `/generate-report` | POST | Generate report from file IDs → Get `report_id` |
| `/report/{report_id}` | GET | Check status & get report data |
| `/report/{report_id}/pdf` | GET | Download PDF report |
| `/reports/search` | GET | Search similar reports (vector search) |
| `/files/list` | GET | List all uploaded files |
| `/reports/list` | GET | List all reports |

### Direct Workflow Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate-report-instant` | POST | Upload files → Get instant JSON report |
| `/generate-report-instant-pdf` | POST | Upload files → Download PDF instantly |

### General Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/docs` | GET | Swagger documentation |

---

## 📋 Complete Usage Examples

### Using Swagger UI (Interactive)

1. Open: http://localhost:8000/docs
2. Try any endpoint with "Try it out" button
3. Upload files directly in browser
4. See instant results

### Example CSV Input

**sales_data.csv:**
```csv
Month,Revenue,Customers,Orders,Avg_Order_Value
January,180000,450,520,346
February,195000,480,545,358
March,210000,520,580,362
April,225000,550,610,369
```

### Example Response (Both Workflows)

```json
{
  "status": "success",
  "data": {
    "summary": "Q1 demonstrates strong growth with 25% revenue increase...",
    
    "key_metrics": [
      {"name": "Total Revenue", "value": 810000, "unit": "USD"},
      {"name": "Revenue Growth", "value": 25, "unit": "%"},
      {"name": "Total Customers", "value": 2000, "unit": "customers"}
    ],
    
    "trends": [
      {
        "description": "Consistent month-over-month revenue growth",
        "direction": "up",
        "impact": "positive"
      }
    ],
    
    "correlations": [
      "Customer growth correlates with 15% increase in order volume"
    ],
    
    "recommendations": [
      {
        "priority": "high",
        "action": "Implement customer retention program",
        "rationale": "Strong acquisition needs retention strategies"
      }
    ],
    
    "visual_insights": [
      "Revenue chart shows clear upward trajectory"
    ],
    
    "generated_at": "2024-12-13T10:30:00Z"
  }
}
```

---

## 🔧 Configuration

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | Yes | - | Google Gemini API key |
| `GEMINI_MODEL` | No | `gemini-2.0-flash-exp` | Gemini model version |
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `QDRANT_HOST` | Yes | `localhost` | Qdrant server host |
| `QDRANT_PORT` | Yes | `6333` | Qdrant server port |
| `QDRANT_COLLECTION` | No | `reports_collection` | Collection name |
| `USE_LOCAL_STORAGE` | No | `true` | Use local storage vs S3 |
| `LOCAL_STORAGE_PATH` | No | `./storage` | Local storage directory |
| `AWS_ACCESS_KEY_ID` | No | - | AWS S3 access key |
| `AWS_SECRET_ACCESS_KEY` | No | - | AWS S3 secret key |
| `S3_BUCKET_NAME` | No | - | AWS S3 bucket name |
| `DEBUG` | No | `true` | Enable debug mode |

### Storage Options

**Local Storage (Development):**
```bash
USE_LOCAL_STORAGE=true
LOCAL_STORAGE_PATH=./storage
```

**AWS S3 (Production):**
```bash
USE_LOCAL_STORAGE=false
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket
```

---

## 🧪 Testing

### Test Multi-Step Workflow

```bash
# 1. Upload file
FILE_ID=$(curl -X POST http://localhost:8000/upload/csv \
  -F "file=@test.csv" | jq -r '.file_id')

# 2. Generate report
REPORT_ID=$(curl -X POST http://localhost:8000/generate-report \
  -H "Content-Type: application/json" \
  -d "{\"csv_file_ids\": [\"$FILE_ID\"], \"image_file_ids\": [], \"description\": \"Test\"}" \
  | jq -r '.report_id')

# 3. Check status
curl http://localhost:8000/report/$REPORT_ID | jq

# 4. Download PDF
curl http://localhost:8000/report/$REPORT_ID/pdf -o test.pdf
```

### Test Direct Workflow

```bash
# Instant JSON report
curl -X POST http://localhost:8000/generate-report-instant \
  -F "csv_files=@test.csv" \
  -F "description=Test analysis" | jq

# Instant PDF
curl -X POST http://localhost:8000/generate-report-instant-pdf \
  -F "csv_files=@test.csv" \
  -F "description=Test report" \
  -o instant_report.pdf
```

---

## 🚀 Deployment

### Option 1: Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Add PostgreSQL
railway add postgresql

# Set environment variables
railway variables set GOOGLE_API_KEY="your_key"

# Deploy
railway up

# Get URL
railway domain
```

### Option 2: Render

1. Push code to GitHub
2. Go to https://render.com
3. Create "Web Service" from GitHub repo
4. Add PostgreSQL database
5. Set environment variables
6. Deploy

### Option 3: Docker

```bash
# Using docker-compose
docker-compose up -d

# Or build manually
docker build -t report-generator .
docker run -d -p 8000:8000 \
  -e GOOGLE_API_KEY="your_key" \
  -e DATABASE_URL="your_db_url" \
  report-generator
```

---

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list                # macOS

# Test connection
psql -h localhost -U reportuser -d reportdb

# Check DATABASE_URL in .env
echo $DATABASE_URL
```

### Qdrant Connection Issues

```bash
# Check if Qdrant is running
curl http://localhost:6333/health

# View Qdrant logs
docker logs qdrant

# Restart Qdrant
docker restart qdrant
```

### Gemini API Issues

**Invalid API Key:**
- Verify key in .env: `cat .env | grep GOOGLE_API_KEY`
- Check key at https://makersuite.google.com/app/apikey
- Ensure key starts with `AIza`

**Rate Limit Exceeded:**
- Free tier: 60 requests/minute, 1,500/day
- Wait 60 seconds or upgrade tier

### Background Task Not Processing

```bash
# Check logs for errors
tail -f uvicorn.log

# Verify database connection
# Check report status in database
psql -d reportdb -c "SELECT report_id, status FROM reports ORDER BY created_at DESC LIMIT 5;"
```

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --port 8001
```

---

## 💰 Cost Information

### Google Gemini Pricing

**Free Tier:**
- 60 requests per minute
- 1,500 requests per day
- Perfect for development and small-scale production

**Paid Tier:**
- Pay-as-you-go
- Much cheaper than OpenAI
- See: https://ai.google.dev/pricing

### Infrastructure Costs

**Development (Local):**
- PostgreSQL: $0 (local)
- Qdrant: $0 (local)
- Gemini API: $0 (free tier)
- **Total: $0/month**

**Production (Cloud):**
- Hosting (Railway/Render): $5-10/month
- PostgreSQL (managed): $15/month
- Qdrant Cloud: $25/month (or $0 self-hosted)
- Gemini API: $0-20/month
- **Total: ~$45-70/month**

---

## 🎯 When to Use Which Workflow?

### Use Multi-Step Workflow When:
- ✅ Building production system
- ✅ Need file history and tracking
- ✅ Multiple users accessing reports
- ✅ Want to search past reports
- ✅ Need background processing for large files
- ✅ Require report versioning

### Use Direct Workflow When:
- ✅ Quick one-time analysis
- ✅ Prototyping or demos
- ✅ Don't need file history
- ✅ Simple use cases
- ✅ Want fastest results
- ✅ No database setup available

**Both workflows produce identical report quality!**

---

## 📚 Additional Resources

### Documentation
- **Google Gemini:** https://ai.google.dev/
- **FastAPI:** https://fastapi.tiangolo.com/
- **PostgreSQL:** https://www.postgresql.org/docs/
- **Qdrant:** https://qdrant.tech/documentation/
- **LangChain:** https://python.langchain.com/

### API Testing
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Test with Postman or Insomnia

---

## 📝 License

MIT License - Free to use for personal and commercial projects

---

## 🎉 Quick Start Summary

**Multi-Step Workflow:**
```bash
# Setup
pip install -r requirements.txt
# Setup PostgreSQL + Qdrant
echo "GOOGLE_API_KEY=your_key" > .env
python main.py

# Use
# 1. Upload files → Get file_ids
# 2. Generate report → Get report_id  
# 3. Check status → Get results
```

**Direct Workflow:**
```bash
# Setup (same as above)
pip install -r requirements.txt
echo "GOOGLE_API_KEY=your_key" > .env
python main.py

# Use
# 1. Upload files → Get instant report!
```

**Visit http://localhost:8000/docs to try both workflows interactively!** 🚀

---

## 🙏 Acknowledgments

- **Google Gemini** - Free multimodal AI
- **FastAPI** - Modern Python framework
- **PostgreSQL** - Reliable database
- **Qdrant** - Vector search engine
- **LangChain** - AI orchestration
- **ReportLab** - PDF generation

---

**Ready to generate AI-powered business reports with both flexible workflows!** 🎯