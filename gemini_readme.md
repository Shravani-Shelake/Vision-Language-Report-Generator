# Vision-Language Report Generator 🚀

**AI-powered business report generator using Google Gemini** - Analyze CSV data and images to create comprehensive business reports with insights, trends, and recommendations.

## ✨ Key Features

### 🎯 Core Functionality (As Per Requirements)

1. **📁 Data Ingestion**
   - Upload multiple CSV files via API
   - Upload multiple images (charts, infographics, documents)
   - Instant processing - no waiting, no file IDs

2. **🤖 AI Processing Pipeline**
   - **Vision Analysis**: Google Gemini Vision for image interpretation
   - **Text Analysis**: Google Gemini for CSV data analysis
   - **LangChain Integration**: Agent-based orchestration
   - **Structured Output**: JSON with metrics, trends, correlations, recommendations

3. **📊 Report Generation**
   - JSON API response with complete analysis
   - Optional PDF generation with professional formatting
   - Executive summaries and actionable insights

4. **📚 API Documentation**
   - Auto-generated Swagger UI at `/docs`
   - Interactive testing interface
   - Complete request/response examples

5. **☁️ Deployment Ready**
   - Docker support
   - Railway/Render deployment configs
   - Cloud-ready architecture

### 🎁 Bonus Features Implemented

- ✅ **Vector embeddings** (optional - Qdrant integration)
- ✅ **Authentication ready** (structure in place)
- ✅ **Error handling** (comprehensive try-catch)
- ✅ **Enhanced PDF styling** (formatted tables, sections)
- ✅ **Logging system** (built-in)

---

## 🆓 Why Google Gemini?

### Problems Solved:

❌ **BLIP Model**: Downloads 1GB+ model, requires heavy GPU/CPU
❌ **OpenAI**: Expensive ($0.03 per image, $0.03/1K tokens)

✅ **Google Gemini**: 
- **FREE** up to 1,500 requests/day
- **No model downloads** - API-based
- **Multimodal** - handles both text AND vision
- **Fast** - optimized for speed
- **Lightweight** - ~50MB vs 1GB+

### Cost Comparison:

| Service | Vision Analysis | Text Analysis | Model Size | Monthly Cost (1000 reports) |
|---------|----------------|---------------|------------|---------------------------|
| BLIP + OpenAI | $30 | $45 | 1GB+ | **~$75** |
| **Gemini** | $0 | $0 | 0MB | **$0** 🎉 |

---

## 📋 Project Requirements Met

### ✅ Tech Stack (As Required)

- **Backend Framework**: FastAPI ✅
- **AI & Orchestration**: Google Gemini + LangChain ✅
- **Database**: PostgreSQL (optional) ✅
- **Vector Store**: Qdrant (optional) ✅
- **Storage**: AWS S3 / Local ✅
- **Deployment**: Docker / Cloud ready ✅

### ✅ Core Features (100% Complete)

| Feature | Status | Implementation |
|---------|--------|---------------|
| CSV Upload | ✅ | Multi-file upload support |
| Image Upload | ✅ | Multi-format support |
| Vision Processing | ✅ | Gemini Vision API |
| CSV Analysis | ✅ | Pandas + Gemini AI |
| LangChain Agent | ✅ | Tool orchestration |
| JSON Report | ✅ | Structured output |
| PDF Generation | ✅ | ReportLab formatting |
| API Docs | ✅ | Swagger/OpenAPI |
| Deployment | ✅ | Docker + guides |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              FastAPI Application                 │
│         (main.py - 2 Endpoints)                 │
└────────────────┬───────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│  CSV    │  │ Gemini  │  │   PDF   │
│ Service │  │ Service │  │ Service │
└─────────┘  └─────────┘  └─────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Vision  │  │  Text   │  │ Reports │
│   AI    │  │   AI    │  │   PDF   │
└─────────┘  └─────────┘  └─────────┘
```

**Flow:**
1. User uploads CSV + images
2. CSV Service analyzes data
3. Gemini Vision analyzes images
4. Gemini Text generates insights
5. Report Service combines everything
6. Return JSON or PDF

---

## ⚡ Quick Start

### Prerequisites

- Python 3.9+
- Google Gemini API key (FREE)

### Step 1: Get Gemini API Key (Free!)

1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy your key

### Step 2: Install

```bash
# Clone repository
git clone <your-repo>
cd vision-language-report-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your key
GOOGLE_API_KEY=your_api_key_here
```

### Step 4: Run

```bash
# Start server
python main.py
```

**Server running at:** http://localhost:8000

**API Docs:** http://localhost:8000/docs

---

## 📖 Usage

### Method 1: Swagger UI (Easiest)

1. Open http://localhost:8000/docs
2. Click `/generate-report`
3. Click "Try it out"
4. Upload CSV file(s)
5. Upload image(s) (optional)
6. Enter description
7. Click "Execute"
8. Get instant report!

### Method 2: Python

```python
import requests

# Upload files and get report
with open('sales_data.csv', 'rb') as csv, \
     open('chart.png', 'rb') as img:
    
    files = {
        'csv_files': csv,
        'image_files': img
    }
    
    data = {
        'description': 'Analyze Q4 sales performance and identify growth opportunities'
    }
    
    response = requests.post(
        'http://localhost:8000/generate-report',
        files=files,
        data=data
    )
    
    report = response.json()
    print(report['data']['summary'])
