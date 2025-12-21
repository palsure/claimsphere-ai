# Automated Claim Processing Agent

An AI-powered automated claim processing system that uses PaddleOCR-VL for document extraction and ERNIE for intelligent claim validation, categorization, and natural language queries.

## Problem Statement

Insurance companies, healthcare providers, and businesses waste significant time and resources on manual claim processing. This system solves:
- Manual claim data entry (time-consuming and error-prone)
- Inconsistent claim validation and categorization
- Difficult duplicate claim detection
- Slow claim approval workflows
- No natural language querying of claim history
- Multi-language claim document processing challenges

## Solution

An intelligent automated claim processing agent that combines:
- **PaddleOCR-VL**: Text and layout extraction from claim documents
- **ERNIE 4.5**: Understanding, validation, categorization, and natural language analysis
- **Modern Web Interface**: Clean dashboard with analytics and claim management

## Features

- 📄 **Multi-format Support**: PDF, JPG, PNG claim document processing
- 🤖 **Automatic Categorization**: AI-powered claim type classification
- ✅ **Claim Validation**: Automatic validation with error detection
- 🔍 **Duplicate Detection**: Identifies duplicate claims automatically
- 📊 **Analytics Dashboard**: Visual insights and claim processing trends
- 💬 **Natural Language Queries**: Ask questions about claims
- 🌍 **Multi-language Support**: Process claims in multiple languages
- ⚡ **Approval Workflows**: Streamlined claim approval/rejection process
- 📈 **Processing Metrics**: Track approval rates and processing times

## Technology Stack

- **Backend**: Python, FastAPI, PaddlePaddle
- **Frontend**: React/Next.js
- **OCR**: PaddleOCR-VL
- **AI Model**: ERNIE 4.5 (via Baidu AI Studio API)

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- Baidu AI Studio API key (for ERNIE)
- poppler-utils (for PDF processing): 
  - macOS: `brew install poppler`
  - Linux: `sudo apt-get install poppler-utils`

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ERNIE
```

2. Install system dependency (poppler for PDF processing):
```bash
# macOS
brew install poppler

# Linux
sudo apt-get install poppler-utils
```

3. Install backend dependencies:
```bash
pip install -r requirements.txt
```

**Note:** This will install all dependencies including PaddleOCR (may take a few minutes on first install).

4. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

5. Set up environment variables:
```bash
cp env.template .env
# Edit .env and add your Baidu AI Studio API credentials:
# BAIDU_API_KEY=your_api_key
# BAIDU_SECRET_KEY=your_secret_key
```

6. Run the backend:
```bash
python backend/app.py
```
The API will be available at `http://localhost:8000`

7. Run the frontend (in a new terminal):
```bash
cd frontend
npm run dev
```
The frontend will be available at `http://localhost:3000`

### Quick Start (Warm-up Task)

1. Open `warmup/index.html` in a web browser
2. Update the `API_URL` in the file to point to your backend
3. Upload a PDF or image claim document
4. View the processed claim information

## Project Structure

```
ERNIE/
├── README.md
├── requirements.txt
├── backend/
│   ├── app.py              # FastAPI application
│   ├── ocr_processor.py    # PaddleOCR integration
│   ├── ernie_service.py    # ERNIE API integration
│   ├── claim_processor.py  # Claim processing logic
│   └── models/             # Data models
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Next.js pages
│   │   └── styles/         # CSS styles
│   └── package.json
├── warmup/                 # Warm-up task (GitHub Pages)
│   └── index.html
├── docs/                   # Documentation
│   ├── API.md
│   └── DEPLOYMENT.md
└── tests/                  # Unit tests
```

## API Documentation

See [docs/API.md](docs/API.md) for detailed API documentation.

## Testing

Run backend tests:
```bash
python -m pytest tests/
```

Or use unittest:
```bash
python -m unittest discover tests
```

## Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions.

## Features Implemented

✅ **Warm-up Task**: PDF to Web Page generator with PaddleOCR + ERNIE  
✅ **Document Processing**: Multi-format support (PDF, JPG, PNG)  
✅ **OCR Integration**: PaddleOCR-VL for text and layout extraction  
✅ **AI Processing**: ERNIE for claim extraction, validation, and categorization  
✅ **Duplicate Detection**: Automatic duplicate claim identification  
✅ **Anomaly Detection**: Unusual claim pattern detection  
✅ **Analytics Dashboard**: Visual insights and processing trends  
✅ **Natural Language Queries**: Ask questions about claims  
✅ **Multi-language Support**: Process claims in multiple languages  
✅ **Claim Workflows**: Approval/rejection workflow management  
✅ **Modern UI**: Clean, responsive web interface  

## License

MIT