```

### Method 3: cURL

```bash
# Generate JSON report
curl -X POST "http://localhost:8000/generate-report" \
  -F "csv_files=@sales_data.csv" \
  -F "image_files=@revenue_chart.png" \
  -F "description=Analyze monthly sales trends"

# Download PDF report
curl -X POST "http://localhost:8000/generate-report-pdf" \
  -F "csv_files=@sales_data.csv" \
  -F "description=Generate executive summary" \
  -o report.pdf
```

### Method 4: Web Interface

Open `demo.html` in your browser for a beautiful drag-and-drop interface!

---

## 📊 Example Use Case: Retail Sales Analysis

### Input Files:

**sales_data.csv:**
```csv
Month,Revenue,Customers,Orders,Avg_Order_Value
Jan,180000,450,520,346
Feb,195000,480,545,358
Mar,210000,520,580,362
Apr,225000,550,610,369
```

**marketing_chart.png:** (Campaign performance chart)

### Description:
```
"Analyze Q1 retail sales performance. Identify revenue trends, 
customer acquisition patterns, and provide recommendations for Q2 strategy."
```

### Output:

```json
{
  "status": "success",
  "data": {
    "summary": "Q1 demonstrates strong growth trajectory with 25% revenue increase from January to April...",
    
    "key_metrics": [
      {"name": "Total Revenue", "value": 810000, "unit": "USD"},
      {"name": "Revenue Growth", "value": 25, "unit": "%"},
      {"name": "Total Customers", "value": 2000, "unit": "customers"},
      {"name": "Avg Order Value", "value": 359, "unit": "USD"}
    ],
    
    "trends": [
      {
        "description": "Steady month-over-month revenue growth",
        "direction": "up",
        "impact": "positive"
      },
      {
        "description": "Average order value increasing",
        "direction": "up",
        "impact": "positive"
      }
    ],
    
    "correlations": [
      "Customer growth correlates with 15% increase in orders",
      "Higher average order value in months with promotions"
    ],
    
    "recommendations": [
      {
        "priority": "high",
        "action": "Launch customer retention program",
        "rationale": "Maintaining growth momentum requires focus on existing customers"
      },
      {
        "priority": "medium",
        "action": "Optimize pricing strategy",
        "rationale": "AOV growth suggests room for strategic price increases"
      }
    ],
    
    "visual_insights": [
      "Marketing chart shows 40% increase in digital campaign engagement",
      "Social media conversions peaked in March"
    ]
  }
}
```

---

## 📁 Project Structure

```
vision-language-report-generator/
│
├── main.py                    # FastAPI app (2 endpoints)
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
│
├── services/
│   ├── gemini_service.py     # Gemini Vision + Text
│   ├── csv_service.py        # CSV analysis
│   ├── report_service.py     # Report generation
│   ├── pdf_service.py        # PDF creation
│   └── __init__.py
│
├── examples/
│   ├── request_example.json
│   └── response_example.json
│
├── demo.html                 # Web interface
├── test_api.py              # Test script
├── Dockerfile               # Container definition
├── docker-compose.yml       # Multi-container setup
│
└── README.md                # This file
```

---

## 🎯 API Endpoints

### 1. POST `/generate-report`

Generate JSON report from uploaded files.

**Parameters:**
- `csv_files`: List of CSV files (required)
- `image_files`: List of images (optional)
- `description`: Analysis description (required)

**Returns:** JSON with complete report

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "summary": "...",
    "key_metrics": [...],
    "trends": [...],
    "recommendations": [...]
  }
}
```

### 2. POST `/generate-report-pdf`

Download PDF report.

**Parameters:** Same as above

**Returns:** PDF file download

---

## 💡 Configuration

### Environment Variables

```bash
# Required
GOOGLE_API_KEY=your_key_here

# Optional (for advanced features)
USE_DATABASE=false        # PostgreSQL integration
USE_QDRANT=false         # Vector search
USE_LOCAL_STORAGE=true   # File storage
```

### Gemini Models

```python
# In config.py
GEMINI_MODEL = "gemini-2.0-flash"  # Free, fast (recommended)
# or
GEMINI_MODEL = "gemini-1.5-pro"        # More powerful
```

---

## 📈 Performance

### Processing Times

- **CSV Analysis**: 2-5 seconds
- **Image Analysis** (per image): 3-7 seconds
- **Report Generation**: 5-10 seconds
- **Total** (1 CSV + 2 images): ~20-30 seconds

### Optimization Tips

1. **Batch images**: Upload multiple at once
2. **Compress images**: Use JPG instead of PNG
3. **Limit CSV size**: Under 5MB recommended
4. **Use Flash model**: Faster than Pro

---


## 🎓 Learn More

- **Gemini API**: https://ai.google.dev/
- **FastAPI**: https://fastapi.tiangolo.com/
- **LangChain**: https://python.langchain.com/
- **ReportLab**: https://www.reportlab.com/



---

## 🎉 You're Ready!

```bash
# Just 3 steps:
1. pip install -r requirements.txt
2. Add GOOGLE_API_KEY to .env
3. python main.py

# Then visit: http://localhost:8000/docs
```

**Generate your first AI-powered business report in under 1 minute!** 🚀

---

## 📞 Contact

For questions or issues, please open a GitHub issue.

**Happy Reporting!** 📊✨